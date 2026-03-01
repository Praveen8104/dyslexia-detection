import os
import numpy as np
import logging

logger = logging.getLogger(__name__)

CLASS_NAMES = ["Normal", "At-Risk"]
MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "saved_models", "speech_model.keras"
)

# Age-based WPM thresholds (below these = concern)
AGE_WPM_THRESHOLDS = {
    6: 60, 7: 80, 8: 100, 9: 110, 10: 120, 11: 130, 12: 140,
}


class SpeechPredictor:
    def __init__(self):
        self.model = None
        self._load_model()

    def _load_model(self):
        if os.path.exists(MODEL_PATH):
            from tensorflow import keras
            self.model = keras.models.load_model(MODEL_PATH)
            logger.info("Speech model loaded successfully")
        else:
            logger.warning(
                f"Model not found at {MODEL_PATH}. "
                "Using rule-based predictions only."
            )

    def predict(self, audio_path: str, expected_text: str = "",
                child_age: int = None) -> dict:
        from app.ml.speech.audio_processor import (
            load_audio, compute_silence_ratio,
            count_hesitations, estimate_reading_speed,
        )
        from app.ml.speech.feature_extractor import extract_mfcc_features

        signal, sr = load_audio(audio_path)

        # Validate audio duration (at least 1 second)
        duration_sec = len(signal) / sr
        if duration_sec < 1.0:
            raise ValueError(
                f"Audio too short ({duration_sec:.1f}s). "
                "Please record for at least 2 seconds."
            )

        # Extract heuristic features
        word_count = len(expected_text.split()) if expected_text else 10
        reading_speed = estimate_reading_speed(signal, sr, word_count)
        hesitation_count = count_hesitations(signal, sr)
        silence_ratio = compute_silence_ratio(signal, sr)

        # ML-based prediction
        if self.model is not None:
            features = extract_mfcc_features(signal, sr)
            features_batch = np.expand_dims(features, axis=0)
            probs = self.model.predict(features_batch, verbose=0)[0]
        else:
            # Rule-based fallback using age-appropriate thresholds
            probs = self._rule_based_score(
                reading_speed, hesitation_count, silence_ratio, child_age
            )

        pred_idx = int(np.argmax(probs))
        confidence = float(probs[pred_idx])
        prediction = CLASS_NAMES[pred_idx]

        # Compute risk score (0-100)
        risk_score = float(probs[1]) * 100  # probability of At-Risk

        return {
            "prediction": prediction,
            "confidence": round(confidence, 4),
            "risk_score": round(risk_score, 2),
            "reading_speed_wpm": round(reading_speed, 1),
            "hesitation_count": hesitation_count,
            "silence_ratio": round(silence_ratio, 4),
        }

    def _rule_based_score(self, wpm: float, hesitations: int,
                          silence_ratio: float,
                          child_age: int = None) -> np.ndarray:
        """Compute risk probability using rule-based heuristics."""
        risk = 0.0

        # Use age-appropriate WPM threshold if age is provided
        wpm_threshold = AGE_WPM_THRESHOLDS.get(child_age, 100)
        wpm_warning = wpm_threshold * 0.8  # 80% of threshold = mild concern

        if wpm < wpm_warning:
            risk += 0.3
        elif wpm < wpm_threshold:
            risk += 0.15

        # Many hesitations
        if hesitations >= 5:
            risk += 0.3
        elif hesitations >= 3:
            risk += 0.15

        # High silence ratio
        if silence_ratio > 0.5:
            risk += 0.2
        elif silence_ratio > 0.3:
            risk += 0.1

        risk = min(risk, 0.95)
        return np.array([1.0 - risk, risk])
