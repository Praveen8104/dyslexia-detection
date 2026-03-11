import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, regularizers


def build_handwriting_model(num_classes: int = 3) -> keras.Model:
    """Build EfficientNetB0-based handwriting classification model.

    Architecture:
    - Input: 224x224x1 grayscale
    - Conv2D to expand to 3 channels (for EfficientNet compatibility)
    - EfficientNetB0 (pretrained on ImageNet, frozen base)
    - GlobalAveragePooling2D
    - Dense(256, relu, L2) + BatchNorm + Dropout(0.4)
    - Dense(128, relu, L2) + Dropout(0.3)
    - Dense(num_classes, softmax)
    """
    inputs = keras.Input(shape=(224, 224, 1))

    # Expand grayscale to 3 channels
    x = layers.Conv2D(3, (1, 1), padding="same", name="channel_expand")(inputs)

    # EfficientNetB0 backbone (better accuracy than MobileNetV2 at similar cost)
    base_model = keras.applications.EfficientNetB0(
        input_shape=(224, 224, 3),
        include_top=False,
        weights="imagenet",
    )
    base_model.trainable = False

    x = base_model(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)

    # Deeper classification head with regularization
    x = layers.Dense(256, kernel_regularizer=regularizers.L2(1e-4))(x)
    x = layers.BatchNormalization()(x)
    x = layers.ReLU()(x)
    x = layers.Dropout(0.4)(x)

    x = layers.Dense(128, activation="relu",
                     kernel_regularizer=regularizers.L2(1e-4))(x)
    x = layers.Dropout(0.3)(x)

    outputs = layers.Dense(num_classes, activation="softmax")(x)

    model = keras.Model(inputs, outputs, name="handwriting_classifier")
    return model


def fine_tune_model(model: keras.Model, unfreeze_layers: int = 40):
    """Unfreeze the last N layers of the base model for fine-tuning."""
    base = None
    for layer in model.layers:
        if hasattr(layer, 'layers') and len(layer.layers) > 10:
            base = layer
            break

    if base:
        base.trainable = True
        for layer in base.layers[:-unfreeze_layers]:
            layer.trainable = False

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-5),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model
