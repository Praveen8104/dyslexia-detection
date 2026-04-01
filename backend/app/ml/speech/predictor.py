import os
import numpy as np
import logging

logger = logging.getLogger(__name__)

CLASS_NAMES = ["Normal", "At-Risk"]
MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "saved_models", "speech_model.keras"
)

# Age-based WPM thresholds (below these = concern)
# Based on Hasbrouck & Tindal (2017) oral reading fluency norms
AGE_WPM_THRESHOLDS = {
    6: 60, 7: 80, 8: 100, 9: 110, 10: 120, 11: 130, 12: 140,
}

# Weights for combining ML and rule-based scores
ML_WEIGHT = 0.35
HEURISTIC_WEIGHT = 0.65


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
        from app.ml.speech.transcriber import transcribe_audio, analyze_reading_errors

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

        # Transcribe audio and compute reading accuracy
        transcription = transcribe_audio(audio_path)
        reading_errors = analyze_reading_errors(expected_text, transcription)

        # Rule-based risk score (always computed)
        heuristic_probs = self._rule_based_score(
            reading_speed, hesitation_count, silence_ratio,
            child_age, reading_errors
        )

        # Combine ML + heuristics if model is available
        if self.model is not None:
            features = extract_mfcc_features(signal, sr)
            features_batch = np.expand_dims(features, axis=0)
            ml_probs = self.model.predict(features_batch, verbose=0)[0]

            # Weighted blend: heuristics are more reliable for dyslexia
            # since the ML model was trained on dysarthria (different domain)
            probs = (ML_WEIGHT * ml_probs) + (HEURISTIC_WEIGHT * heuristic_probs)
        else:
            probs = heuristic_probs

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
            # New transcription fields
            "transcription": reading_errors["transcription"],
            "reading_accuracy": reading_errors["reading_accuracy"],
            "wer": reading_errors["wer"],
            "substitutions": reading_errors["substitutions"],
            "deletions": reading_errors["deletions"],
            "insertions": reading_errors["insertions"],
            "error_details": reading_errors["error_details"],
        }

    def _rule_based_score(self, wpm: float, hesitations: int,
                          silence_ratio: float,
                          child_age: int = None,
                          reading_errors: dict = None) -> np.ndarray:
        """Compute risk probability using rule-based heuristics."""
        risk = 0.0

        # Use age-appropriate WPM threshold if age is provided
        wpm_threshold = AGE_WPM_THRESHOLDS.get(child_age, 100)
        wpm_warning = wpm_threshold * 0.8  # 80% of threshold = mild concern

        # Reading speed assessment (biggest indicator)
        if wpm < wpm_warning * 0.5:
            risk += 0.35  # Very slow
        elif wpm < wpm_warning:
            risk += 0.25
        elif wpm < wpm_threshold:
            risk += 0.12

        # Hesitation count
        if hesitations >= 6:
            risk += 0.25
        elif hesitations >= 4:
            risk += 0.18
        elif hesitations >= 2:
            risk += 0.10

        # Silence ratio
        if silence_ratio > 0.6:
            risk += 0.20
        elif silence_ratio > 0.4:
            risk += 0.12
        elif silence_ratio > 0.25:
            risk += 0.05

        # Reading accuracy (from transcription) - key dyslexia indicator
        # Word substitutions, omissions, and insertions directly reflect
        # phonological processing difficulties characteristic of dyslexia
        if reading_errors and reading_errors.get("wer") is not None:
            wer = reading_errors["wer"]
            if wer > 0.5:
                risk += 0.30  # More than half the words wrong
            elif wer > 0.3:
                risk += 0.20
            elif wer > 0.15:
                risk += 0.10
            elif wer > 0.0:
                risk += 0.05

            # Extra weight for substitutions (classic dyslexia pattern:
            # confusing similar-looking/sounding words)
            subs = reading_errors.get("substitutions", 0)
            if subs >= 3:
                risk += 0.10
            elif subs >= 1:
                risk += 0.05

        risk = min(risk, 0.95)
        return np.array([1.0 - risk, risk])
