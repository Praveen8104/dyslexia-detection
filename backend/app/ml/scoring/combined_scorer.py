DISCLAIMER = (
    "This is a screening tool, not a clinical diagnosis. "
    "It identifies potential indicators of dyslexia based on handwriting and speech patterns. "
    "A positive result does not confirm dyslexia, and a negative result does not rule it out. "
    "Results should always be interpreted by a qualified professional "
    "(educational psychologist, speech-language pathologist, or specialist teacher)."
)

RISK_LEVELS = {
    "low": {
        "range": (0, 30),
        "label": "Low Risk",
        "recommendation": (
            "No significant indicators detected. "
            "Continue to monitor the child's reading and writing development. "
            "If you have concerns, consider re-screening in 6-12 months."
        ),
    },
    "moderate": {
        "range": (31, 60),
        "label": "Moderate Risk",
        "recommendation": (
            "Some indicators are present. We recommend consulting a learning specialist "
            "or educational psychologist for a more comprehensive assessment. "
            "Early intervention can make a significant difference. "
            "Consider re-screening after 2-4 weeks to confirm these findings."
        ),
    },
    "high": {
        "range": (61, 100),
        "label": "High Risk",
        "recommendation": (
            "Multiple indicators are present. A professional evaluation by an educational psychologist "
            "or speech-language pathologist is strongly recommended. "
            "Early identification and targeted intervention can greatly improve reading outcomes. "
            "Please share this report with the child's teacher and healthcare provider."
        ),
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
            return "Low Risk", RISK_LEVELS["low"]["recommendation"]
        elif score <= 60:
            return "Moderate Risk", RISK_LEVELS["moderate"]["recommendation"]
        else:
            return "High Risk", RISK_LEVELS["high"]["recommendation"]
