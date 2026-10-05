import json
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.config import settings
from app.models import (
    DimJob, DimSkill, DimCompany, DimLocation, DimDate, 
    FactJobSkill, StagingJobPosting, EtlAuditLog
)
from app.services.taxonomy import SKILL_TAXONOMY, normalize_skill, extract_skills_from_text

def run_etl_pipeline(db: Session, raw_file_path: str = None) -> EtlAuditLog:
    """
    Execute full ETL pipeline: Extract raw data, transform/validate, and load into Star Schema.
    Idempotent: prevents duplicate fact entries.
    """
    if raw_file_path is None:
        raw_file_path = settings.RAW_DATA_PATH

    run_id = f"ETL-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"
    audit_log = EtlAuditLog(
        run_id=run_id,
        start_time=datetime.utcnow(),
        source_name=raw_file_path,
        status="IN_PROGRESS"
    )
    db.add(audit_log)
    db.commit()

    try:
        # 1. EXTRACT
        with open(raw_file_path, "r", encoding="utf-8") as f:
            raw_postings = json.load(f)

        input_count = len(raw_postings)
        accepted_count = 0
        rejected_count = 0
        duplicate_count = 0

        # Track existing records to ensure idempotency
        existing_jobs = {j.source_job_id: j.job_key for j in db.query(DimJob.source_job_id, DimJob.job_key).all()}
        existing_skills = {s.canonical_skill_name: s.skill_key for s in db.query(DimSkill.canonical_skill_name, DimSkill.skill_key).all()}
        existing_companies = {c.company_name: c.company_key for c in db.query(DimCompany.company_name, DimCompany.company_key).all()}
        existing_locations = {f"{l.city}_{l.country}": l.location_key for l in db.query(DimLocation.city, DimLocation.country, DimLocation.location_key).all()}
        existing_dates = {d.date_key: d.date_key for d in db.query(DimDate.date_key).all()}

        # Populate DimSkill upfront from taxonomy if missing
        for canonical, info in SKILL_TAXONOMY.items():
            if canonical not in existing_skills:
                skill_dim = DimSkill(
                    canonical_skill_name=canonical,
                    skill_category=info["category"],
                    taxonomy_version="v1.0"
                )
                db.add(skill_dim)
                db.flush()
                existing_skills[canonical] = skill_dim.skill_key

        db.commit()

        # 2. TRANSFORM & LOAD EACH RECORD
        for item in raw_postings:
            source_id = item.get("source_job_id")
            if not source_id:
                rejected_count += 1
                continue

            # Idempotency check
            if source_id in existing_jobs:
                duplicate_count += 1
                continue

            job_title = item.get("job_title", "Unknown Role").strip()
            job_category = item.get("job_category", "General Tech").strip()
            company_name = item.get("company_name", "Anonymous Company").strip()
            city = item.get("city", "Remote").strip()
            state = item.get("state", "N/A").strip()
            country = item.get("country", "Global").strip()
            region = item.get("region", "Global").strip()
            exp_level = item.get("experience_level", "Mid Level").strip()
            emp_type = item.get("employment_type", "Full-Time").strip()
            min_sal = item.get("min_salary")
            max_sal = item.get("max_salary")
            description = item.get("description", "")
            posting_date_str = item.get("posting_date", "2025-01-01")

            # Validate date
            try:
                dt = datetime.strptime(posting_date_str, "%Y-%m-%d")
            except Exception:
                dt = datetime(2025, 1, 1)

            date_key = int(dt.strftime("%Y%m%d"))

            # Staging record
            staging_rec = StagingJobPosting(
                source_job_id=source_id,
                job_title=job_title,
                job_category=job_category,
                company_name=company_name,
                city=city,
                state=state,
                country=country,
                region=region,
                experience_level=exp_level,
                employment_type=emp_type,
                min_salary=min_sal,
                max_salary=max_sal,
                currency="USD",
                posting_date=posting_date_str,
                required_skills_raw="|".join(item.get("required_skills", [])),
                preferred_skills_raw="|".join(item.get("preferred_skills", [])),
                description=description,
                extracted_skills_json=item.get("all_extracted_skills", []),
                is_valid=True
            )
            db.add(staging_rec)

            # Ensure DimCompany
            if company_name not in existing_companies:
                comp_dim = DimCompany(company_name=company_name, industry="Technology")
                db.add(comp_dim)
                db.flush()
                existing_companies[company_name] = comp_dim.company_key
            comp_key = existing_companies[company_name]

            # Ensure DimLocation
            loc_id = f"{city}_{country}"
            if loc_id not in existing_locations:
                loc_dim = DimLocation(city=city, state=state, country=country, region=region)
                db.add(loc_dim)
                db.flush()
                existing_locations[loc_id] = loc_dim.location_key
            loc_key = existing_locations[loc_id]

            # Ensure DimDate
            if date_key not in existing_dates:
                date_dim = DimDate(
                    date_key=date_key,
                    full_date=dt.date(),
                    day=dt.day,
                    month=dt.month,
                    quarter=(dt.month - 1) // 3 + 1,
                    year=dt.year,
                    day_of_week=dt.strftime("%A")
                )
                db.add(date_dim)
                db.flush()
                existing_dates[date_key] = date_key

            # Create DimJob
            job_dim = DimJob(
                source_job_id=source_id,
                job_title=job_title,
                job_category=job_category,
                seniority_level=exp_level,
                employment_type=emp_type,
                experience_level=exp_level,
                min_salary=min_sal,
                max_salary=max_sal,
                currency="USD",
                description=description
            )
            db.add(job_dim)
            db.flush()
            existing_jobs[source_id] = job_dim.job_key
            job_key = job_dim.job_key

            # Extract & Process Skills
            req_skills = item.get("required_skills", [])
            opt_skills = item.get("preferred_skills", [])

            # Also extract skills dynamically from text
            extracted_from_desc = extract_skills_from_text(description)
            combined_skills = set(req_skills + opt_skills + extracted_from_desc)

            for raw_s in combined_skills:
                canonical = normalize_skill(raw_s) or raw_s.title()
                if canonical not in existing_skills:
                    skill_dim = DimSkill(
                        canonical_skill_name=canonical,
                        skill_category="Other Technologies",
                        taxonomy_version="v1.0"
                    )
                    db.add(skill_dim)
                    db.flush()
                    existing_skills[canonical] = skill_dim.skill_key

                s_key = existing_skills[canonical]
                is_req = raw_s in req_skills
                weight = 2.0 if is_req else 1.0

                fact = FactJobSkill(
                    job_key=job_key,
                    skill_key=s_key,
                    company_key=comp_key,
                    location_key=loc_key,
                    date_key=date_key,
                    mention_count=1,
                    is_required=is_req,
                    skill_weight=weight,
                    source_lineage="Kaggle EMSI Real Job Postings Dataset"
                )
                db.add(fact)

            accepted_count += 1

        db.commit()

        quality_score = round(100.0 * (accepted_count / max(input_count - duplicate_count, 1)), 2)

        audit_log.end_time = datetime.utcnow()
        audit_log.input_rows = input_count
        audit_log.accepted_rows = accepted_count
        audit_log.rejected_rows = rejected_count
        audit_log.duplicate_rows = duplicate_count
        audit_log.data_quality_score = quality_score
        audit_log.status = "SUCCESS"
        audit_log.details = f"Loaded {accepted_count} job postings into Star Schema. Quality Score: {quality_score}%"

        db.commit()
        return audit_log

    except Exception as e:
        db.rollback()
        audit_log.end_time = datetime.utcnow()
        audit_log.status = "FAILED"
        audit_log.details = f"ETL Failure: {str(e)}"
        db.commit()
        raise e
