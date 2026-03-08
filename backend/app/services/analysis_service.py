import re
from dataclasses import dataclass

from app.core.config import settings
from app.schemas.analysis import AnalysisResult
from app.services.ai_suggestions import AISuggestionError, generate_gemini_suggestions

SKILL_KEYWORDS = {
    "python",
    "java",
    "javascript",
    "typescript",
    "go",
    "sql",
    "postgresql",
    "mysql",
    "mongodb",
    "redis",
    "fastapi",
    "django",
    "flask",
    "node.js",
    "next.js",
    "react",
    "vue",
    "angular",
    "tailwind",
    "docker",
    "kubernetes",
    "aws",
    "gcp",
    "azure",
    "git",
    "github",
    "ci/cd",
    "pytest",
    "unit testing",
    "rest api",
    "graphql",
    "machine learning",
    "nlp",
    "data analysis",
    "pandas",
    "numpy",
    "scikit-learn",
    "communication",
    "leadership",
    "stakeholder management",
    "agile",
    "scrum",
}

SKILL_ALIASES = {
    "node": "node.js",
    "nextjs": "next.js",
    "postgres": "postgresql",
    "ml": "machine learning",
    "nlp": "nlp",
    "unit test": "unit testing",
    "testing": "unit testing",
}


@dataclass
class SkillSignals:
    resume_skills: set[str]
    job_skills: set[str]


def analyze_resume_job_match(
    resume_text: str,
    job_text: str,
    role_title: str,
    company_name: str | None = None,
) -> AnalysisResult:
    signals = _extract_skill_signals(resume_text=resume_text, job_text=job_text)

    overlapping_skills = sorted(signals.resume_skills & signals.job_skills)
    missing_skills = sorted(signals.job_skills - signals.resume_skills)
    match_score = _calculate_match_score(overlapping_skills, signals.job_skills)
    summary = _build_summary(
        role_title=role_title,
        company_name=company_name,
        score=match_score,
        overlap_count=len(overlapping_skills),
        required_count=len(signals.job_skills),
    )
    suggestions, suggestions_source, ai_error = _build_suggestions(
        missing_skills=missing_skills,
        role_title=role_title,
        company_name=company_name,
    )

    metadata = {
        "resume_skill_count": len(signals.resume_skills),
        "job_skill_count": len(signals.job_skills),
        "overlap_count": len(overlapping_skills),
        "scoring_version": "phase1-keyword-overlap-v1",
        "suggestions_source": suggestions_source,
    }
    if suggestions_source == "ai":
        metadata["ai_model"] = settings.ai_model
    if ai_error:
        metadata["ai_error"] = ai_error

    return AnalysisResult(
        match_score=match_score,
        summary=summary,
        overlapping_skills=overlapping_skills,
        missing_skills=missing_skills,
        suggestions=suggestions,
        analysis_metadata=metadata,
    )


def _extract_skill_signals(resume_text: str, job_text: str) -> SkillSignals:
    resume_skills = _extract_skills(resume_text)
    job_skills = _extract_skills(job_text)
    return SkillSignals(resume_skills=resume_skills, job_skills=job_skills)


def _extract_skills(text: str) -> set[str]:
    normalized = _normalize_text(text)
    found_skills: set[str] = set()

    for skill in SKILL_KEYWORDS:
        if skill in normalized:
            found_skills.add(skill)

    for alias, canonical in SKILL_ALIASES.items():
        if re.search(rf"\b{re.escape(alias)}\b", normalized):
            found_skills.add(canonical)

    return found_skills


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _calculate_match_score(overlap: list[str], job_skills: set[str]) -> float:
    if not job_skills:
        return 50.0
    score = (len(overlap) / len(job_skills)) * 100
    return round(min(score, 100.0), 2)


def _build_summary(
    role_title: str,
    company_name: str | None,
    score: float,
    overlap_count: int,
    required_count: int,
) -> str:
    company_segment = f" at {company_name}" if company_name else ""
    return (
        f"Estimated match for {role_title}{company_segment}: {score:.2f}%. "
        f"Detected {overlap_count} overlapping skills out of {required_count} "
        "skill signals in the job description."
    )


def _build_suggestions(
    *,
    missing_skills: list[str],
    role_title: str,
    company_name: str | None,
) -> tuple[list[str], str, str | None]:
    # No gap detected: keep deterministic output and skip AI call entirely.
    if not missing_skills:
        return (_build_rule_based_suggestions(missing_skills), "rule_based", None)

    # AI suggestion path is optional and guarded by env configuration.
    if settings.ai_suggestions_enabled and settings.gemini_api_key:
        try:
            ai_suggestions = generate_gemini_suggestions(
                missing_skills=missing_skills,
                role_title=role_title,
                company_name=company_name,
                api_key=settings.gemini_api_key,
                model=settings.ai_model,
                timeout_seconds=settings.ai_timeout_seconds,
            )
            if ai_suggestions:
                return (ai_suggestions, "ai", None)
        except AISuggestionError as exc:
            return (
                _build_rule_based_suggestions(missing_skills),
                "rule_based_fallback",
                str(exc),
            )

    if not settings.ai_suggestions_enabled:
        return (_build_rule_based_suggestions(missing_skills), "rule_based_ai_disabled", None)

    return (_build_rule_based_suggestions(missing_skills), "rule_based_no_api_key", None)


def _build_rule_based_suggestions(missing_skills: list[str]) -> list[str]:
    if not missing_skills:
        return [
            "Your resume already covers the key detected skills. "
            "Strengthen impact by adding quantified outcomes for recent projects."
        ]

    focus_skills = missing_skills[:5]
    suggestions = [
        f"Add evidence for {skill} with a project bullet and measurable result."
        for skill in focus_skills
    ]
    suggestions.append(
        "Customize the resume summary so it mirrors the role requirements and keywords."
    )
    return suggestions
