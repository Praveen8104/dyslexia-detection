from tensorflow import keras
from tensorflow.keras import layers, regularizers


def build_speech_model(input_shape=(200, 39), num_classes: int = 2) -> keras.Model:
    """Build 1D-CNN + BiLSTM hybrid model for speech analysis.

    Architecture:
    - Input: (200, 39) - 200 time frames, 39 MFCC features
    - Conv1D(64) -> BatchNorm -> ReLU -> Dropout -> MaxPool
    - Conv1D(128) -> BatchNorm -> ReLU -> Dropout -> MaxPool
    - Conv1D(128) -> BatchNorm -> ReLU -> Dropout -> MaxPool
    - Bidirectional LSTM(64)
    - Dense(64, relu, L2) -> Dropout(0.4)
    - Dense(32, relu, L2) -> Dropout(0.3)
    - Dense(num_classes, softmax)
    """
    inputs = keras.Input(shape=input_shape)

    # First Conv block
    x = layers.Conv1D(64, kernel_size=3, padding="same",
                      kernel_regularizer=regularizers.L2(1e-4))(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.ReLU()(x)
    x = layers.SpatialDropout1D(0.1)(x)
    x = layers.MaxPooling1D(pool_size=2)(x)

    # Second Conv block
    x = layers.Conv1D(128, kernel_size=3, padding="same",
                      kernel_regularizer=regularizers.L2(1e-4))(x)
    x = layers.BatchNormalization()(x)
    x = layers.ReLU()(x)
    x = layers.SpatialDropout1D(0.1)(x)
    x = layers.MaxPooling1D(pool_size=2)(x)

    # Third Conv block (new)
    x = layers.Conv1D(128, kernel_size=3, padding="same",
                      kernel_regularizer=regularizers.L2(1e-4))(x)
    x = layers.BatchNormalization()(x)
    x = layers.ReLU()(x)
    x = layers.SpatialDropout1D(0.1)(x)
    x = layers.MaxPooling1D(pool_size=2)(x)

    # Bidirectional LSTM (captures forward + backward temporal patterns)
    x = layers.Bidirectional(layers.LSTM(64))(x)

    # Deeper classification head with regularization
    x = layers.Dense(64, activation="relu",
                     kernel_regularizer=regularizers.L2(1e-4))(x)
    x = layers.Dropout(0.4)(x)
    x = layers.Dense(32, activation="relu",
                     kernel_regularizer=regularizers.L2(1e-4))(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(num_classes, activation="softmax")(x)

    model = keras.Model(inputs, outputs, name="speech_classifier")
    return model
