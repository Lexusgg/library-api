from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_borrow_book_limit():
    response = client.post("/borrow/", json={"book_id": 1, "reader_id": 1})
    assert response.status_code == 400  # Ожидаем ошибку, если лимит превышен