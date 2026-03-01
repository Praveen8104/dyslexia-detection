"""Train CNN-LSTM speech classification model on TORGO dysarthria dataset."""

import os
import sys
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight

# Add parent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import tensorflow as tf
from tensorflow import keras
import librosa

from app.ml.speech.feature_extractor import extract_mfcc_features
from app.ml.speech.speech_model import build_speech_model

# Configuration
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "speech_real")
CSV_PATH = os.path.join(DATA_DIR, "data_with_path.csv")
MODEL_SAVE_PATH = os.path.join(os.path.dirname(__file__), "..", "saved_models", "speech_model.keras")
BATCH_SIZE = 32
EPOCHS = 25
MAX_SAMPLES = None  # Set to a number to limit samples for faster testing


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


def train():
    print("=" * 60)
    print("Speech Model Training (TORGO Dysarthria Dataset)")
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

    # Compute class weights to handle imbalance
    class_weights = compute_class_weight("balanced", classes=np.array([0, 1]), y=y_train)
    class_weight_dict = {0: class_weights[0], 1: class_weights[1]}
    print(f"Class weights: {class_weight_dict}\n")

    # Convert labels to categorical
    y_train_cat = keras.utils.to_categorical(y_train, 2)
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
        keras.callbacks.EarlyStopping(patience=7, restore_best_weights=True, monitor="val_accuracy"),
        keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=3, monitor="val_loss"),
    ]

    print("\nTraining...")
    model.fit(
        X_train, y_train_cat,
        validation_data=(X_val, y_val_cat),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        class_weight=class_weight_dict,
        callbacks=callbacks,
        verbose=1,
    )

    # Evaluate
    test_loss, test_acc = model.evaluate(X_test, y_test_cat, verbose=0)
    print(f"\nTest Accuracy: {test_acc:.4f}")
    print(f"Test Loss: {test_loss:.4f}")

    # Per-class accuracy
    y_pred = model.predict(X_test, verbose=0)
    y_pred_classes = np.argmax(y_pred, axis=1)
    for cls, name in [(0, "Normal"), (1, "Dysarthria")]:
        mask = y_test == cls
        acc = np.mean(y_pred_classes[mask] == cls)
        print(f"  {name}: {acc:.4f} ({np.sum(mask)} samples)")

    # Save model
    os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)
    model.save(MODEL_SAVE_PATH)
    print(f"\nModel saved to {MODEL_SAVE_PATH}")

    return model, test_acc


if __name__ == "__main__":
    train()
