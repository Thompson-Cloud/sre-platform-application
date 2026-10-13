from app import app


def test_home():
    client = app.test_client()
    response = client.get("/")

    assert response.status_code == 200
    assert response.json["service"] == "sre-platform-api"


def test_health():
    client = app.test_client()
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json["status"] == "healthy"


def test_ready():
    client = app.test_client()
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json["status"] == "ready"


def test_work():
    client = app.test_client()
    response = client.get("/api/work")

    assert response.status_code == 200
    assert response.json["status"] == "success"


def test_metrics():
    client = app.test_client()

    client.get("/api/work")
    response = client.get("/metrics")

    assert response.status_code == 200
    assert b"http_requests_total" in response.data
    assert b"http_request_duration_seconds" in response.data


def test_not_found():
    client = app.test_client()
    response = client.get("/does-not-exist")

    assert response.status_code == 404