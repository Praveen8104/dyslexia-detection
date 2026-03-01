import logging
from flask import Blueprint, request, jsonify
from app import db
from app.models.db_models import TestSession
from app.ml.scoring.combined_scorer import CombinedScorer

logger = logging.getLogger(__name__)
results_bp = Blueprint("results", __name__)
scorer = CombinedScorer()


@results_bp.route("/results/combine", methods=["POST"])
def combine_results():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    session_id = data.get("session_id")
    if not session_id:
        return jsonify({"error": "session_id is required"}), 400

    try:
        session_id_int = int(session_id)
    except (ValueError, TypeError):
        return jsonify({"error": "session_id must be a number"}), 400

    session = db.session.get(TestSession, session_id_int)
    if not session:
        return jsonify({"error": "Test session not found"}), 404

    handwriting_score = data.get("handwriting_score")
    speech_score = data.get("speech_score")

    if handwriting_score is None and speech_score is None:
        return jsonify({"error": "At least one score is required"}), 400

    # Validate score ranges
    try:
        if handwriting_score is not None:
            handwriting_score = float(handwriting_score)
            if not 0 <= handwriting_score <= 100:
                return jsonify({"error": "handwriting_score must be between 0 and 100"}), 400
        if speech_score is not None:
            speech_score = float(speech_score)
            if not 0 <= speech_score <= 100:
                return jsonify({"error": "speech_score must be between 0 and 100"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Scores must be numbers"}), 400

    try:
        result = scorer.compute(
            handwriting_score=handwriting_score,
            speech_score=speech_score,
        )
    except Exception as e:
        logger.error(f"Combined scoring failed: {e}")
        return jsonify({"error": "Scoring calculation failed"}), 500

    session.combined_score = result["combined_score"]
    session.risk_level = result["risk_level"]
    db.session.commit()

    return jsonify({
        "session_id": session.id,
        "combined_score": result["combined_score"],
        "risk_level": result["risk_level"],
        "recommendation": result["recommendation"],
        "disclaimer": result["disclaimer"],
    })


@results_bp.route("/results/<int:session_id>", methods=["GET"])
def get_results(session_id):
    from app.models.db_models import User

    session = db.session.get(TestSession, session_id)
    if not session:
        return jsonify({"error": "Test session not found"}), 404
    d = session.to_dict()
    user = db.session.get(User, session.user_id)
    d["user_name"] = user.name if user else "Unknown"
    d["user_age"] = user.age if user else None
    return jsonify(d)


@results_bp.route("/results/history/<int:user_id>", methods=["GET"])
def get_history(user_id):
    sessions = (
        TestSession.query
        .filter_by(user_id=user_id)
        .order_by(TestSession.created_at.desc())
        .all()
    )
    return jsonify([s.to_dict() for s in sessions])


@results_bp.route("/results/all", methods=["GET"])
def get_all_sessions():
    from app.models.db_models import User

    sessions = (
        TestSession.query
        .order_by(TestSession.created_at.desc())
        .all()
    )
    result = []
    for s in sessions:
        d = s.to_dict()
        user = db.session.get(User, s.user_id)
        d["user_name"] = user.name if user else "Unknown"
        d["user_age"] = user.age if user else None
        result.append(d)
    return jsonify(result)
