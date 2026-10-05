from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional, List
from app.database import get_db
from app.models import DimJob, DimSkill, DimCompany, DimLocation, FactJobSkill
from app.schemas import RoleComparisonRequest

router = APIRouter(prefix="/market", tags=["Market Intelligence"])

@router.get("/skills-demand")
def get_skills_demand_matrix(
    category: Optional[str] = None,
    city: Optional[str] = None,
    exp_level: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Fetch skill demand list with average salary and job posting volume."""
    q = (
        db.query(
            DimSkill.canonical_skill_name,
            DimSkill.skill_category,
            func.count(func.distinct(DimJob.job_key)).label("posting_count"),
            func.round(func.avg((DimJob.min_salary + DimJob.max_salary) / 2), 2).label("avg_salary")
        )
        .join(FactJobSkill, DimSkill.skill_key == FactJobSkill.skill_key)
        .join(DimJob, FactJobSkill.job_key == DimJob.job_key)
        .join(DimLocation, FactJobSkill.location_key == DimLocation.location_key)
    )

    if category:
        q = q.filter(DimJob.job_category == category)
    if city:
        q = q.filter(DimLocation.city == city)
    if exp_level:
        q = q.filter(DimJob.experience_level == exp_level)

    results = q.group_by(DimSkill.canonical_skill_name, DimSkill.skill_category)\
               .order_by(desc("posting_count"))\
               .limit(50)\
               .all()

    return [
        {
            "skill": r.canonical_skill_name,
            "category": r.skill_category,
            "posting_count": r.posting_count,
            "avg_salary": float(r.avg_salary or 0)
        }
        for r in results
    ]

@router.post("/compare-roles")
def compare_job_roles(
    req: RoleComparisonRequest,
    db: Session = Depends(get_db)
):
    """Compare two job roles across required skills, volume, and salary statistics."""
    def get_role_data(role_title: str):
        jobs = db.query(DimJob).filter(
            (DimJob.job_title.ilike(f"%{role_title}%")) | (DimJob.job_category.ilike(f"%{role_title}%"))
        ).all()
        job_keys = [j.job_key for j in jobs]
        if not job_keys:
            return {"role": role_title, "posting_volume": 0, "avg_min_sal": 0, "avg_max_sal": 0, "top_skills": []}

        salaries = [(j.min_salary or 0, j.max_salary or 0) for j in jobs]
        avg_min = sum(s[0] for s in salaries) / len(salaries)
        avg_max = sum(s[1] for s in salaries) / len(salaries)

        skills = (
            db.query(
                DimSkill.canonical_skill_name,
                func.count(FactJobSkill.job_skill_fact_key).label("count")
            )
            .join(FactJobSkill, DimSkill.skill_key == FactJobSkill.skill_key)
            .filter(FactJobSkill.job_key.in_(job_keys))
            .group_by(DimSkill.canonical_skill_name)
            .order_by(desc("count"))
            .limit(10)
            .all()
        )

        return {
            "role": role_title,
            "posting_volume": len(jobs),
            "avg_min_sal": round(avg_min, 2),
            "avg_max_sal": round(avg_max, 2),
            "top_skills": [{"skill": s.canonical_skill_name, "count": s.count} for s in skills]
        }

    return {
        "role_1": get_role_data(req.role_1),
        "role_2": get_role_data(req.role_2)
    }
