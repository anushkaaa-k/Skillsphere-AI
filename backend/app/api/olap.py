from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import OlapQueryRequest
from app.services.olap_service import execute_olap_query

router = APIRouter(prefix="/olap", tags=["Warehouse Explorer OLAP"])

@router.post("/query")
def run_olap_operation(
    req: OlapQueryRequest,
    db: Session = Depends(get_db)
):
    """Execute real SQL OLAP queries: Roll-up, Drill-down, Slice, Dice, and Pivot."""
    valid_ops = ["rollup", "drilldown", "slice", "dice", "pivot"]
    if req.operation_type not in valid_ops:
        raise HTTPException(status_code=400, detail=f"Invalid OLAP operation. Must be one of {valid_ops}")

    return execute_olap_query(
        db,
        operation_type=req.operation_type,
        category=req.category,
        job_title=req.job_title,
        skill_name=req.skill_name,
        location_city=req.location_city,
        year=req.year,
        limit=req.limit
    )
