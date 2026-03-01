from flask import Blueprint, request, jsonify
from app import db
from app.models.db_models import User, TestSession

users_bp = Blueprint("users", __name__)


@users_bp.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    if not data or not data.get("name") or not data.get("age"):
        return jsonify({"error": "Name and age are required"}), 400

    user = User(
        name=data["name"],
        age=int(data["age"]),
        gender=data.get("gender"),
        parent_email=data.get("parent_email"),
    )
    db.session.add(user)
    db.session.commit()

    # Create a test session for this user
    session = TestSession(user_id=user.id)
    db.session.add(session)
    db.session.commit()

    return jsonify({
        "user": user.to_dict(),
        "session_id": session.id,
    }), 201


@users_bp.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict())


@users_bp.route("/users", methods=["GET"])
def list_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify([u.to_dict() for u in users])
