from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AnalysisResult(BaseModel):
    match_score: float
    summary: str
    overlapping_skills: list[str]
    missing_skills: list[str]
    suggestions: list[str]
    analysis_metadata: dict[str, Any]


class AnalysisListItem(BaseModel):
    id: int
    role_title: str
    company_name: str | None
    match_score: float
    created_at: datetime


class AnalysisDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    resume_id: int
    job_description_id: int
    resume_filename: str
    role_title: str
    company_name: str | None
    match_score: float
    summary: str
    overlapping_skills: list[str]
    missing_skills: list[str]
    suggestions: list[str]
    analysis_metadata: dict[str, Any]
    created_at: datetime

