from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import SkillGapRequest
from app.services.skill_gap_service import analyze_skill_gap
from app.models import UserSkillProfile
from app.services.taxonomy import normalize_skill, normalize_skill_list, clean_skill_key

router = APIRouter(prefix="/skill-gap", tags=["Skill Gap Studio"])

@router.post("/analyze")
def run_skill_gap_analysis(
    req: SkillGapRequest,
    db: Session = Depends(get_db)
):
    """Run transparent skill gap analysis and generate candidate learning roadmap."""
    normalized_skills = normalize_skill_list(req.confirmed_skills)
    profile = db.query(UserSkillProfile).filter(UserSkillProfile.user_id == "default_user").first()
    if not profile:
        profile = UserSkillProfile(user_id="default_user")
        db.add(profile)

    profile.confirmed_skills = normalized_skills
    profile.target_role = req.target_role
    profile.experience_level = req.experience_level
    db.commit()

    return analyze_skill_gap(
        db,
        confirmed_skills=normalized_skills,
        target_role=req.target_role,
        experience_level=req.experience_level,
        learned_skills=profile.learned_skills
    )

@router.get("/profile")
def get_user_profile(db: Session = Depends(get_db)):
    """Fetch saved candidate skill profile."""
    profile = db.query(UserSkillProfile).filter(UserSkillProfile.user_id == "default_user").first()
    if not profile:
        profile = UserSkillProfile(
            user_id="default_user",
            target_role="Data Scientist",
            experience_level="Mid Level",
            confirmed_skills=[],
            learned_skills=[]
        )
        db.add(profile)
        db.commit()

    return profile

@router.post("/toggle-skill-learned")
def toggle_skill_learned(
    skill_name: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """Mark a skill as learned in the candidate's profile."""
    profile = db.query(UserSkillProfile).filter(UserSkillProfile.user_id == "default_user").first()
    if not profile:
        profile = UserSkillProfile(user_id="default_user")
        db.add(profile)

    norm_skill = normalize_skill(skill_name)
    clean_key = clean_skill_key(norm_skill)

    learned_keys = {clean_skill_key(s): s for s in (profile.learned_skills or [])}
    confirmed_keys = {clean_skill_key(s): s for s in (profile.confirmed_skills or [])}

    if clean_key in learned_keys:
        del learned_keys[clean_key]
    else:
        learned_keys[clean_key] = norm_skill
        confirmed_keys[clean_key] = norm_skill

    profile.learned_skills = list(learned_keys.values())
    profile.confirmed_skills = list(confirmed_keys.values())
    db.commit()

    return {
        "message": f"Skill '{norm_skill}' updated successfully.",
        "confirmed_skills": profile.confirmed_skills,
        "learned_skills": profile.learned_skills,
        "analysis": analyze_skill_gap(
            db,
            confirmed_skills=profile.confirmed_skills,
            target_role=profile.target_role or "Data Scientist",
            experience_level=profile.experience_level or "Mid Level",
            learned_skills=profile.learned_skills
        )
    }
