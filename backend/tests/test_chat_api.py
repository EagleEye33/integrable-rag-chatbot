from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services import chat_service


client = TestClient(app)


def test_chat_returns_fallback_without_index():
    chat_service._load_index.cache_clear()
    response = client.post("/api/chat", json={"question": "What are your working hours?"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["grounded"] is False
    assert "could not find" in payload["answer"].lower()


def test_chat_returns_sources_when_retrieval_matches(monkeypatch):
    class FakeIndex:
        def search(self, query, top_k, min_score):  # noqa: ARG002
            return [type("M", (), {"source": "about-org", "text": "We offer 24x7 support.", "score": 0.95})()]

    def fake_load_index():
        return FakeIndex()

    monkeypatch.setattr(chat_service, "_load_index", fake_load_index)

    response = client.post("/api/chat", json={"question": "Do you provide support?"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["grounded"] is False
    assert payload["sources"][0]["source"] == "about-org"
    assert "could not find" in payload["answer"].lower()
