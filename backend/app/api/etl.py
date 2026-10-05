from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models import EtlAuditLog, StagingJobPosting
from app.services.etl_service import run_etl_pipeline

router = APIRouter(prefix="/etl", tags=["Data Pipeline ETL"])

@router.post("/run")
def trigger_etl_pipeline(db: Session = Depends(get_db)):
    """Trigger execution of the ETL pipeline."""
    try:
        audit_log = run_etl_pipeline(db)
        return {
            "message": "ETL Pipeline completed successfully!",
            "run_id": audit_log.run_id,
            "data_quality_score": audit_log.data_quality_score,
            "accepted_rows": audit_log.accepted_rows,
            "status": audit_log.status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ETL pipeline failed: {str(e)}")

@router.get("/logs")
def get_etl_audit_logs(db: Session = Depends(get_db)):
    """Fetch history of ETL pipeline executions and quality scores."""
    logs = db.query(EtlAuditLog).order_by(desc(EtlAuditLog.start_time)).all()
    return logs

@router.get("/staging-summary")
def get_staging_summary(db: Session = Depends(get_db)):
    """Fetch staging area record counts and data quality summary."""
    total_staging = db.query(StagingJobPosting).count()
    valid_staging = db.query(StagingJobPosting).filter(StagingJobPosting.is_valid == True).count()
    
    latest_run = db.query(EtlAuditLog).order_by(desc(EtlAuditLog.start_time)).first()

    return {
        "total_staging_records": total_staging,
        "valid_records": valid_staging,
        "invalid_records": total_staging - valid_staging,
        "latest_quality_score": latest_run.data_quality_score if latest_run else 100.0,
        "latest_run_id": latest_run.run_id if latest_run else "N/A"
    }
