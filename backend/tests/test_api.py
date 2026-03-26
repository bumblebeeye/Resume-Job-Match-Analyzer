import app.services.analysis_service as analysis_service_module
from app.services.ai_suggestions import AISuggestionError
from fastapi.testclient import TestClient


def _build_analyze_payload() -> tuple[dict[str, str], dict[str, tuple[str, bytes, str]]]:
    payload = {
        "role_title": "AI Engineer",
        "company_name": "Acme",
        "job_description": "Python FastAPI AWS Bedrock Terraform Observability",
    }
    files = {
        "resume_file": (
            "resume.txt",
            b"Built APIs in Python and FastAPI on AWS.",
            "text/plain",
        )
    }
    return payload, files


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


def test_analyze_uses_rule_based_metadata_when_ai_disabled(client: TestClient) -> None:
    payload, files = _build_analyze_payload()

    response = client.post("/api/analyze", data=payload, files=files)

    assert response.status_code == 201
    analysis = response.json()

    assert analysis["analysis_metadata"]["suggestions_source"] == "rule_based_ai_disabled"
    assert "ai_model" not in analysis["analysis_metadata"]
    assert "ai_error" not in analysis["analysis_metadata"]
    assert analysis["missing_skills"] == ["llm", "observability", "terraform"]


def test_analyze_uses_rule_based_metadata_when_ai_key_missing(client: TestClient) -> None:
    payload, files = _build_analyze_payload()

    from app.core.config import settings

    settings.ai_suggestions_enabled = True
    settings.gemini_api_key = None

    response = client.post("/api/analyze", data=payload, files=files)

    assert response.status_code == 201
    analysis = response.json()

    assert analysis["analysis_metadata"]["suggestions_source"] == "rule_based_no_api_key"
    assert "ai_model" not in analysis["analysis_metadata"]
    assert "ai_error" not in analysis["analysis_metadata"]


def test_analyze_records_ai_fallback_error(
    client: TestClient,
    monkeypatch,
) -> None:
    payload, files = _build_analyze_payload()

    from app.core.config import settings

    settings.ai_suggestions_enabled = True
    settings.gemini_api_key = "test-key"

    def raise_timeout(**_kwargs) -> list[str]:
        raise AISuggestionError("simulated timeout")

    monkeypatch.setattr(
        analysis_service_module,
        "generate_gemini_suggestions",
        raise_timeout,
    )

    response = client.post("/api/analyze", data=payload, files=files)

    assert response.status_code == 201
    analysis = response.json()

    assert analysis["analysis_metadata"]["suggestions_source"] == "rule_based_fallback"
    assert analysis["analysis_metadata"]["ai_error"] == "simulated timeout"
    assert "ai_model" not in analysis["analysis_metadata"]
    assert analysis["suggestions"][0] == "Add evidence for llm with a project bullet and measurable result."
