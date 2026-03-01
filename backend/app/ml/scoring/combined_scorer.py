DISCLAIMER = (
    "This is a screening tool, not a clinical diagnosis. "
    "Results should be interpreted by a qualified professional."
)

RISK_LEVELS = {
    "low": {"range": (0, 30), "label": "Low Risk"},
    "moderate": {
        "range": (31, 60),
        "label": "Moderate Risk",
        "recommendation": "Consider consulting a learning specialist.",
    },
    "high": {
        "range": (61, 100),
        "label": "High Risk",
        "recommendation": "Professional evaluation recommended.",
    },
}


class CombinedScorer:
    HANDWRITING_WEIGHT = 0.55
    SPEECH_WEIGHT = 0.45

    def compute(self, handwriting_score: float = None,
                speech_score: float = None) -> dict:
        """Compute combined risk score from individual module scores.

        Args:
            handwriting_score: Risk score from handwriting analysis (0-100)
            speech_score: Risk score from speech analysis (0-100)

        Returns:
            dict with combined_score, risk_level, recommendation, disclaimer
        """
        if handwriting_score is not None and speech_score is not None:
            combined = (
                handwriting_score * self.HANDWRITING_WEIGHT
                + speech_score * self.SPEECH_WEIGHT
            )
        elif handwriting_score is not None:
            combined = handwriting_score
        else:
            combined = speech_score

        combined = round(min(max(combined, 0), 100), 2)

        risk_level, recommendation = self._classify_risk(combined)

        return {
            "combined_score": combined,
            "risk_level": risk_level,
            "recommendation": recommendation,
            "disclaimer": DISCLAIMER,
        }

    def _classify_risk(self, score: float) -> tuple:
        if score <= 30:
            return "Low Risk", "No significant indicators detected."
        elif score <= 60:
            return "Moderate Risk", RISK_LEVELS["moderate"]["recommendation"]
        else:
            return "High Risk", RISK_LEVELS["high"]["recommendation"]
