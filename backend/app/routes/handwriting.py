import os
import uuid
import json
from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models.db_models import HandwritingTest, TestSession
from app.ml.handwriting.predictor import HandwritingPredictor

handwriting_bp = Blueprint("handwriting", __name__)

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

    session = db.session.get(TestSession, int(session_id))
    if not session:
        return jsonify({"error": "Test session not found"}), 404

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # Save uploaded image
    ext = os.path.splitext(file.filename)[1] or ".png"
    filename = f"{uuid.uuid4().hex}{ext}"
    upload_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], "handwriting")
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)

    # Run prediction
    pred = get_predictor()
    result = pred.predict(filepath)

    # Save to database
    test = HandwritingTest(
        session_id=int(session_id),
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
