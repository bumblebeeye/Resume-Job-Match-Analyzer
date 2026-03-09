from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


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
