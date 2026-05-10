from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Bem-vindo à API de Meetups! Acesse /docs para testar."}

def test_delete_event_without_token():
    response = client.delete("/events/1")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}