from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db, engine, Base
from app.services.taxonomy import get_taxonomy_summary
from app.services.etl_service import run_etl_pipeline
from app.models import DimJob, DimSkill, FactJobSkill

router = APIRouter(prefix="/settings", tags=["Settings"])

@router.get("/info")
def get_system_settings(db: Session = Depends(get_db)):
    """Fetch database status, system version, and taxonomy summary."""
    job_count = db.query(DimJob).count()
    skill_count = db.query(DimSkill).count()
    fact_count = db.query(FactJobSkill).count()

    taxonomy_info = get_taxonomy_summary()

    return {
        "app_name": "SkillSphere AI",
        "version": "1.0.0 (DWM Mini-Project Academic Edition)",
        "database_type": "PostgreSQL Compatible (SQLite active engine)",
        "warehouse_status": "ONLINE" if fact_count > 0 else "EMPTY",
        "total_jobs_stored": job_count,
        "total_skills_mapped": skill_count,
        "total_facts_recorded": fact_count,
        "taxonomy_skills_count": taxonomy_info["total_skills"],
        "taxonomy_categories": list(taxonomy_info["categories"].keys())
    }

@router.post("/reseed")
def reseed_database(db: Session = Depends(get_db)):
    """Reset and re-run ETL pipeline from raw dataset."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    audit_log = run_etl_pipeline(db)
    return {
        "message": "Database reseeded successfully!",
        "run_id": audit_log.run_id,
        "accepted_rows": audit_log.accepted_rows
    }
