from fastapi.testclient import TestClient


def test_kb_health(client: TestClient):
    response = client.get("/api/kb/health")
    assert response.status_code == 200
    assert response.json()["status"] == "KB router OK"


# def test_chat_health(client: TestClient):
#     response = client.get("/api/chat/health")
#     # If you don’t have a chat health endpoint, adjust/remove
#     assert response.status_code == 200
#     assert "OK" in response.json()["status"]
