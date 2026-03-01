import os
import uuid
import json
import logging
from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models.db_models import HandwritingTest, TestSession
from app.ml.handwriting.predictor import HandwritingPredictor

logger = logging.getLogger(__name__)
handwriting_bp = Blueprint("handwriting", __name__)

ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB

predictor = None


def get_predictor():
    global predictor
    if predictor is None:
        predictor = HandwritingPredictor()
    return predictor


@handwriting_bp.route("/handwriting/analyze", methods=["POST"])
def analyze_handwriting():
    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    session_id = request.form.get("session_id")
    if not session_id:
        return jsonify({"error": "session_id is required"}), 400

    try:
        session_id_int = int(session_id)
    except ValueError:
        return jsonify({"error": "session_id must be a number"}), 400

    session = db.session.get(TestSession, session_id_int)
    if not session:
        return jsonify({"error": "Test session not found"}), 404

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # Validate file extension
    ext = os.path.splitext(file.filename)[1].lower() or ".png"
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        return jsonify({"error": f"Invalid image format. Allowed: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"}), 400

    # Save uploaded image
    filename = f"{uuid.uuid4().hex}{ext}"
    upload_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], "handwriting")
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)

    # Validate file size
    file_size = os.path.getsize(filepath)
    if file_size > MAX_IMAGE_SIZE:
        os.remove(filepath)
        return jsonify({"error": "Image too large. Maximum size is 10MB."}), 400

    try:
        pred = get_predictor()
        result = pred.predict(filepath)
    except Exception as e:
        logger.error(f"Handwriting prediction failed: {e}")
        os.remove(filepath)
        return jsonify({"error": "Analysis failed. Please try again with a clearer image."}), 500

    # Save to database
    test = HandwritingTest(
        session_id=session_id_int,
        image_path=filepath,
        prediction=result["prediction"],
        confidence=result["confidence"],
        markers=json.dumps(result.get("markers", [])),
    )
    db.session.add(test)
    db.session.commit()

    return jsonify({
        "id": test.id,
        "prediction": result["prediction"],
        "confidence": result["confidence"],
        "markers": result.get("markers", []),
        "risk_score": result["risk_score"],
    })
