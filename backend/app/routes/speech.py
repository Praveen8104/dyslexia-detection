import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models.db_models import SpeechTest, TestSession
from app.ml.speech.predictor import SpeechPredictor

speech_bp = Blueprint("speech", __name__)

predictor = None


def get_predictor():
    global predictor
    if predictor is None:
        predictor = SpeechPredictor()
    return predictor


@speech_bp.route("/speech/analyze", methods=["POST"])
def analyze_speech():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    session_id = request.form.get("session_id")
    expected_text = request.form.get("expected_text", "")
    if not session_id:
        return jsonify({"error": "session_id is required"}), 400

    session = db.session.get(TestSession, int(session_id))
    if not session:
        return jsonify({"error": "Test session not found"}), 404

    file = request.files["audio"]
    ext = os.path.splitext(file.filename)[1] or ".wav"
    filename = f"{uuid.uuid4().hex}{ext}"
    upload_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], "audio")
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)

    # Run prediction
    pred = get_predictor()
    result = pred.predict(filepath, expected_text)

    # Save to database
    test = SpeechTest(
        session_id=int(session_id),
        audio_path=filepath,
        expected_text=expected_text,
        prediction=result["prediction"],
        confidence=result["confidence"],
        reading_speed_wpm=result.get("reading_speed_wpm"),
        hesitation_count=result.get("hesitation_count"),
        silence_ratio=result.get("silence_ratio"),
    )
    db.session.add(test)
    db.session.commit()

    return jsonify({
        "id": test.id,
        "prediction": result["prediction"],
        "confidence": result["confidence"],
        "reading_speed_wpm": result.get("reading_speed_wpm"),
        "hesitation_count": result.get("hesitation_count"),
        "silence_ratio": result.get("silence_ratio"),
        "risk_score": result["risk_score"],
    })
