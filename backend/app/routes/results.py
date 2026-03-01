from flask import Blueprint, request, jsonify
from app import db
from app.models.db_models import TestSession, HandwritingTest, SpeechTest
from app.ml.scoring.combined_scorer import CombinedScorer

results_bp = Blueprint("results", __name__)
scorer = CombinedScorer()


@results_bp.route("/results/combine", methods=["POST"])
def combine_results():
    data = request.get_json()
    session_id = data.get("session_id")
    if not session_id:
        return jsonify({"error": "session_id is required"}), 400

    session = db.session.get(TestSession, int(session_id))
    if not session:
        return jsonify({"error": "Test session not found"}), 404

    handwriting_score = data.get("handwriting_score")
    speech_score = data.get("speech_score")

    if handwriting_score is None and speech_score is None:
        return jsonify({"error": "At least one score is required"}), 400

    result = scorer.compute(
        handwriting_score=handwriting_score,
        speech_score=speech_score,
    )

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
    session = db.session.get(TestSession, session_id)
    if not session:
        return jsonify({"error": "Test session not found"}), 404
    return jsonify(session.to_dict())


@results_bp.route("/results/history/<int:user_id>", methods=["GET"])
def get_history(user_id):
    sessions = (
        TestSession.query
        .filter_by(user_id=user_id)
        .order_by(TestSession.created_at.desc())
        .all()
    )
    return jsonify([s.to_dict() for s in sessions])
