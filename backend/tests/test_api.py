from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    response = client.get("/health", headers={"X-Request-ID": "health-check-123"})

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["X-Request-ID"] == "health-check-123"


def test_analyze_and_history_flow(client: TestClient) -> None:
    payload = {
        "role_title": "Backend Engineer",
        "company_name": "Acme",
        "job_description": "Python FastAPI SQL Docker Kubernetes",
    }
    files = {
        "resume_file": (
            "resume.txt",
            b"Built APIs in Python and FastAPI with SQL and Docker.",
            "text/plain",
        )
    }

    analyze_response = client.post("/api/analyze", data=payload, files=files)
    assert analyze_response.status_code == 201

    analysis = analyze_response.json()
    assert analysis["role_title"] == "Backend Engineer"
    assert analysis["company_name"] == "Acme"
    assert isinstance(analysis["match_score"], float)
    assert isinstance(analysis["overlapping_skills"], list)
    assert isinstance(analysis["missing_skills"], list)
    assert isinstance(analysis["suggestions"], list)
    assert analysis["analysis_metadata"]["suggestions_source"].startswith("rule_based")

    history_response = client.get("/api/analyses")
    assert history_response.status_code == 200
    history_items = history_response.json()
    assert len(history_items) == 1
    assert history_items[0]["id"] == analysis["id"]

    detail_response = client.get(f"/api/analyses/{analysis['id']}")
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["id"] == analysis["id"]
    assert detail["resume_filename"] == "resume.txt"


def test_get_analysis_not_found(client: TestClient) -> None:
    response = client.get("/api/analyses/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Analysis not found."
    assert response.json()["error_code"] == "not_found"
    assert response.json()["request_id"] == response.headers["X-Request-ID"]


def test_analyze_rejects_blank_role_title(client: TestClient) -> None:
    payload = {
        "role_title": "   ",
        "company_name": "Acme",
        "job_description": "Python FastAPI SQL",
    }
    files = {
        "resume_file": (
            "resume.txt",
            b"Python FastAPI SQL",
            "text/plain",
        )
    }

    response = client.post("/api/analyze", data=payload, files=files)

    assert response.status_code == 400
    assert response.json()["detail"] == "role_title is required."
    assert response.json()["error_code"] == "bad_request"
    assert response.json()["request_id"] == response.headers["X-Request-ID"]


def test_analyze_rejects_unsupported_resume_content_type(client: TestClient) -> None:
    payload = {
        "role_title": "Backend Engineer",
        "company_name": "Acme",
        "job_description": "Python FastAPI SQL",
    }
    files = {
        "resume_file": (
            "resume.pdf",
            b"%PDF-1.4 fake content",
            "text/plain",
        )
    }

    response = client.post("/api/analyze", data=payload, files=files)

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Unsupported content type for .pdf files. Use one of: application/pdf."
    )
    assert response.json()["error_code"] == "bad_request"
    assert response.json()["request_id"] == response.headers["X-Request-ID"]


def test_analyze_rejects_oversized_resume_file(client: TestClient) -> None:
    from app.core.config import settings

    payload = {
        "role_title": "Backend Engineer",
        "company_name": "Acme",
        "job_description": "Python FastAPI SQL",
    }
    files = {
        "resume_file": (
            "resume.txt",
            b"0123456789ABCDEF",
            "text/plain",
        )
    }
    original_limit = settings.max_resume_upload_bytes
    settings.max_resume_upload_bytes = 10

    try:
        response = client.post("/api/analyze", data=payload, files=files)
    finally:
        settings.max_resume_upload_bytes = original_limit

    assert response.status_code == 400
    assert response.json()["detail"] == "Uploaded file exceeds the 10 bytes limit."
    assert response.json()["error_code"] == "bad_request"
    assert response.json()["request_id"] == response.headers["X-Request-ID"]


def test_analyze_validation_errors_use_standardized_error_shape(client: TestClient) -> None:
    response = client.post("/api/analyze", data={})

    assert response.status_code == 422
    assert response.json()["detail"] == "Request validation failed."
    assert response.json()["error_code"] == "validation_error"
    assert response.json()["request_id"] == response.headers["X-Request-ID"]


def test_analyze_rate_limit_rejects_excess_requests(client: TestClient) -> None:
    from app.core.config import settings

    payload = {
        "role_title": "Backend Engineer",
        "company_name": "Acme",
        "job_description": "Python FastAPI SQL Docker Kubernetes",
    }
    files = {
        "resume_file": (
            "resume.txt",
            b"Built APIs in Python and FastAPI with SQL and Docker.",
            "text/plain",
        )
    }
    original_limit = settings.api_rate_limit_requests
    original_window = settings.api_rate_limit_window_seconds
    settings.api_rate_limit_requests = 1
    settings.api_rate_limit_window_seconds = 60

    try:
        first_response = client.post("/api/analyze", data=payload, files=files)
        second_response = client.post("/api/analyze", data=payload, files=files)
    finally:
        settings.api_rate_limit_requests = original_limit
        settings.api_rate_limit_window_seconds = original_window

    assert first_response.status_code == 201
    assert second_response.status_code == 429
    assert second_response.json()["detail"] == "Rate limit exceeded. Try again in 60 seconds."
    assert second_response.json()["error_code"] == "rate_limit_exceeded"
    assert second_response.json()["request_id"] == second_response.headers["X-Request-ID"]
