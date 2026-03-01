import os
import numpy as np
import logging

logger = logging.getLogger(__name__)

CLASS_NAMES = ["Normal", "Reversal", "Corrected"]
MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "saved_models", "handwriting_model.keras"
)


class HandwritingPredictor:
    def __init__(self):
        self.model = None
        self._load_model()

    def _load_model(self):
        if os.path.exists(MODEL_PATH):
            from tensorflow import keras
            self.model = keras.models.load_model(MODEL_PATH)
            logger.info("Handwriting model loaded successfully")
        else:
            logger.warning(
                f"Model not found at {MODEL_PATH}. "
                "Using dummy predictions. Train the model first."
            )

    def predict(self, image_path: str) -> dict:
        from app.ml.handwriting.preprocessor import preprocess_image

        img = preprocess_image(image_path)
        img_batch = np.expand_dims(img, axis=0)

        if self.model is not None:
            predictions = self.model.predict(img_batch, verbose=0)
            probs = predictions[0]
        else:
            # Dummy predictions for development/testing
            probs = np.random.dirichlet(np.ones(3))

        pred_idx = int(np.argmax(probs))
        confidence = float(probs[pred_idx])
        prediction = CLASS_NAMES[pred_idx]

        # Compute risk score (0-100)
        # Normal = low risk, Reversal = high risk, Corrected = medium risk
        risk_weights = {"Normal": 0.1, "Reversal": 0.9, "Corrected": 0.5}
        risk_score = float(probs[0] * risk_weights["Normal"]
                          + probs[1] * risk_weights["Reversal"]
                          + probs[2] * risk_weights["Corrected"]) * 100

        markers = []
        if probs[1] > 0.3:
            markers.append("Letter reversal detected")
        if probs[2] > 0.3:
            markers.append("Self-correction patterns observed")

        return {
            "prediction": prediction,
            "confidence": round(confidence, 4),
            "risk_score": round(risk_score, 2),
            "probabilities": {
                name: round(float(p), 4)
                for name, p in zip(CLASS_NAMES, probs)
            },
            "markers": markers,
        }
