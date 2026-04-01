import os
import uuid
import logging
from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models.db_models import SpeechTest, TestSession
from app.ml.speech.predictor import SpeechPredictor

logger = logging.getLogger(__name__)
speech_bp = Blueprint("speech", __name__)

MAX_AUDIO_SIZE = 10 * 1024 * 1024  # 10MB

_predictor = None
_predictor_lock = __import__("threading").Lock()


def get_predictor():
    global _predictor
    if _predictor is None:
        with _predictor_lock:
            if _predictor is None:
                _predictor = SpeechPredictor()
    return _predictor


@speech_bp.route("/speech/analyze", methods=["POST"])
def analyze_speech():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    session_id = request.form.get("session_id")
    expected_text = request.form.get("expected_text", "")
    if not session_id:
        return jsonify({"error": "session_id is required"}), 400

    try:
        session_id_int = int(session_id)
    except ValueError:
        return jsonify({"error": "session_id must be a number"}), 400

    session = db.session.get(TestSession, session_id_int)
    if not session:
        return jsonify({"error": "Test session not found"}), 404

    file = request.files["audio"]
    ext = os.path.splitext(file.filename)[1].lower() or ".wav"

    # Validate audio format
    allowed_audio_ext = {".wav", ".mp3", ".webm", ".ogg", ".m4a", ".flac", ".aac"}
    if ext not in allowed_audio_ext:
        return jsonify({
            "error": f"Unsupported audio format '{ext}'. Allowed: {', '.join(sorted(allowed_audio_ext))}"
        }), 400

    # Validate file size before saving
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    if file_size > MAX_AUDIO_SIZE:
        return jsonify({"error": "Audio file too large. Maximum size is 10MB."}), 400

    filename = f"{uuid.uuid4().hex}{ext}"
    upload_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], "audio")
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)

    # Get child age for age-appropriate thresholds
    child_age = None
    if session.user and session.user.age is not None:
        child_age = session.user.age

    try:
        pred = get_predictor()
        result = pred.predict(filepath, expected_text, child_age=child_age)
    except Exception as e:
        logger.error(f"Speech prediction failed: {e}")
        try:
            os.remove(filepath)
        except OSError:
            pass
        return jsonify({"error": "Speech analysis failed. Please try recording again."}), 500

    # Validate audio duration (signal must be at least 1 second)
    if result.get("reading_speed_wpm", 0) == 0:
        try:
            os.remove(filepath)
        except OSError:
            pass
        return jsonify({"error": "Audio too short. Please record for at least 2 seconds."}), 400

    # Save to database
    test = SpeechTest(
        session_id=session_id_int,
        audio_path=filepath,
        expected_text=expected_text,
        prediction=result["prediction"],
        confidence=result["confidence"],
        reading_speed_wpm=result.get("reading_speed_wpm"),
        hesitation_count=result.get("hesitation_count"),
        silence_ratio=result.get("silence_ratio"),
        transcript=result.get("transcription", ""),
        reading_accuracy=result.get("reading_accuracy"),
        wer=result.get("wer"),
        substitutions=result.get("substitutions", 0),
        deletions=result.get("deletions", 0),
        insertions=result.get("insertions", 0),
        error_details=result.get("error_details", ""),
    )
    try:
        db.session.add(test)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to save speech result: {e}")
        try:
            os.remove(filepath)
        except OSError:
            pass
        return jsonify({"error": "Failed to save results. Please try again."}), 500

    return jsonify({
        "id": test.id,
        "prediction": result["prediction"],
        "confidence": result["confidence"],
        "reading_speed_wpm": result.get("reading_speed_wpm"),
        "hesitation_count": result.get("hesitation_count"),
        "silence_ratio": result.get("silence_ratio"),
        "risk_score": result["risk_score"],
        # Transcription & reading accuracy
        "transcription": result.get("transcription", ""),
        "reading_accuracy": result.get("reading_accuracy"),
        "wer": result.get("wer"),
        "substitutions": result.get("substitutions", 0),
        "deletions": result.get("deletions", 0),
        "insertions": result.get("insertions", 0),
        "error_details": result.get("error_details", ""),
    })
