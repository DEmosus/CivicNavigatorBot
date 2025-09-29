from fastapi.testclient import TestClient

def test_invalid_login(client: TestClient):
    # Try logging in with a non‑existent user
    response = client.post("/api/auth/login", json={"email": "ghost@example.com", "password": "WrongPass!1"})
    assert response.status_code == 401
    assert "detail" in response.json()


def test_check_status_nonexistent_incident(client: TestClient):
    response = client.get("/api/incidents/FAKE123/status")
    assert response.status_code == 404
    assert response.json()["detail"] == "Unknown incident ID"


def test_chat_flow_aborted(client: TestClient):
    r1 = client.post("/api/chat/message", json={"message": "I want to report an incident"})
    assert r1.status_code == 200
    session_id = r1.json()["session_id"]

    r2 = client.post("/api/chat/message", json={"message": "Never mind", "session_id": session_id})
    assert r2.status_code == 200
    reply = r2.json()["reply"].lower()
    assert "chat" in reply and "form" in reply

