"""Train EfficientNetB0-based handwriting classification model on real Kaggle dataset."""

import os
import sys
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import classification_report, confusion_matrix

# Add parent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

from app.ml.handwriting.preprocessor import preprocess_image
from app.ml.handwriting.cnn_model import build_handwriting_model, fine_tune_model

# Configuration
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "handwriting_real", "Gambo", "Test")
MODEL_SAVE_PATH = os.path.join(os.path.dirname(__file__), "..", "saved_models", "handwriting_model.keras")
CLASS_NAMES = ["Normal", "Reversal", "Corrected"]
BATCH_SIZE = 32
EPOCHS_PHASE1 = 30
EPOCHS_PHASE2 = 30
MAX_PER_CLASS = 10000


def build_augmentation_layer():
    """Build data augmentation pipeline for training."""
    return keras.Sequential([
        layers.RandomRotation(0.05),
        layers.RandomTranslation(0.1, 0.1),
        layers.RandomZoom((-0.1, 0.1)),
        layers.RandomContrast(0.2),
        layers.GaussianNoise(0.02),
    ], name="augmentation")


def load_dataset():
    """Load and preprocess all images from the real Kaggle dataset."""
    images = []
    labels = []

    for class_idx, class_name in enumerate(CLASS_NAMES):
        class_dir = os.path.join(DATA_DIR, class_name)
        if not os.path.exists(class_dir):
            print(f"WARNING: {class_dir} not found!")
            continue

        files = [f for f in os.listdir(class_dir) if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp"))]
        print(f"{class_name}: {len(files)} images found", end="")

        # Limit samples per class
        if MAX_PER_CLASS and len(files) > MAX_PER_CLASS:
            np.random.seed(42)
            files = list(np.random.choice(files, MAX_PER_CLASS, replace=False))
            print(f" -> sampled {len(files)}", end="")
        print()

        loaded = 0
        for fname in files:
            fpath = os.path.join(class_dir, fname)
            try:
                img = preprocess_image(fpath)
                images.append(img)
                labels.append(class_idx)
                loaded += 1
            except Exception as e:
                if loaded < 3:
                    print(f"  Error: {fpath}: {e}")

        print(f"  Loaded: {loaded}")

    X = np.array(images)
    y = np.array(labels)
    print(f"\nTotal: {len(X)} images, shape: {X.shape}")
    return X, y


def train():
    print("=" * 60)
    print("Handwriting Model Training (EfficientNetB0 + Augmentation)")
    print("=" * 60)
    print(f"TensorFlow version: {tf.__version__}")
    print(f"Data directory: {DATA_DIR}")
    print()

    # Load data
    X, y = load_dataset()

    # Compute class weights
    class_weights = compute_class_weight("balanced", classes=np.array([0, 1, 2]), y=y)
    class_weight_dict = {i: w for i, w in enumerate(class_weights)}
    print(f"Class weights: {class_weight_dict}\n")

    # Convert to categorical
    y_cat = keras.utils.to_categorical(y, num_classes=len(CLASS_NAMES))

    # Split: 70% train, 15% val, 15% test
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y_cat, test_size=0.3, random_state=42, stratify=y
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.5, random_state=42, stratify=np.argmax(y_temp, axis=1)
    )
    print(f"Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")
    print()

    # Build augmentation layer
    augmentation = build_augmentation_layer()

    # Create tf.data pipelines with augmentation for training
    train_ds = tf.data.Dataset.from_tensor_slices((X_train, y_train))
    train_ds = train_ds.shuffle(buffer_size=len(X_train))
    train_ds = train_ds.batch(BATCH_SIZE)
    train_ds = train_ds.map(
        lambda x, y: (augmentation(x, training=True), y),
        num_parallel_calls=tf.data.AUTOTUNE
    )
    train_ds = train_ds.prefetch(tf.data.AUTOTUNE)

    val_ds = tf.data.Dataset.from_tensor_slices((X_val, y_val))
    val_ds = val_ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)

    # Phase 1: Train classification head (base frozen)
    print("Phase 1: Training classification head (base frozen)...")
    model = build_handwriting_model(num_classes=len(CLASS_NAMES))
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-3),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    model.summary()

    callbacks = [
        keras.callbacks.EarlyStopping(
            patience=10, restore_best_weights=True, monitor="val_accuracy"
        ),
        keras.callbacks.ReduceLROnPlateau(
            factor=0.5, patience=4, monitor="val_loss", min_lr=1e-7
        ),
    ]

    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=EPOCHS_PHASE1,
        class_weight=class_weight_dict,
        callbacks=callbacks,
        verbose=1,
    )

    # Phase 2: Fine-tune last 40 layers
    print("\nPhase 2: Fine-tuning EfficientNetB0 layers...")
    model = fine_tune_model(model, unfreeze_layers=40)

    # Use cosine decay for fine-tuning
    cosine_schedule = keras.optimizers.schedules.CosineDecay(
        initial_learning_rate=1e-5,
        decay_steps=EPOCHS_PHASE2 * (len(X_train) // BATCH_SIZE),
        alpha=1e-7,
    )
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=cosine_schedule),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )

    callbacks_ft = [
        keras.callbacks.EarlyStopping(
            patience=12, restore_best_weights=True, monitor="val_accuracy"
        ),
    ]

    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=EPOCHS_PHASE2,
        class_weight=class_weight_dict,
        callbacks=callbacks_ft,
        verbose=1,
    )

    # Evaluate
    test_loss, test_acc = model.evaluate(X_test, y_test, verbose=0)
    print(f"\nTest Accuracy: {test_acc:.4f}")
    print(f"Test Loss: {test_loss:.4f}")

    # Detailed metrics
    y_pred = model.predict(X_test, verbose=0)
    y_pred_classes = np.argmax(y_pred, axis=1)
    y_true_classes = np.argmax(y_test, axis=1)

    print("\nClassification Report:")
    print(classification_report(y_true_classes, y_pred_classes, target_names=CLASS_NAMES))

    print("Confusion Matrix:")
    cm = confusion_matrix(y_true_classes, y_pred_classes)
    print(cm)

    # Save model
    os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)
    model.save(MODEL_SAVE_PATH)
    print(f"\nModel saved to {MODEL_SAVE_PATH}")

    return model, test_acc


if __name__ == "__main__":
    train()
