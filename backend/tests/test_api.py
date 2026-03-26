import io
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


# ---------------------------------------------------------------------------
# Helper to create a user + session for reuse
# ---------------------------------------------------------------------------
def _create_user(client, name="Test Child", age=8):
    res = client.post(
        "/api/users",
        data=json.dumps({"name": name, "age": age}),
        content_type="application/json",
    )
    data = res.get_json()
    return data["user"], data["session_id"]


# ===========================================================================
# User API Tests
# ===========================================================================
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

    def test_create_user_missing_name(self, client):
        response = client.post(
            "/api/users",
            data=json.dumps({"age": 8}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_create_user_invalid_age_string(self, client):
        response = client.post(
            "/api/users",
            data=json.dumps({"name": "Test", "age": "abc"}),
            content_type="application/json",
        )
        assert response.status_code == 400
        assert "valid number" in response.get_json()["error"]

    def test_create_user_age_too_low(self, client):
        response = client.post(
            "/api/users",
            data=json.dumps({"name": "Test", "age": 1}),
            content_type="application/json",
        )
        assert response.status_code == 400
        assert "between 3 and 18" in response.get_json()["error"]

    def test_create_user_age_too_high(self, client):
        response = client.post(
            "/api/users",
            data=json.dumps({"name": "Test", "age": 25}),
            content_type="application/json",
        )
        assert response.status_code == 400
        assert "between 3 and 18" in response.get_json()["error"]

    def test_create_user_with_optional_fields(self, client):
        response = client.post(
            "/api/users",
            data=json.dumps({
                "name": "Alice",
                "age": 7,
                "gender": "female",
                "parent_email": "parent@example.com",
            }),
            content_type="application/json",
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data["user"]["gender"] == "female"
        assert data["user"]["parent_email"] == "parent@example.com"

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


# ===========================================================================
# Results API Tests
# ===========================================================================
class TestResultsAPI:
    def test_combine_results(self, client):
        _, session_id = _create_user(client)

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
        _, session_id = _create_user(client)

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

    def test_combine_speech_only(self, client):
        _, session_id = _create_user(client)

        response = client.post(
            "/api/results/combine",
            data=json.dumps({
                "session_id": session_id,
                "speech_score": 75,
            }),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["combined_score"] == 75.0
        assert data["risk_level"] == "High Risk"

    def test_combine_no_scores(self, client):
        _, session_id = _create_user(client)

        response = client.post(
            "/api/results/combine",
            data=json.dumps({"session_id": session_id}),
            content_type="application/json",
        )
        assert response.status_code == 400
        assert "At least one score" in response.get_json()["error"]

    def test_combine_invalid_score_range(self, client):
        _, session_id = _create_user(client)

        response = client.post(
            "/api/results/combine",
            data=json.dumps({
                "session_id": session_id,
                "handwriting_score": 150,
            }),
            content_type="application/json",
        )
        assert response.status_code == 400
        assert "between 0 and 100" in response.get_json()["error"]

    def test_combine_non_numeric_score(self, client):
        _, session_id = _create_user(client)

        response = client.post(
            "/api/results/combine",
            data=json.dumps({
                "session_id": session_id,
                "handwriting_score": "abc",
            }),
            content_type="application/json",
        )
        assert response.status_code == 400
        assert "numbers" in response.get_json()["error"]

    def test_combine_invalid_session(self, client):
        response = client.post(
            "/api/results/combine",
            data=json.dumps({
                "session_id": 99999,
                "handwriting_score": 50,
            }),
            content_type="application/json",
        )
        assert response.status_code == 404

    def test_combine_missing_body(self, client):
        response = client.post(
            "/api/results/combine",
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_get_results(self, client):
        _, session_id = _create_user(client)

        response = client.get(f"/api/results/{session_id}")
        assert response.status_code == 200
        data = response.get_json()
        assert "handwriting_tests" in data
        assert "speech_tests" in data

    def test_get_results_includes_user_info(self, client):
        user, session_id = _create_user(client, name="Alice", age=9)

        response = client.get(f"/api/results/{session_id}")
        assert response.status_code == 200
        data = response.get_json()
        assert data["user_name"] == "Alice"
        assert data["user_age"] == 9

    def test_get_results_not_found(self, client):
        response = client.get("/api/results/99999")
        assert response.status_code == 404

    def test_get_history(self, client):
        user, _ = _create_user(client)

        response = client.get(f"/api/results/history/{user['id']}")
        assert response.status_code == 200
        assert len(response.get_json()) == 1

    def test_get_all_sessions(self, client):
        _create_user(client, name="Child A", age=6)
        _create_user(client, name="Child B", age=10)

        response = client.get("/api/results/all")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2
        assert all("user_name" in s for s in data)


# ===========================================================================
# Combined Scorer Unit Tests
# ===========================================================================
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

    def test_boundary_low_moderate(self):
        from app.ml.scoring.combined_scorer import CombinedScorer
        scorer = CombinedScorer()
        result = scorer.compute(handwriting_score=30, speech_score=30)
        assert result["risk_level"] == "Low Risk"

    def test_boundary_moderate_high(self):
        from app.ml.scoring.combined_scorer import CombinedScorer
        scorer = CombinedScorer()
        result = scorer.compute(handwriting_score=60, speech_score=60)
        assert result["risk_level"] == "Moderate Risk"

    def test_boundary_just_high(self):
        from app.ml.scoring.combined_scorer import CombinedScorer
        scorer = CombinedScorer()
        result = scorer.compute(handwriting_score=61, speech_score=61)
        assert result["risk_level"] == "High Risk"

    def test_score_clamped_to_100(self):
        from app.ml.scoring.combined_scorer import CombinedScorer
        scorer = CombinedScorer()
        result = scorer.compute(handwriting_score=100, speech_score=100)
        assert result["combined_score"] == 100.0

    def test_score_clamped_to_0(self):
        from app.ml.scoring.combined_scorer import CombinedScorer
        scorer = CombinedScorer()
        result = scorer.compute(handwriting_score=0, speech_score=0)
        assert result["combined_score"] == 0.0

    def test_disclaimer_present(self):
        from app.ml.scoring.combined_scorer import CombinedScorer
        scorer = CombinedScorer()
        result = scorer.compute(handwriting_score=50, speech_score=50)
        assert "screening tool" in result["disclaimer"].lower()
        assert "not a clinical diagnosis" in result["disclaimer"].lower()

    def test_recommendation_present(self):
        from app.ml.scoring.combined_scorer import CombinedScorer
        scorer = CombinedScorer()
        for hw, sp in [(10, 10), (50, 50), (80, 80)]:
            result = scorer.compute(handwriting_score=hw, speech_score=sp)
            assert len(result["recommendation"]) > 10


# ===========================================================================
# Handwriting Upload Validation Tests
# ===========================================================================
class TestHandwritingValidation:
    def test_no_image_provided(self, client):
        _, session_id = _create_user(client)
        response = client.post(
            "/api/handwriting/analyze",
            data={"session_id": str(session_id)},
        )
        assert response.status_code == 400
        assert "No image file" in response.get_json()["error"]

    def test_missing_session_id(self, client):
        data = {"image": (io.BytesIO(b"fake"), "test.png")}
        response = client.post("/api/handwriting/analyze", data=data)
        assert response.status_code == 400
        assert "session_id" in response.get_json()["error"]

    def test_invalid_session_id(self, client):
        data = {
            "image": (io.BytesIO(b"fake"), "test.png"),
            "session_id": "abc",
        }
        response = client.post("/api/handwriting/analyze", data=data)
        assert response.status_code == 400
        assert "number" in response.get_json()["error"]

    def test_session_not_found(self, client):
        data = {
            "image": (io.BytesIO(b"fake"), "test.png"),
            "session_id": "99999",
        }
        response = client.post("/api/handwriting/analyze", data=data)
        assert response.status_code == 404

    def test_invalid_image_extension(self, client):
        _, session_id = _create_user(client)
        data = {
            "image": (io.BytesIO(b"fake"), "test.gif"),
            "session_id": str(session_id),
        }
        response = client.post("/api/handwriting/analyze", data=data)
        assert response.status_code == 400
        assert "Invalid image format" in response.get_json()["error"]

    def test_empty_filename(self, client):
        _, session_id = _create_user(client)
        data = {
            "image": (io.BytesIO(b"fake"), ""),
            "session_id": str(session_id),
        }
        response = client.post("/api/handwriting/analyze", data=data)
        assert response.status_code == 400


# ===========================================================================
# Speech Upload Validation Tests
# ===========================================================================
class TestSpeechValidation:
    def test_no_audio_provided(self, client):
        _, session_id = _create_user(client)
        response = client.post(
            "/api/speech/analyze",
            data={"session_id": str(session_id)},
        )
        assert response.status_code == 400
        assert "No audio file" in response.get_json()["error"]

    def test_missing_session_id(self, client):
        data = {"audio": (io.BytesIO(b"fake"), "test.wav")}
        response = client.post("/api/speech/analyze", data=data)
        assert response.status_code == 400

    def test_invalid_audio_extension(self, client):
        _, session_id = _create_user(client)
        data = {
            "audio": (io.BytesIO(b"fake"), "test.exe"),
            "session_id": str(session_id),
        }
        response = client.post("/api/speech/analyze", data=data)
        assert response.status_code == 400
        assert "Unsupported audio format" in response.get_json()["error"]

    def test_session_not_found(self, client):
        data = {
            "audio": (io.BytesIO(b"fake"), "test.wav"),
            "session_id": "99999",
        }
        response = client.post("/api/speech/analyze", data=data)
        assert response.status_code == 404


# ===========================================================================
# Preprocessing Unit Tests
# ===========================================================================
class TestPreprocessor:
    def test_preprocess_invalid_path(self):
        from app.ml.handwriting.preprocessor import preprocess_image
        with pytest.raises(ValueError, match="Could not read image"):
            preprocess_image("/nonexistent/path.png")

    def test_preprocess_output_shape(self, tmp_path):
        """Verify preprocessor returns correct shape for a valid image."""
        import numpy as np
        import cv2
        from app.ml.handwriting.preprocessor import preprocess_image

        # Create a simple test image
        img = np.zeros((100, 200, 3), dtype=np.uint8)
        cv2.putText(img, "Hello", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)
        path = str(tmp_path / "test.png")
        cv2.imwrite(path, img)

        result = preprocess_image(path)
        assert result.shape == (224, 224, 1)
        assert result.dtype == np.float32
        assert 0.0 <= result.min() <= result.max() <= 1.0


# ===========================================================================
# Audio Processor Unit Tests
# ===========================================================================
class TestAudioProcessor:
    def test_silence_ratio_range(self):
        """Silence ratio should always be between 0.0 and 1.0."""
        import numpy as np
        from app.ml.speech.audio_processor import compute_silence_ratio

        # Generate tone with gaps (speech-like)
        sr = 16000
        tone = np.zeros(sr * 2, dtype=np.float32)
        t = np.linspace(0, 0.5, sr // 2, dtype=np.float32)
        tone[:sr // 2] = 0.5 * np.sin(2 * np.pi * 440 * t)
        # Leave second half silent
        ratio = compute_silence_ratio(tone, sr=sr)
        assert 0.0 <= ratio <= 1.0

    def test_hesitation_count_no_pauses(self):
        """A continuous tone should have zero hesitations."""
        import numpy as np
        from app.ml.speech.audio_processor import count_hesitations

        # Generate a continuous 440Hz tone (1 second)
        sr = 16000
        t = np.linspace(0, 1, sr, dtype=np.float32)
        tone = 0.5 * np.sin(2 * np.pi * 440 * t)
        assert count_hesitations(tone, sr=sr) == 0

    def test_reading_speed_returns_float(self):
        """Reading speed should always return a non-negative float."""
        import numpy as np
        from app.ml.speech.audio_processor import estimate_reading_speed

        sr = 16000
        # Generate a 3-second tone
        t = np.linspace(0, 3, sr * 3, dtype=np.float32)
        tone = 0.5 * np.sin(2 * np.pi * 440 * t)
        wpm = estimate_reading_speed(tone, sr=sr, expected_word_count=10)
        assert isinstance(wpm, float)
        assert wpm >= 0.0


# ===========================================================================
# Feature Extractor Unit Tests
# ===========================================================================
class TestFeatureExtractor:
    def test_mfcc_output_shape(self):
        import numpy as np
        from app.ml.speech.feature_extractor import extract_mfcc_features, MAX_FRAMES, NUM_FEATURES

        # 2 seconds of random audio
        signal = np.random.randn(32000).astype(np.float32)
        features = extract_mfcc_features(signal, sr=16000)
        assert features.shape == (MAX_FRAMES, NUM_FEATURES)
        assert features.dtype == np.float32

    def test_mfcc_short_audio_padded(self):
        import numpy as np
        from app.ml.speech.feature_extractor import extract_mfcc_features, MAX_FRAMES, NUM_FEATURES

        # Very short audio (0.5 seconds)
        signal = np.random.randn(8000).astype(np.float32)
        features = extract_mfcc_features(signal, sr=16000)
        assert features.shape == (MAX_FRAMES, NUM_FEATURES)
