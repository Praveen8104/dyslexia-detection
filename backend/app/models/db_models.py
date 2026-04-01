from datetime import datetime, timezone
from app import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20))
    parent_email = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    sessions = db.relationship("TestSession", backref="user", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "parent_email": self.parent_email,
            "created_at": self.created_at.isoformat(),
        }


class TestSession(db.Model):
    __tablename__ = "test_sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    combined_score = db.Column(db.Float)
    risk_level = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    handwriting_tests = db.relationship("HandwritingTest", backref="session", lazy=True)
    speech_tests = db.relationship("SpeechTest", backref="session", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "combined_score": self.combined_score,
            "risk_level": self.risk_level,
            "created_at": self.created_at.isoformat(),
            "handwriting_tests": [t.to_dict() for t in self.handwriting_tests],
            "speech_tests": [t.to_dict() for t in self.speech_tests],
        }


class HandwritingTest(db.Model):
    __tablename__ = "handwriting_tests"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("test_sessions.id"), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    prediction = db.Column(db.String(50))
    confidence = db.Column(db.Float)
    markers = db.Column(db.Text)  # JSON string of detected markers
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "prediction": self.prediction,
            "confidence": self.confidence,
            "markers": self.markers,
            "created_at": self.created_at.isoformat(),
        }


class SpeechTest(db.Model):
    __tablename__ = "speech_tests"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("test_sessions.id"), nullable=False)
    audio_path = db.Column(db.String(255), nullable=False)
    transcript = db.Column(db.Text)
    expected_text = db.Column(db.Text)
    prediction = db.Column(db.String(50))
    confidence = db.Column(db.Float)
    reading_speed_wpm = db.Column(db.Float)
    hesitation_count = db.Column(db.Integer)
    silence_ratio = db.Column(db.Float)
    reading_accuracy = db.Column(db.Float)
    wer = db.Column(db.Float)
    substitutions = db.Column(db.Integer)
    deletions = db.Column(db.Integer)
    insertions = db.Column(db.Integer)
    error_details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "expected_text": self.expected_text,
            "prediction": self.prediction,
            "confidence": self.confidence,
            "reading_speed_wpm": self.reading_speed_wpm,
            "hesitation_count": self.hesitation_count,
            "silence_ratio": self.silence_ratio,
            "transcript": self.transcript,
            "reading_accuracy": self.reading_accuracy,
            "wer": self.wer,
            "substitutions": self.substitutions,
            "deletions": self.deletions,
            "insertions": self.insertions,
            "error_details": self.error_details,
            "created_at": self.created_at.isoformat(),
        }
