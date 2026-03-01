from tensorflow import keras
from tensorflow.keras import layers


def build_speech_model(input_shape=(200, 39), num_classes: int = 2) -> keras.Model:
    """Build 1D-CNN + LSTM hybrid model for speech analysis.

    Architecture:
    - Input: (200, 39) - 200 time frames, 39 MFCC features
    - Conv1D(64) -> BatchNorm -> ReLU -> MaxPool
    - Conv1D(128) -> BatchNorm -> ReLU -> MaxPool
    - LSTM(64)
    - Dense(32, relu) -> Dropout(0.3)
    - Dense(num_classes, softmax)
    """
    inputs = keras.Input(shape=input_shape)

    # First Conv block
    x = layers.Conv1D(64, kernel_size=3, padding="same")(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.ReLU()(x)
    x = layers.MaxPooling1D(pool_size=2)(x)

    # Second Conv block
    x = layers.Conv1D(128, kernel_size=3, padding="same")(x)
    x = layers.BatchNormalization()(x)
    x = layers.ReLU()(x)
    x = layers.MaxPooling1D(pool_size=2)(x)

    # LSTM
    x = layers.LSTM(64)(x)

    # Classification head
    x = layers.Dense(32, activation="relu")(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(num_classes, activation="softmax")(x)

    model = keras.Model(inputs, outputs, name="speech_classifier")
    return model
