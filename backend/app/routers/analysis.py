from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models.analysis import Analysis
from app.models.job_description import JobDescription
from app.models.resume import Resume
from app.schemas.analysis import AnalysisDetailResponse, AnalysisListItem
from app.services.analysis_service import analyze_resume_job_match
from app.services.resume_parser import ResumeParserError, extract_resume_text, save_resume_file

router = APIRouter()


@router.post("/analyze", response_model=AnalysisDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_analysis(
    resume_file: UploadFile = File(...),
    role_title: str = Form(...),
    company_name: str | None = Form(default=None),
    job_description: str = Form(...),
    db: Session = Depends(get_db),
) -> AnalysisDetailResponse:
    if not role_title.strip():
        raise HTTPException(status_code=400, detail="role_title is required.")
    if not job_description.strip():
        raise HTTPException(status_code=400, detail="job_description is required.")

    try:
        file_path, stored_filename, file_bytes = await save_resume_file(resume_file)
        extracted_resume_text = extract_resume_text(
            filename=resume_file.filename or stored_filename,
            file_bytes=file_bytes,
        )
    except ResumeParserError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    resume = Resume(
        original_filename=resume_file.filename or stored_filename,
        stored_filename=stored_filename,
        file_path=file_path,
        extracted_text=extracted_resume_text,
    )
    job_record = JobDescription(
        company_name=company_name.strip() if company_name else None,
        role_title=role_title.strip(),
        job_text=job_description.strip(),
    )

    db.add(resume)
    db.add(job_record)
    db.flush()

    analysis_result = analyze_resume_job_match(
        resume_text=extracted_resume_text,
        job_text=job_record.job_text,
        role_title=job_record.role_title,
        company_name=job_record.company_name,
    )

    analysis = Analysis(
        resume_id=resume.id,
        job_description_id=job_record.id,
        match_score=analysis_result.match_score,
        summary=analysis_result.summary,
        overlapping_skills=analysis_result.overlapping_skills,
        missing_skills=analysis_result.missing_skills,
        suggestions=analysis_result.suggestions,
        analysis_metadata=analysis_result.analysis_metadata,
    )

    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    db.refresh(resume)
    db.refresh(job_record)

    return _build_detail_response(analysis=analysis, resume=resume, job_record=job_record)


@router.get("/analyses", response_model=list[AnalysisListItem])
def list_analyses(db: Session = Depends(get_db)) -> list[AnalysisListItem]:
    query = (
        select(Analysis, JobDescription)
        .join(JobDescription, Analysis.job_description_id == JobDescription.id)
        .order_by(Analysis.created_at.desc())
    )
    rows = db.execute(query).all()
    return [
        AnalysisListItem(
            id=analysis.id,
            role_title=job.role_title,
            company_name=job.company_name,
            match_score=analysis.match_score,
            created_at=analysis.created_at,
        )
        for analysis, job in rows
    ]


@router.get("/analyses/{analysis_id}", response_model=AnalysisDetailResponse)
def get_analysis(analysis_id: int, db: Session = Depends(get_db)) -> AnalysisDetailResponse:
    query = (
        select(Analysis)
        .where(Analysis.id == analysis_id)
        .options(joinedload(Analysis.resume), joinedload(Analysis.job_description))
    )
    analysis = db.scalar(query)
    if not analysis or not analysis.resume or not analysis.job_description:
        raise HTTPException(status_code=404, detail="Analysis not found.")

    return _build_detail_response(
        analysis=analysis,
        resume=analysis.resume,
        job_record=analysis.job_description,
    )


def _build_detail_response(
    analysis: Analysis,
    resume: Resume,
    job_record: JobDescription,
) -> AnalysisDetailResponse:
    return AnalysisDetailResponse(
        id=analysis.id,
        resume_id=analysis.resume_id,
        job_description_id=analysis.job_description_id,
        resume_filename=resume.original_filename,
        role_title=job_record.role_title,
        company_name=job_record.company_name,
        match_score=analysis.match_score,
        summary=analysis.summary,
        overlapping_skills=analysis.overlapping_skills,
        missing_skills=analysis.missing_skills,
        suggestions=analysis.suggestions,
        analysis_metadata=analysis.analysis_metadata,
        created_at=analysis.created_at,
    )

