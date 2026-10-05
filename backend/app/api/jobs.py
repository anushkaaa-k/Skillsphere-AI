from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from app.database import get_db
from app.models import DimJob, FactJobSkill, DimSkill, SavedJob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

router = APIRouter(prefix="/jobs", tags=["Job Explorer"])

@router.get("/search")
def search_jobs(
    query: Optional[str] = None,
    category: Optional[str] = None,
    city: Optional[str] = None,
    exp_level: Optional[str] = None,
    skill: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Search and filter job postings with pagination."""
    q = db.query(DimJob)

    if query:
        q = q.filter(
            (DimJob.job_title.ilike(f"%{query}%")) | 
            (DimJob.description.ilike(f"%{query}%")) | 
            (DimJob.company_name.ilike(f"%{query}%"))
        )
    if category:
        q = q.filter(DimJob.job_category == category)
    if exp_level:
        q = q.filter(DimJob.experience_level == exp_level)

    total_count = q.count()
    jobs = q.order_by(desc(DimJob.job_key)).offset(offset).limit(limit).all()

    results = []
    for j in jobs:
        extracted_skills = [f.skill.canonical_skill_name for f in j.facts if f.skill]
        results.append({
            "job_key": j.job_key,
            "source_job_id": j.source_job_id,
            "job_title": j.job_title,
            "job_category": j.job_category,
            "company_name": j.facts[0].company.company_name if j.facts else "TechCorp",
            "city": j.facts[0].location.city if j.facts else "Remote",
            "country": j.facts[0].location.country if j.facts else "Global",
            "experience_level": j.experience_level,
            "employment_type": j.employment_type,
            "min_salary": j.min_salary,
            "max_salary": j.max_salary,
            "extracted_skills": extracted_skills,
            "description": j.description
        })

    return {"total": total_count, "items": results}

@router.get("/{job_key}")
def get_job_detail(job_key: int, db: Session = Depends(get_db)):
    """Fetch detail of a single job posting including similar job recommendations via TF-IDF cosine similarity."""
    job = db.query(DimJob).filter(DimJob.job_key == job_key).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found.")

    extracted_skills = [f.skill.canonical_skill_name for f in job.facts if f.skill]
    company = job.facts[0].company.company_name if job.facts else "TechCorp"
    city = job.facts[0].location.city if job.facts else "Remote"

    # Compute similar jobs using TF-IDF cosine similarity over description + skills
    all_jobs = db.query(DimJob).limit(200).all()
    texts = [f"{j.job_title} {j.description or ''}" for j in all_jobs]
    target_idx = 0
    for idx, j in enumerate(all_jobs):
        if j.job_key == job_key:
            target_idx = idx
            break

    similar_jobs = []
    if len(all_jobs) > 1:
        vectorizer = TfidfVectorizer(stop_words="english", max_features=300)
        tfidf_matrix = vectorizer.fit_transform(texts)
        sim_scores = cosine_similarity(tfidf_matrix[target_idx:target_idx+1], tfidf_matrix).flatten()
        top_indices = sim_scores.argsort()[::-1][1:6]

        for i in top_indices:
            sj = all_jobs[i]
            similar_jobs.append({
                "job_key": sj.job_key,
                "job_title": sj.job_title,
                "job_category": sj.job_category,
                "similarity_score": round(float(sim_scores[i]), 3)
            })

    return {
        "job_key": job.job_key,
        "source_job_id": job.source_job_id,
        "job_title": job.job_title,
        "job_category": job.job_category,
        "company_name": company,
        "city": city,
        "experience_level": job.experience_level,
        "employment_type": job.employment_type,
        "min_salary": job.min_salary,
        "max_salary": job.max_salary,
        "description": job.description,
        "extracted_skills": extracted_skills,
        "similar_jobs": similar_jobs
    }
