"""Train CNN-BiLSTM speech classification model on TORGO dysarthria dataset."""

import os
import sys
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score

# Add parent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import tensorflow as tf
from tensorflow import keras

from app.ml.speech.feature_extractor import extract_mfcc_features
from app.ml.speech.speech_model import build_speech_model

# Configuration
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "speech_real")
CSV_PATH = os.path.join(DATA_DIR, "data_with_path.csv")
MODEL_SAVE_PATH = os.path.join(os.path.dirname(__file__), "..", "saved_models", "speech_model.keras")
BATCH_SIZE = 32
EPOCHS = 40
MAX_SAMPLES = None


def augment_audio_features(features: np.ndarray) -> np.ndarray:
    """Apply augmentation to MFCC features."""
    augmented = features.copy()

    # Time masking: zero out random time frames
    if np.random.random() < 0.5:
        t = np.random.randint(0, 20)
        t0 = np.random.randint(0, max(1, features.shape[0] - t))
        augmented[t0:t0 + t, :] = 0

    # Feature masking: zero out random feature channels
    if np.random.random() < 0.5:
        f = np.random.randint(0, 5)
        f0 = np.random.randint(0, max(1, features.shape[1] - f))
        augmented[:, f0:f0 + f] = 0

    # Add small Gaussian noise
    if np.random.random() < 0.5:
        noise = np.random.normal(0, 0.05, augmented.shape)
        augmented = augmented + noise

    # Time stretching (simple: repeat or skip frames)
    if np.random.random() < 0.3:
        rate = np.random.uniform(0.9, 1.1)
        indices = np.round(np.arange(0, features.shape[0], rate)).astype(int)
        indices = indices[indices < features.shape[0]]
        stretched = augmented[indices]
        # Re-pad/truncate to original length
        if stretched.shape[0] < features.shape[0]:
            pad = features.shape[0] - stretched.shape[0]
            stretched = np.pad(stretched, ((0, pad), (0, 0)), mode="constant")
        else:
            stretched = stretched[:features.shape[0]]
        augmented = stretched

    return augmented.astype(np.float32)


def load_dataset():
    """Load audio files and extract MFCC features."""
    df = pd.read_csv(CSV_PATH)
    print(f"Total entries in CSV: {len(df)}")
    print(f"Class distribution:\n{df['Is_dysarthria'].value_counts()}\n")

    if MAX_SAMPLES:
        df = df.sample(n=min(MAX_SAMPLES, len(df)), random_state=42)
        print(f"Sampled {len(df)} entries\n")

    features = []
    labels = []
    errors = 0

    for i, row in df.iterrows():
        # Convert kaggle path to local path
        kaggle_path = row["Wav_path"]
        local_path = os.path.join(DATA_DIR, *kaggle_path.split("/")[4:])

        if not os.path.exists(local_path):
            errors += 1
            continue

        try:
            import librosa
            signal, sr = librosa.load(local_path, sr=16000, duration=10.0)

            # Skip very short audio (< 0.5s)
            if len(signal) < sr * 0.5:
                continue

            mfcc = extract_mfcc_features(signal, sr)
            features.append(mfcc)
            labels.append(1 if row["Is_dysarthria"] == "Yes" else 0)

            if (len(features)) % 500 == 0:
                print(f"  Processed {len(features)} files...")
        except Exception as e:
            errors += 1
            if errors <= 5:
                print(f"  Error processing {local_path}: {e}")

    X = np.array(features)
    y = np.array(labels)
    print(f"\nLoaded {len(X)} samples (shape: {X.shape}), {errors} errors")
    print(f"Class 0 (Normal): {np.sum(y == 0)}, Class 1 (Dysarthria): {np.sum(y == 1)}")
    return X, y


def create_augmented_dataset(X, y, augment_factor=2):
    """Create augmented training dataset."""
    X_aug = list(X)
    y_aug = list(y)
    for _ in range(augment_factor):
        for i in range(len(X)):
            X_aug.append(augment_audio_features(X[i]))
            y_aug.append(y[i])
    return np.array(X_aug), np.array(y_aug)


def train():
    print("=" * 60)
    print("Speech Model Training (CNN-BiLSTM + SpecAugment)")
    print("=" * 60)
    print(f"TensorFlow version: {tf.__version__}")
    print()

    # Load data
    X, y = load_dataset()

    # Split: 70% train, 15% val, 15% test
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp
    )
    print(f"\nTrain: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")

    # Augment training data (2x more samples)
    print("Augmenting training data...")
    X_train_aug, y_train_aug = create_augmented_dataset(X_train, y_train, augment_factor=2)
    print(f"Augmented train: {len(X_train_aug)} samples")

    # Compute class weights
    class_weights = compute_class_weight("balanced", classes=np.array([0, 1]), y=y_train_aug)
    class_weight_dict = {0: class_weights[0], 1: class_weights[1]}
    print(f"Class weights: {class_weight_dict}\n")

    # Convert labels to categorical
    y_train_cat = keras.utils.to_categorical(y_train_aug, 2)
    y_val_cat = keras.utils.to_categorical(y_val, 2)
    y_test_cat = keras.utils.to_categorical(y_test, 2)

    # Build model
    model = build_speech_model(input_shape=(200, 39), num_classes=2)
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

    # Create tf.data pipeline
    train_ds = tf.data.Dataset.from_tensor_slices((X_train_aug, y_train_cat))
    train_ds = train_ds.shuffle(buffer_size=len(X_train_aug))
    train_ds = train_ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)

    val_ds = tf.data.Dataset.from_tensor_slices((X_val, y_val_cat))
    val_ds = val_ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)

    print("\nTraining...")
    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=EPOCHS,
        class_weight=class_weight_dict,
        callbacks=callbacks,
        verbose=1,
    )

    # Evaluate
    test_loss, test_acc = model.evaluate(X_test, y_test_cat, verbose=0)
    print(f"\nTest Accuracy: {test_acc:.4f}")
    print(f"Test Loss: {test_loss:.4f}")

    # Detailed metrics
    y_pred = model.predict(X_test, verbose=0)
    y_pred_classes = np.argmax(y_pred, axis=1)

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred_classes, target_names=["Normal", "Dysarthria"]))

    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred_classes))

    # AUC-ROC
    auc = roc_auc_score(y_test, y_pred[:, 1])
    print(f"\nAUC-ROC: {auc:.4f}")

    # Save model
    os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)
    model.save(MODEL_SAVE_PATH)
    print(f"\nModel saved to {MODEL_SAVE_PATH}")

    return model, test_acc


if __name__ == "__main__":
    train()
