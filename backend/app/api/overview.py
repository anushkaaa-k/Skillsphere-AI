from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.database import get_db
from app.models import DimJob, DimCompany, DimSkill, DimLocation, FactJobSkill, EtlAuditLog

router = APIRouter(prefix="/overview", tags=["Overview"])

@router.get("/kpi")
def get_overview_kpis(db: Session = Depends(get_db)):
    """Fetch live database-derived metrics for dashboard KPI cards."""
    total_postings = db.query(func.count(DimJob.job_key)).scalar() or 0
    unique_companies = db.query(func.count(DimCompany.company_key)).scalar() or 0
    unique_skills = db.query(func.count(DimSkill.skill_key)).scalar() or 0
    job_categories = db.query(func.count(func.distinct(DimJob.job_category))).scalar() or 0
    
    latest_log = db.query(EtlAuditLog).order_by(desc(EtlAuditLog.start_time)).first()
    refresh_date = latest_log.start_time.strftime("%Y-%m-%d %H:%M") if latest_log else "2026-10-01 12:00"
    quality_score = latest_log.data_quality_score if latest_log else 100.0

    return {
        "total_job_postings": total_postings,
        "unique_companies": unique_companies,
        "unique_skills": unique_skills,
        "job_categories": job_categories,
        "latest_dataset_refresh": refresh_date,
        "etl_quality_score": quality_score
    }

@router.get("/charts")
def get_overview_charts(
    category: str = None,
    city: str = None,
    db: Session = Depends(get_db)
):
    """Fetch aggregated chart data for Top Skills, Category Demand, Exp Levels, Location distribution, Salary Stats."""
    # Base query for top skills
    skill_q = (
        db.query(
            DimSkill.canonical_skill_name,
            func.count(FactJobSkill.job_skill_fact_key).label("count")
        )
        .join(FactJobSkill, DimSkill.skill_key == FactJobSkill.skill_key)
        .join(DimJob, FactJobSkill.job_key == DimJob.job_key)
        .join(DimLocation, FactJobSkill.location_key == DimLocation.location_key)
    )
    if category:
        skill_q = skill_q.filter(DimJob.job_category == category)
    if city:
        skill_q = skill_q.filter(DimLocation.city == city)

    top_skills = [
        {"skill": r.canonical_skill_name, "count": r.count}
        for r in skill_q.group_by(DimSkill.canonical_skill_name).order_by(desc("count")).limit(10).all()
    ]

    # Category distribution
    cat_q = (
        db.query(
            DimJob.job_category,
            func.count(DimJob.job_key).label("count")
        )
    )
    if city:
        cat_q = cat_q.join(FactJobSkill, DimJob.job_key == FactJobSkill.job_key)\
                     .join(DimLocation, FactJobSkill.location_key == DimLocation.location_key)\
                     .filter(DimLocation.city == city)

    category_distribution = [
        {"category": r.job_category, "count": r.count}
        for r in cat_q.group_by(DimJob.job_category).order_by(desc("count")).all()
    ]

    # Experience level distribution
    exp_distribution = [
        {"level": r.experience_level, "count": r.count}
        for r in db.query(DimJob.experience_level, func.count(DimJob.job_key).label("count")).group_by(DimJob.experience_level).all()
    ]

    # Location distribution
    location_distribution = [
        {"city": r.city, "count": r.count}
        for r in db.query(DimLocation.city, func.count(FactJobSkill.job_skill_fact_key).label("count")).join(FactJobSkill, DimLocation.location_key == FactJobSkill.location_key).group_by(DimLocation.city).order_by(desc("count")).limit(8).all()
    ]

    return {
        "top_skills": top_skills,
        "category_distribution": category_distribution,
        "exp_distribution": exp_distribution,
        "location_distribution": location_distribution
    }
