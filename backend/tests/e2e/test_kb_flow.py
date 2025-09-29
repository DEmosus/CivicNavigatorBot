from fastapi.testclient import TestClient


def test_kb_search_no_results(client: TestClient):
    response = client.get("/api/kb/search?q=nonexistent")
    assert response.status_code == 404
    assert response.json()["detail"] == "No KB articles found"


def test_kb_index_invalid_payload(client: TestClient):
    # Missing required fields
    payload = {"question": "Incomplete entry"}
    response = client.post("/api/kb/index", json=payload)
    assert response.status_code == 422  # validation error
