import json
import pytest
from app import create_app, db


@pytest.fixture
def app():
    app = create_app(testing=True)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["TESTING"] = True

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


class TestUserAPI:
    def test_create_user(self, client):
        response = client.post(
            "/api/users",
            data=json.dumps({"name": "Test Child", "age": 8}),
            content_type="application/json",
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data["user"]["name"] == "Test Child"
        assert data["user"]["age"] == 8
        assert "session_id" in data

    def test_create_user_missing_fields(self, client):
        response = client.post(
            "/api/users",
            data=json.dumps({"name": "Test"}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_get_user(self, client):
        # Create user first
        res = client.post(
            "/api/users",
            data=json.dumps({"name": "Test Child", "age": 7}),
            content_type="application/json",
        )
        user_id = res.get_json()["user"]["id"]

        response = client.get(f"/api/users/{user_id}")
        assert response.status_code == 200
        assert response.get_json()["name"] == "Test Child"

    def test_get_user_not_found(self, client):
        response = client.get("/api/users/999")
        assert response.status_code == 404

    def test_list_users(self, client):
        client.post(
            "/api/users",
            data=json.dumps({"name": "Child 1", "age": 6}),
            content_type="application/json",
        )
        client.post(
            "/api/users",
            data=json.dumps({"name": "Child 2", "age": 9}),
            content_type="application/json",
        )

        response = client.get("/api/users")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2


class TestResultsAPI:
    def test_combine_results(self, client):
        # Create user and session
        res = client.post(
            "/api/users",
            data=json.dumps({"name": "Test", "age": 8}),
            content_type="application/json",
        )
        session_id = res.get_json()["session_id"]

        response = client.post(
            "/api/results/combine",
            data=json.dumps({
                "session_id": session_id,
                "handwriting_score": 40,
                "speech_score": 60,
            }),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.get_json()
        # 40 * 0.55 + 60 * 0.45 = 22 + 27 = 49
        assert data["combined_score"] == 49.0
        assert data["risk_level"] == "Moderate Risk"
        assert "disclaimer" in data

    def test_combine_handwriting_only(self, client):
        res = client.post(
            "/api/users",
            data=json.dumps({"name": "Test", "age": 8}),
            content_type="application/json",
        )
        session_id = res.get_json()["session_id"]

        response = client.post(
            "/api/results/combine",
            data=json.dumps({
                "session_id": session_id,
                "handwriting_score": 20,
            }),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["combined_score"] == 20.0
        assert data["risk_level"] == "Low Risk"

    def test_get_results(self, client):
        res = client.post(
            "/api/users",
            data=json.dumps({"name": "Test", "age": 8}),
            content_type="application/json",
        )
        session_id = res.get_json()["session_id"]

        response = client.get(f"/api/results/{session_id}")
        assert response.status_code == 200

    def test_get_history(self, client):
        res = client.post(
            "/api/users",
            data=json.dumps({"name": "Test", "age": 8}),
            content_type="application/json",
        )
        user_id = res.get_json()["user"]["id"]

        response = client.get(f"/api/results/history/{user_id}")
        assert response.status_code == 200
        assert len(response.get_json()) == 1


class TestCombinedScorer:
    def test_low_risk(self):
        from app.ml.scoring.combined_scorer import CombinedScorer
        scorer = CombinedScorer()
        result = scorer.compute(handwriting_score=10, speech_score=20)
        assert result["risk_level"] == "Low Risk"

    def test_moderate_risk(self):
        from app.ml.scoring.combined_scorer import CombinedScorer
        scorer = CombinedScorer()
        result = scorer.compute(handwriting_score=50, speech_score=50)
        assert result["risk_level"] == "Moderate Risk"

    def test_high_risk(self):
        from app.ml.scoring.combined_scorer import CombinedScorer
        scorer = CombinedScorer()
        result = scorer.compute(handwriting_score=80, speech_score=80)
        assert result["risk_level"] == "High Risk"

    def test_weighted_formula(self):
        from app.ml.scoring.combined_scorer import CombinedScorer
        scorer = CombinedScorer()
        result = scorer.compute(handwriting_score=100, speech_score=0)
        assert result["combined_score"] == 55.0  # 100 * 0.55 + 0 * 0.45
