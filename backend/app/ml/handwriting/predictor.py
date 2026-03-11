import os
import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

CLASS_NAMES = ["Normal", "Reversal", "Corrected"]
MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "saved_models", "handwriting_model.keras"
)

# Weights for combining ML and heuristic scores
ML_WEIGHT = 0.30
HEURISTIC_WEIGHT = 0.70


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
        from app.ml.handwriting.preprocessor import preprocess_image, IMG_SIZE

        img = preprocess_image(image_path)

        # Always compute heuristic score from the original image
        heuristic_probs, analysis = self._analyze_handwriting(image_path)

        if self.model is not None:
            # Match preprocessed image to model's expected input shape
            model_h = self.model.input_shape[1]
            if model_h != IMG_SIZE:
                img_resized = cv2.resize(img[:, :, 0], (model_h, model_h))
                img_resized = np.expand_dims(img_resized, axis=-1)
            else:
                img_resized = img
            img_batch = np.expand_dims(img_resized, axis=0)
            ml_probs = self.model.predict(img_batch, verbose=0)[0]
            # Blend: heuristics weighted more since model trained on
            # individual 32x32 letters, not full handwriting photos
            probs = (ML_WEIGHT * ml_probs) + (HEURISTIC_WEIGHT * heuristic_probs)
        else:
            probs = heuristic_probs

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
        if analysis.get("irregular_spacing"):
            markers.append("Irregular letter spacing")
        if analysis.get("inconsistent_size"):
            markers.append("Inconsistent letter sizes")
        if analysis.get("poor_alignment"):
            markers.append("Poor baseline alignment")
        if analysis.get("low_stroke_quality"):
            markers.append("Uneven stroke quality")

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

    def _analyze_handwriting(self, image_path: str) -> tuple:
        """Analyze handwriting features from the original image.

        Extracts meaningful features:
        - Stroke regularity (consistency of pen strokes)
        - Spatial distribution (letter spacing uniformity)
        - Baseline alignment (how straight the writing line is)
        - Size consistency (uniform letter heights)
        - Left-right symmetry (reversal indicator)

        Returns: (probability array, analysis dict)
        """
        img = cv2.imread(image_path)
        if img is None:
            return np.array([0.34, 0.33, 0.33]), {}

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        analysis = {}
        risk_score = 0.0

        # 1. Ink density - how much writing is on the page
        ink_density = np.sum(binary > 0) / binary.size
        # Very sparse or very dense writing can indicate issues
        if ink_density < 0.02 or ink_density > 0.6:
            risk_score += 0.05

        # 2. Find contours (connected components = individual strokes/letters)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # Filter tiny noise contours
        min_area = binary.size * 0.0005
        contours = [c for c in contours if cv2.contourArea(c) > min_area]

        if len(contours) < 2:
            # Not enough strokes to analyze
            return np.array([0.5, 0.25, 0.25]), analysis

        # 3. Bounding boxes for each contour
        bboxes = [cv2.boundingRect(c) for c in contours]
        heights = [h for _, _, _, h in bboxes]
        widths = [w for _, _, w, _ in bboxes]
        centers_y = [y + h / 2 for _, y, _, h in bboxes]
        centers_x = [x + w / 2 for x, _, w, _ in bboxes]

        # 4. Size consistency - coefficient of variation of heights
        if len(heights) >= 3:
            height_cv = np.std(heights) / (np.mean(heights) + 1e-6)
            if height_cv > 0.6:
                risk_score += 0.15
                analysis["inconsistent_size"] = True
            elif height_cv > 0.4:
                risk_score += 0.08
                analysis["inconsistent_size"] = True

        # 5. Baseline alignment - how well letters sit on a line
        if len(centers_y) >= 3:
            # Sort by x position and check y-deviation from a fitted line
            sorted_pairs = sorted(zip(centers_x, centers_y))
            y_vals = [y for _, y in sorted_pairs]
            # Deviation from linear trend
            if len(y_vals) >= 3:
                x_arr = np.arange(len(y_vals))
                coeffs = np.polyfit(x_arr, y_vals, 1)
                fitted = np.polyval(coeffs, x_arr)
                residuals = np.std(np.array(y_vals) - fitted)
                avg_height = np.mean(heights)
                alignment_ratio = residuals / (avg_height + 1e-6)
                if alignment_ratio > 0.5:
                    risk_score += 0.15
                    analysis["poor_alignment"] = True
                elif alignment_ratio > 0.3:
                    risk_score += 0.08
                    analysis["poor_alignment"] = True

        # 6. Spacing regularity - gaps between adjacent letters
        if len(bboxes) >= 3:
            sorted_bboxes = sorted(bboxes, key=lambda b: b[0])
            gaps = []
            for i in range(1, len(sorted_bboxes)):
                prev_right = sorted_bboxes[i - 1][0] + sorted_bboxes[i - 1][2]
                curr_left = sorted_bboxes[i][0]
                gaps.append(curr_left - prev_right)
            if len(gaps) >= 2:
                gap_cv = np.std(gaps) / (np.mean(np.abs(gaps)) + 1e-6)
                if gap_cv > 1.0:
                    risk_score += 0.12
                    analysis["irregular_spacing"] = True
                elif gap_cv > 0.6:
                    risk_score += 0.06
                    analysis["irregular_spacing"] = True

        # 7. Stroke quality - smoothness of contours
        if len(contours) >= 2:
            irregularity_scores = []
            for c in contours[:20]:  # Check up to 20 contours
                perimeter = cv2.arcLength(c, True)
                area = cv2.contourArea(c)
                if perimeter > 0:
                    # Circularity measure - jagged strokes have lower values
                    circularity = 4 * np.pi * area / (perimeter * perimeter)
                    irregularity_scores.append(1.0 - circularity)

            if irregularity_scores:
                avg_irregularity = np.mean(irregularity_scores)
                if avg_irregularity > 0.85:
                    risk_score += 0.12
                    analysis["low_stroke_quality"] = True
                elif avg_irregularity > 0.7:
                    risk_score += 0.06
                    analysis["low_stroke_quality"] = True

        # 8. Left-right symmetry (reversal indicator)
        h, w = binary.shape
        mid = w // 2
        left_half = binary[:, :mid]
        right_half = binary[:, mid:]
        right_flipped = np.fliplr(right_half)
        min_w = min(left_half.shape[1], right_flipped.shape[1])
        if min_w > 0:
            asymmetry = np.mean(np.abs(
                left_half[:, :min_w].astype(float) - right_flipped[:, :min_w].astype(float)
            )) / 255.0
            # High symmetry with reversed content suggests letter reversal
            if asymmetry < 0.05 and ink_density > 0.03:
                risk_score += 0.10  # Suspiciously symmetric = possible mirror writing

        # Convert risk score to class probabilities
        risk_score = min(risk_score, 0.90)

        # Distribute risk across Reversal and Corrected
        has_reversal_signs = analysis.get("irregular_spacing") or asymmetry < 0.08 if 'asymmetry' in dir() else False
        if has_reversal_signs:
            reversal_prob = risk_score * 0.6
            corrected_prob = risk_score * 0.4
        else:
            reversal_prob = risk_score * 0.4
            corrected_prob = risk_score * 0.6

        normal_prob = max(0.05, 1.0 - reversal_prob - corrected_prob)

        total = normal_prob + reversal_prob + corrected_prob
        probs = np.array([
            normal_prob / total,
            reversal_prob / total,
            corrected_prob / total,
        ])

        return probs, analysis
