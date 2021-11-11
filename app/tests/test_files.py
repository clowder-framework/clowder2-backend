from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

user = {"name": "test@test.org", "password": "not_a_password"}


def test_create():
    response = client.post("/users", json=user)
    assert response.status_code == 200
    response = client.post("/login", json=user)
    assert response.status_code == 200
    token = response.json().get("token")
    assert token is not None
    headers = {"Authorization": "Bearer " + token}
    # https://stackoverflow.com/questions/60783222/how-to-test-a-fastapi-api-endpoint-that-consumes-images
    # with open("./data/cat.jpg", "wb") as f:
    #     response = client.post(
    #         "/files", headers=headers, files={"file": ("filename", f, "image/jpeg")}
    #     )
    response = client.post(
        "/files",
        files={"file": ("filename", open("./data/cat.jpg", "rb"), "image/jpeg")},
        headers=headers,
    )

    assert response.json().get("id") is not None
    assert response.status_code == 200
