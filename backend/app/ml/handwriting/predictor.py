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
        self.model_loaded = False
        self._load_model()

    def _load_model(self):
        if os.path.exists(MODEL_PATH):
            from tensorflow import keras
            self.model = keras.models.load_model(MODEL_PATH)
            self.model_loaded = True
            logger.info("Handwriting model loaded successfully")
        else:
            logger.warning(
                f"Model not found at {MODEL_PATH}. "
                "Using image-feature-based analysis as fallback."
            )

    def predict(self, image_path: str) -> dict:
        from app.ml.handwriting.preprocessor import preprocess_image

        img = preprocess_image(image_path)
        img_batch = np.expand_dims(img, axis=0)

        if self.model is not None:
            predictions = self.model.predict(img_batch, verbose=0)
            probs = predictions[0]
        else:
            probs = self._image_heuristic_score(img)

        pred_idx = int(np.argmax(probs))
        confidence = float(probs[pred_idx])
        prediction = CLASS_NAMES[pred_idx]

        # Compute risk score (0-100)
        risk_weights = {"Normal": 0.1, "Reversal": 0.9, "Corrected": 0.5}
        risk_score = float(probs[0] * risk_weights["Normal"]
                          + probs[1] * risk_weights["Reversal"]
                          + probs[2] * risk_weights["Corrected"]) * 100

        markers = []
        if probs[1] > 0.3:
            markers.append("Letter reversal detected")
        if probs[2] > 0.3:
            markers.append("Self-correction patterns observed")
        if not self.model_loaded:
            markers.append("Note: Analysis used heuristic mode (ML model not trained yet)")

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

    def _image_heuristic_score(self, img: np.ndarray) -> np.ndarray:
        """Analyze image features when ML model is unavailable.

        Uses basic image statistics as proxies:
        - Ink density (ratio of dark pixels)
        - Stroke irregularity (variance of pixel values)
        - Spatial symmetry (left-right comparison for reversal detection)
        """
        flat = img.squeeze()

        # Ink density: how much of the image has writing
        ink_density = float(np.mean(flat < 0.5))

        # Stroke irregularity: high variance = uneven strokes
        stroke_var = float(np.var(flat))

        # Left-right asymmetry: potential reversal indicator
        mid = flat.shape[1] // 2
        left_half = flat[:, :mid]
        right_half = flat[:, mid:]
        right_flipped = np.fliplr(right_half)
        min_w = min(left_half.shape[1], right_flipped.shape[1])
        asymmetry = float(np.mean(np.abs(left_half[:, :min_w] - right_flipped[:, :min_w])))

        # Score based on heuristics
        reversal_prob = min(0.6, asymmetry * 1.5)
        corrected_prob = min(0.4, stroke_var * 2.0)
        normal_prob = max(0.1, 1.0 - reversal_prob - corrected_prob)

        # Normalize to sum to 1
        total = normal_prob + reversal_prob + corrected_prob
        probs = np.array([
            normal_prob / total,
            reversal_prob / total,
            corrected_prob / total,
        ])

        return probs
