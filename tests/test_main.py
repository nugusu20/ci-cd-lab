from app.main import app


def test_health() -> None:
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_ready() -> None:
    client = app.test_client()
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ready"}


def test_version() -> None:
    client = app.test_client()
    response = client.get("/version")
    assert response.status_code == 200

    payload = response.get_json()
    assert payload["app"] == "ci-cd-lab"
    assert "version" in payload
    assert "image_tag" in payload


def test_create_and_get_task() -> None:
    client = app.test_client()

    created = client.post(
        "/tasks",
        json={"title": "Learn Jenkins", "description": "pipeline practice"},
    )
    assert created.status_code == 201

    created_payload = created.get_json()
    task_id = created_payload["id"]

    fetched = client.get(f"/tasks/{task_id}")
    assert fetched.status_code == 200
    assert fetched.get_json()["title"] == "Learn Jenkins"
