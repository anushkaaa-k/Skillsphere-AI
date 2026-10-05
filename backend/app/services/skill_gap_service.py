from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models import DimJob, FactJobSkill, DimSkill, UserSkillProfile
from app.services.taxonomy import SKILL_TAXONOMY, extract_skills_from_text, clean_skill_key, normalize_skill, normalize_skill_list

def analyze_skill_gap(
    db: Session,
    confirmed_skills: List[str],
    target_role: str = "Data Scientist",
    experience_level: str = "Mid Level",
    learned_skills: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Perform transparent, demand-weighted candidate-to-role skill gap analysis with case-insensitive skill matching.
    Includes both confirmed candidate skills and marked learned skills in candidate competencies.
    """
    all_raw = list(confirmed_skills or []) + list(learned_skills or [])
    normalized_confirmed = normalize_skill_list(all_raw)
    
    # Collect clean keys for raw inputs, normalized canonical names, and all their aliases
    confirmed_clean_keys = set()
    for s in all_raw:
        if not s or not s.strip():
            continue
        confirmed_clean_keys.add(clean_skill_key(s))
        norm = normalize_skill(s)
        if norm:
            confirmed_clean_keys.add(clean_skill_key(norm))
            if norm in SKILL_TAXONOMY:
                for alias in SKILL_TAXONOMY[norm].get("aliases", []):
                    confirmed_clean_keys.add(clean_skill_key(alias))

    # 1. Fetch job postings for target role/category to derive target skill requirements
    jobs_query = db.query(DimJob).filter(
        (DimJob.job_title.ilike(f"%{target_role}%")) | (DimJob.job_category.ilike(f"%{target_role}%"))
    )
    matching_jobs = jobs_query.all()
    if not matching_jobs:
        # Fallback to all jobs if specific title not found
        matching_jobs = db.query(DimJob).all()

    job_keys = [j.job_key for j in matching_jobs]

    # Skill frequency in target postings
    skill_demand_query = (
        db.query(
            DimSkill.canonical_skill_name,
            func.count(FactJobSkill.job_skill_fact_key).label("demand_count"),
            func.avg(FactJobSkill.skill_weight).label("avg_weight")
        )
        .join(FactJobSkill, DimSkill.skill_key == FactJobSkill.skill_key)
        .filter(FactJobSkill.job_key.in_(job_keys))
        .group_by(DimSkill.canonical_skill_name)
        .order_by(desc("demand_count"))
        .all()
    )

    if not skill_demand_query:
        # Global skill demand fallback
        skill_demand_query = (
            db.query(
                DimSkill.canonical_skill_name,
                func.count(FactJobSkill.job_skill_fact_key).label("demand_count"),
                func.avg(FactJobSkill.skill_weight).label("avg_weight")
            )
            .join(FactJobSkill, DimSkill.skill_key == FactJobSkill.skill_key)
            .group_by(DimSkill.canonical_skill_name)
            .order_by(desc("demand_count"))
            .all()
        )

    max_demand = max([r.demand_count for r in skill_demand_query], default=1)

    matched_skills = []
    missing_high_priority = []
    missing_secondary = []
    all_target_skills = []

    total_possible_weight = 0.0
    matched_weight = 0.0

    for r in skill_demand_query:
        skill_name = r.canonical_skill_name
        count = r.demand_count
        avg_w = float(r.avg_weight or 1.0)
        is_required = avg_w >= 1.5

        # Weighted demand score formula
        norm_freq = count / max_demand
        weight = 2.0 if is_required else 1.0
        priority_score = round(100.0 * (0.5 * norm_freq + 0.3 * (weight / 2.0) + 0.2 * 0.8), 1)

        skill_info = {
            "skill_name": skill_name,
            "category": SKILL_TAXONOMY.get(skill_name, {}).get("category", "General Tech"),
            "demand_count": count,
            "demand_percentage": round(100.0 * count / max(len(matching_jobs), 1), 1),
            "is_required": is_required,
            "priority_score": priority_score
        }

        all_target_skills.append(skill_info)
        total_possible_weight += weight

        if clean_skill_key(skill_name) in confirmed_clean_keys:
            matched_skills.append(skill_info)
            matched_weight += weight
        else:
            if priority_score >= 50.0 or is_required:
                missing_high_priority.append(skill_info)
            else:
                missing_secondary.append(skill_info)

    # Calculate transparent coverage percentage
    coverage_percentage = round(100.0 * (matched_weight / max(total_possible_weight, 1.0)), 1)

    # Generate Learning Roadmap Sequence
    missing_high_priority.sort(key=lambda x: x["priority_score"], reverse=True)
    missing_secondary.sort(key=lambda x: x["priority_score"], reverse=True)

    roadmap = []
    step = 1

    for s in missing_high_priority[:5]:
        related = SKILL_TAXONOMY.get(s["skill_name"], {}).get("related", [])
        roadmap.append({
            "step": step,
            "skill_name": s["skill_name"],
            "priority_level": "High Priority",
            "priority_score": s["priority_score"],
            "evidence": f"Appears in {s['demand_percentage']}% of target '{target_role}' job postings.",
            "prerequisites": [r for r in related if clean_skill_key(r) in confirmed_clean_keys],
            "related_skills": related[:3]
        })
        step += 1

    for s in missing_secondary[:3]:
        related = SKILL_TAXONOMY.get(s["skill_name"], {}).get("related", [])
        roadmap.append({
            "step": step,
            "skill_name": s["skill_name"],
            "priority_level": "Secondary Skill",
            "priority_score": s["priority_score"],
            "evidence": f"Appears in {s['demand_percentage']}% of target '{target_role}' postings.",
            "prerequisites": [],
            "related_skills": related[:3]
        })
        step += 1

    # Related roles suggestion based on matched skills
    related_roles = [
        "Data Scientist", "Machine Learning Engineer", "Data Engineer", 
        "Full Stack Developer", "DevOps Engineer", "Cybersecurity Analyst"
    ]
    suggested_roles = [r for r in related_roles if r.lower() != target_role.lower()][:3]

    return {
        "target_role": target_role,
        "experience_level": experience_level,
        "coverage_percentage": coverage_percentage,
        "confirmed_skill_count": len(normalized_confirmed),
        "confirmed_skills_canonical": normalized_confirmed,
        "total_target_skills_analyzed": len(all_target_skills),
        "matched_skills": matched_skills,
        "missing_high_priority": missing_high_priority,
        "missing_secondary": missing_secondary,
        "roadmap": roadmap,
        "suggested_roles": suggested_roles,
        "methodology": "Skill coverage is calculated as the ratio of candidate's matched skill weights over total target role skill weights (Required=2.0, Preferred=1.0)."
    }
