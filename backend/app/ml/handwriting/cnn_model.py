import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers


def build_handwriting_model(num_classes: int = 3) -> keras.Model:
    """Build MobileNetV2-based handwriting classification model.

    Architecture:
    - Input: 128x128x1 grayscale
    - Conv2D to expand to 3 channels (for MobileNetV2 compatibility)
    - MobileNetV2 (pretrained on ImageNet, frozen base)
    - GlobalAveragePooling2D
    - Dense(128, relu) + Dropout(0.3)
    - Dense(num_classes, softmax)
    """
    inputs = keras.Input(shape=(128, 128, 1))

    # Expand grayscale to 3 channels
    x = layers.Conv2D(3, (1, 1), padding="same", name="channel_expand")(inputs)

    # MobileNetV2 backbone
    base_model = keras.applications.MobileNetV2(
        input_shape=(128, 128, 3),
        include_top=False,
        weights="imagenet",
    )
    base_model.trainable = False

    x = base_model(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dense(128, activation="relu")(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(num_classes, activation="softmax")(x)

    model = keras.Model(inputs, outputs, name="handwriting_classifier")
    return model


def fine_tune_model(model: keras.Model, unfreeze_layers: int = 30):
    """Unfreeze the last N layers of MobileNetV2 for fine-tuning."""
    base = model.layers[1] if hasattr(model.layers[1], 'layers') else None
    if base is None:
        # Find MobileNetV2 in the model
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
