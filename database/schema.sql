-- Phase 1 schema for Resume-Job Match Analyzer
-- Target database: PostgreSQL

CREATE TABLE IF NOT EXISTS resumes (
    id BIGSERIAL PRIMARY KEY,
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    extracted_text TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS job_descriptions (
    id BIGSERIAL PRIMARY KEY,
    company_name VARCHAR(255),
    role_title VARCHAR(255) NOT NULL,
    job_text TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS analyses (
    id BIGSERIAL PRIMARY KEY,
    resume_id BIGINT NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    job_description_id BIGINT NOT NULL REFERENCES job_descriptions(id) ON DELETE CASCADE,
    match_score DOUBLE PRECISION NOT NULL,
    summary TEXT NOT NULL,
    overlapping_skills JSONB NOT NULL,
    missing_skills JSONB NOT NULL,
    suggestions JSONB NOT NULL,
    analysis_metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_job_descriptions_role_title
    ON job_descriptions (role_title);
CREATE INDEX IF NOT EXISTS idx_analyses_created_at
    ON analyses (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_analyses_resume_id
    ON analyses (resume_id);
CREATE INDEX IF NOT EXISTS idx_analyses_job_description_id
    ON analyses (job_description_id);

