"""Train MobileNetV2-based handwriting classification model on real Kaggle dataset."""

import os
import sys
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight

# Add parent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import tensorflow as tf
from tensorflow import keras

from app.ml.handwriting.preprocessor import preprocess_image
from app.ml.handwriting.cnn_model import build_handwriting_model, fine_tune_model

# Configuration
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "handwriting_real", "Gambo", "Test")
MODEL_SAVE_PATH = os.path.join(os.path.dirname(__file__), "..", "saved_models", "handwriting_model.keras")
CLASS_NAMES = ["Normal", "Reversal", "Corrected"]
BATCH_SIZE = 64
EPOCHS_PHASE1 = 15
EPOCHS_PHASE2 = 15
MAX_PER_CLASS = 8000  # Limit samples per class to keep training manageable


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
    print("Handwriting Model Training (Kaggle Real Dataset)")
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

    # Phase 1: Train classification head (base frozen)
    print("Phase 1: Training classification head...")
    model = build_handwriting_model(num_classes=len(CLASS_NAMES))
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-3),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )

    callbacks = [
        keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True, monitor="val_accuracy"),
        keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=3),
    ]

    model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=EPOCHS_PHASE1,
        batch_size=BATCH_SIZE,
        class_weight=class_weight_dict,
        callbacks=callbacks,
        verbose=1,
    )

    # Phase 2: Fine-tune last 30 layers
    print("\nPhase 2: Fine-tuning MobileNetV2 layers...")
    model = fine_tune_model(model, unfreeze_layers=30)

    model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=EPOCHS_PHASE2,
        batch_size=BATCH_SIZE,
        class_weight=class_weight_dict,
        callbacks=callbacks,
        verbose=1,
    )

    # Evaluate
    test_loss, test_acc = model.evaluate(X_test, y_test, verbose=0)
    print(f"\nTest Accuracy: {test_acc:.4f}")
    print(f"Test Loss: {test_loss:.4f}")

    # Per-class accuracy
    y_pred = model.predict(X_test, verbose=0)
    y_pred_classes = np.argmax(y_pred, axis=1)
    y_true_classes = np.argmax(y_test, axis=1)
    for cls, name in enumerate(CLASS_NAMES):
        mask = y_true_classes == cls
        acc = np.mean(y_pred_classes[mask] == cls) if np.sum(mask) > 0 else 0
        print(f"  {name}: {acc:.4f} ({np.sum(mask)} samples)")

    # Save model
    os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)
    model.save(MODEL_SAVE_PATH)
    print(f"\nModel saved to {MODEL_SAVE_PATH}")

    return model, test_acc


if __name__ == "__main__":
    train()
