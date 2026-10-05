from fastapi import APIRouter, Depends, Response, HTTPException, Body
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import UserSkillProfile, DimJob, DimSkill, FactJobSkill, EtlAuditLog
from app.services.skill_gap_service import analyze_skill_gap
from app.services.report_service import generate_pdf_skill_gap_report, generate_csv_export
from app.services.olap_service import execute_olap_query
from app.services.mining_service import run_association_mining

router = APIRouter(prefix="/reports", tags=["Reports"])

from typing import Optional

@router.get("/pdf/skill-gap")
def download_pdf_skill_gap_report(
    target_role: Optional[str] = None,
    experience_level: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Generate and download PDF Skill Gap Report dynamically reflecting the active profile."""
    profile = db.query(UserSkillProfile).filter(UserSkillProfile.user_id == "default_user").first()
    active_target_role = target_role if (target_role and target_role.strip()) else (profile.target_role if profile else "Data Scientist")
    active_exp_level = experience_level if (experience_level and experience_level.strip()) else (profile.experience_level if profile else "Mid Level")
    confirmed = profile.confirmed_skills if (profile and profile.confirmed_skills) else []
    learned = profile.learned_skills if (profile and profile.learned_skills) else []

    analysis_data = analyze_skill_gap(
        db,
        confirmed_skills=confirmed,
        target_role=active_target_role,
        experience_level=active_exp_level,
        learned_skills=learned
    )
    pdf_bytes = generate_pdf_skill_gap_report(analysis_data)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=SkillSphere_Skill_Gap_Report_{active_target_role.replace(' ', '_')}.pdf"}
    )

@router.get("/csv/skill-demand")
def download_csv_skill_demand(db: Session = Depends(get_db)):
    """Export skill demand data to CSV."""
    from app.api.market_intelligence import get_skills_demand_matrix
    data = get_skills_demand_matrix(db=db)
    csv_str = generate_csv_export(data, headers=["skill", "category", "posting_count", "avg_salary"])
    
    return Response(
        content=csv_str,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=SkillSphere_Skill_Demand.csv"}
    )

@router.get("/csv/olap")
def download_csv_olap(operation_type: str = "slice", category: str = None, db: Session = Depends(get_db)):
    """Export OLAP query results to CSV."""
    res = execute_olap_query(db, operation_type=operation_type, category=category)
    data = res["data"]
    headers = list(data[0].keys()) if data else ["skill", "posting_count"]
    csv_str = generate_csv_export(data, headers=headers)

    return Response(
        content=csv_str,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=SkillSphere_OLAP_{operation_type}.csv"}
    )

@router.get("/csv/association-rules")
def download_csv_association_rules(db: Session = Depends(get_db)):
    """Export Apriori association rules to CSV."""
    res = run_association_mining(db)
    rules = res.get("rules", [])
    csv_str = generate_csv_export(rules, headers=["antecedent_str", "consequent_str", "support", "confidence", "lift"])

    return Response(
        content=csv_str,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=SkillSphere_Association_Rules.csv"}
    )
