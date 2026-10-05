from sqlalchemy.orm import Session
from sqlalchemy import func, desc, select
from app.models import FactJobSkill, DimJob, DimSkill, DimCompany, DimLocation, DimDate
from typing import Dict, List, Optional, Any

def execute_olap_query(
    db: Session,
    operation_type: str, # "rollup", "drilldown", "slice", "dice", "pivot"
    category: Optional[str] = None,
    job_title: Optional[str] = None,
    skill_name: Optional[str] = None,
    location_city: Optional[str] = None,
    year: Optional[int] = None,
    limit: int = 50
) -> Dict[str, Any]:
    """
    Execute real OLAP SQL operations over the FactJobSkill star schema.
    """
    base_query = (
        db.query(
            DimJob.job_category,
            DimJob.job_title,
            DimSkill.canonical_skill_name,
            DimCompany.company_name,
            DimLocation.city,
            DimLocation.country,
            DimDate.year,
            DimDate.month,
            func.count(FactJobSkill.job_skill_fact_key).label("fact_count"),
            func.count(func.distinct(DimJob.job_key)).label("posting_count"),
            func.avg(DimJob.min_salary).label("avg_min_salary"),
            func.avg(DimJob.max_salary).label("avg_max_salary")
        )
        .join(DimJob, FactJobSkill.job_key == DimJob.job_key)
        .join(DimSkill, FactJobSkill.skill_key == DimSkill.skill_key)
        .join(DimCompany, FactJobSkill.company_key == DimCompany.company_key)
        .join(DimLocation, FactJobSkill.location_key == DimLocation.location_key)
        .join(DimDate, FactJobSkill.date_key == DimDate.date_key)
    )

    explanation = ""
    sql_snippet = ""

    if operation_type == "rollup":
        # Roll-Up: Aggregate demand from Month/Category level up to Year/Category level
        explanation = "OLAP Roll-Up: Aggregating monthly job demand into yearly skill demand summaries."
        query = (
            db.query(
                DimDate.year,
                DimJob.job_category,
                DimSkill.canonical_skill_name,
                func.count(func.distinct(DimJob.job_key)).label("posting_count"),
                func.round(func.avg((DimJob.min_salary + DimJob.max_salary) / 2), 2).label("avg_salary")
            )
            .join(FactJobSkill, DimJob.job_key == FactJobSkill.job_key)
            .join(DimSkill, FactJobSkill.skill_key == DimSkill.skill_key)
            .join(DimDate, FactJobSkill.date_key == DimDate.date_key)
        )
        if category:
            query = query.filter(DimJob.job_category == category)
        if year:
            query = query.filter(DimDate.year == year)

        query = query.group_by(DimDate.year, DimJob.job_category, DimSkill.canonical_skill_name)\
                     .order_by(desc("posting_count"))\
                     .limit(limit)

        records = [
            {
                "year": r.year,
                "category": r.job_category,
                "skill": r.canonical_skill_name,
                "posting_count": r.posting_count,
                "avg_salary": float(r.avg_salary or 0)
            }
            for r in query.all()
        ]
        sql_snippet = "SELECT year, job_category, canonical_skill_name, COUNT(DISTINCT job_key) FROM fact_job_skill JOIN dim_job JOIN dim_date GROUP BY year, job_category, canonical_skill_name"

    elif operation_type == "drilldown":
        # Drill-Down: Breakdown from Category -> Job Title -> Specific Skill Requirement
        explanation = f"OLAP Drill-Down: Decomposing broad Category '{category or 'All'}' into granular Job Roles and specific Skill demands."
        query = (
            db.query(
                DimJob.job_category,
                DimJob.job_title,
                DimSkill.canonical_skill_name,
                DimSkill.skill_category,
                func.count(func.distinct(DimJob.job_key)).label("posting_count")
            )
            .join(FactJobSkill, DimJob.job_key == FactJobSkill.job_key)
            .join(DimSkill, FactJobSkill.skill_key == DimSkill.skill_key)
        )
        if category:
            query = query.filter(DimJob.job_category == category)
        if job_title:
            query = query.filter(DimJob.job_title == job_title)

        query = query.group_by(DimJob.job_category, DimJob.job_title, DimSkill.canonical_skill_name, DimSkill.skill_category)\
                     .order_by(desc("posting_count"))\
                     .limit(limit)

        records = [
            {
                "job_category": r.job_category,
                "job_title": r.job_title,
                "skill": r.canonical_skill_name,
                "skill_category": r.skill_category,
                "posting_count": r.posting_count
            }
            for r in query.all()
        ]
        sql_snippet = "SELECT job_category, job_title, canonical_skill_name, COUNT(DISTINCT job_key) FROM fact_job_skill JOIN dim_job JOIN dim_skill GROUP BY job_category, job_title, canonical_skill_name"

    elif operation_type == "slice":
        # Slice: Fix one dimension value (e.g. Category = 'Data Science')
        target_cat = category or "Data Science & Analytics"
        explanation = f"OLAP Slice: Isolating a single dimension slice (Job Category = '{target_cat}')."
        query = (
            db.query(
                DimSkill.canonical_skill_name,
                DimSkill.skill_category,
                func.count(func.distinct(DimJob.job_key)).label("posting_count"),
                func.round(func.avg((DimJob.min_salary + DimJob.max_salary) / 2), 2).label("avg_salary")
            )
            .join(FactJobSkill, DimSkill.skill_key == FactJobSkill.skill_key)
            .join(DimJob, FactJobSkill.job_key == DimJob.job_key)
            .filter(DimJob.job_category == target_cat)
            .group_by(DimSkill.canonical_skill_name, DimSkill.skill_category)
            .order_by(desc("posting_count"))
            .limit(limit)
        )

        records = [
            {
                "skill": r.canonical_skill_name,
                "skill_category": r.skill_category,
                "posting_count": r.posting_count,
                "avg_salary": float(r.avg_salary or 0)
            }
            for r in query.all()
        ]
        sql_snippet = f"SELECT canonical_skill_name, COUNT(DISTINCT job_key) FROM fact_job_skill WHERE job_category = '{target_cat}' GROUP BY canonical_skill_name"

    elif operation_type == "dice":
        # Dice: Multi-dimensional sub-cube filtering (Role + Location + Skill)
        explanation = "OLAP Dice: Filtering across multiple dimensions simultaneously (Category, City Location, and Year)."
        query = (
            db.query(
                DimJob.job_category,
                DimLocation.city,
                DimSkill.canonical_skill_name,
                DimCompany.company_name,
                func.count(func.distinct(DimJob.job_key)).label("posting_count")
            )
            .join(FactJobSkill, DimJob.job_key == FactJobSkill.job_key)
            .join(DimSkill, FactJobSkill.skill_key == FactJobSkill.skill_key)
            .join(DimLocation, FactJobSkill.location_key == DimLocation.location_key)
            .join(DimCompany, FactJobSkill.company_key == DimCompany.company_key)
            .join(DimDate, FactJobSkill.date_key == DimDate.date_key)
        )
        if category:
            query = query.filter(DimJob.job_category == category)
        if location_city:
            query = query.filter(DimLocation.city == location_city)
        if year:
            query = query.filter(DimDate.year == year)

        query = query.group_by(DimJob.job_category, DimLocation.city, DimSkill.canonical_skill_name, DimCompany.company_name)\
                     .order_by(desc("posting_count"))\
                     .limit(limit)

        records = [
            {
                "category": r.job_category,
                "city": r.city,
                "skill": r.canonical_skill_name,
                "company": r.company_name,
                "posting_count": r.posting_count
            }
            for r in query.all()
        ]
        sql_snippet = "SELECT job_category, city, canonical_skill_name, company_name FROM fact_job_skill WHERE ... GROUP BY job_category, city, canonical_skill_name, company_name"

    elif operation_type == "pivot":
        # Pivot: Cross-tabulation comparing top skills across Job Categories
        explanation = "OLAP Pivot: Cross-tabulating Skill Demand across major Job Categories."
        query = (
            db.query(
                DimSkill.canonical_skill_name,
                DimJob.job_category,
                func.count(func.distinct(DimJob.job_key)).label("posting_count")
            )
            .join(FactJobSkill, DimSkill.skill_key == FactJobSkill.skill_key)
            .join(DimJob, FactJobSkill.job_key == DimJob.job_key)
            .group_by(DimSkill.canonical_skill_name, DimJob.job_category)
            .order_by(desc("posting_count"))
            .limit(limit * 2)
        )

        rows = query.all()
        # Pivot into matrix
        skills_set = sorted(list(set(r.canonical_skill_name for r in rows)))
        categories_set = sorted(list(set(r.job_category for r in rows)))

        matrix = {s: {c: 0 for c in categories_set} for s in skills_set}
        for r in rows:
            matrix[r.canonical_skill_name][r.job_category] = r.posting_count

        records = [
            {
                "skill": s,
                **cat_counts
            }
            for s, cat_counts in matrix.items()
        ]
        sql_snippet = "SELECT canonical_skill_name, job_category, COUNT(DISTINCT job_key) FROM fact_job_skill GROUP BY canonical_skill_name, job_category"

    else:
        records = []

    return {
        "operation": operation_type,
        "explanation": explanation,
        "sql_snippet": sql_snippet,
        "record_count": len(records),
        "data": records
    }
