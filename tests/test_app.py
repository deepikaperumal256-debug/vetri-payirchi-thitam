import os

# Use demo mode during tests
os.environ["AI_DEMO_MODE"] = "true"

os.environ[
    "DATABASE_URL"
] = "sqlite:///./test_fitbuddy.db"

os.environ[
    "ADMIN_KEY"
] = "test-key"


from fastapi.testclient import TestClient

from app.main import app
from app import gemini_client


client = TestClient(app)


def test_health():

    response = client.get(
        "/api/health"
    )

    assert response.status_code == 200

    assert response.json()["status"] == "ok"


def test_home():

    response = client.get("/")

    assert response.status_code == 200

    assert "FitBuddy" in response.text


def test_generate_workout():

    response = client.post(
        "/api/generate-workout",

        json={
            "username": "Test User",
            "user_id": "TEST001",
            "age": 20,
            "weight": 60,
            "goal": "general wellness",
            "intensity": "low",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "workout_plan" in data

    assert "nutrition_tip" in data


def test_feedback():

    response = client.post(
        "/api/submit-feedback",

        json={
            "user_id": "TEST001",
            "feedback":
                "Make day 6 easier and add mobility.",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "updated_plan" in data
    assert data["updated_plan"]


def test_generate_text_retries_service_unavailable(monkeypatch):

    class ServiceUnavailable(Exception):
        code = 503

    class FakeModels:

        calls = 0

        def generate_content(self, **kwargs):
            self.calls += 1

            if self.calls == 1:
                raise ServiceUnavailable("temporarily unavailable")

            return type("Response", (), {"text": "Generated plan"})()

    models = FakeModels()
    fake_client = type("Client", (), {"models": models})()
    monkeypatch.setattr(gemini_client, "get_client", lambda: fake_client)
    monkeypatch.setattr(gemini_client.time, "sleep", lambda _: None)

    result = gemini_client.generate_text("prompt", "gemini-3.8-flash")

    assert result == "Generated plan"
    assert models.calls == 2