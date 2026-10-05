from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

# ==========================================
# 1. DATA WAREHOUSE STAR SCHEMA DIMENSIONS
# ==========================================

class DimJob(Base):
    __tablename__ = "dim_job"

    job_key = Column(Integer, primary_key=True, index=True, autoincrement=True)
    source_job_id = Column(String(100), unique=True, index=True, nullable=False)
    job_title = Column(String(255), index=True, nullable=False)
    job_category = Column(String(100), index=True, nullable=False)
    seniority_level = Column(String(50), index=True)
    employment_type = Column(String(50))
    experience_level = Column(String(50), index=True)
    min_salary = Column(Float, nullable=True)
    max_salary = Column(Float, nullable=True)
    currency = Column(String(10), default="USD")
    description = Column(Text, nullable=True)

    # Relationships
    facts = relationship("FactJobSkill", back_populates="job")


class DimSkill(Base):
    __tablename__ = "dim_skill"

    skill_key = Column(Integer, primary_key=True, index=True, autoincrement=True)
    canonical_skill_name = Column(String(100), unique=True, index=True, nullable=False)
    skill_category = Column(String(100), index=True, nullable=False)
    taxonomy_version = Column(String(20), default="v1.0")

    # Relationships
    facts = relationship("FactJobSkill", back_populates="skill")


class DimCompany(Base):
    __tablename__ = "dim_company"

    company_key = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_name = Column(String(255), unique=True, index=True, nullable=False)
    industry = Column(String(100), default="Technology")

    # Relationships
    facts = relationship("FactJobSkill", back_populates="company")


class DimLocation(Base):
    __tablename__ = "dim_location"

    location_key = Column(Integer, primary_key=True, index=True, autoincrement=True)
    city = Column(String(100), index=True, nullable=False)
    state = Column(String(100), nullable=True)
    country = Column(String(100), index=True, nullable=False)
    region = Column(String(100), default="Global")

    # Relationships
    facts = relationship("FactJobSkill", back_populates="location")


class DimDate(Base):
    __tablename__ = "dim_date"

    date_key = Column(Integer, primary_key=True, index=True) # YYYYMMDD
    full_date = Column(Date, unique=True, nullable=False)
    day = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    day_of_week = Column(String(20), nullable=False)

    # Relationships
    facts = relationship("FactJobSkill", back_populates="date")


# ==========================================
# 2. DATA WAREHOUSE FACT TABLE
# ==========================================

class FactJobSkill(Base):
    __tablename__ = "fact_job_skill"

    job_skill_fact_key = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    job_key = Column(Integer, ForeignKey("dim_job.job_key"), nullable=False, index=True)
    skill_key = Column(Integer, ForeignKey("dim_skill.skill_key"), nullable=False, index=True)
    company_key = Column(Integer, ForeignKey("dim_company.company_key"), nullable=False, index=True)
    location_key = Column(Integer, ForeignKey("dim_location.location_key"), nullable=False, index=True)
    date_key = Column(Integer, ForeignKey("dim_date.date_key"), nullable=False, index=True)
    
    mention_count = Column(Integer, default=1)
    is_required = Column(Boolean, default=True)
    skill_weight = Column(Float, default=1.0) # Required=2.0, Preferred=1.0
    source_lineage = Column(String(100), default="SkillSphere Job Network")

    # Relationships
    job = relationship("DimJob", back_populates="facts")
    skill = relationship("DimSkill", back_populates="facts")
    company = relationship("DimCompany", back_populates="facts")
    location = relationship("DimLocation", back_populates="facts")
    date = relationship("DimDate", back_populates="facts")


# ==========================================
# 3. STAGING & ETL AUDIT TABLES
# ==========================================

class StagingJobPosting(Base):
    __tablename__ = "staging_job_posting"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_job_id = Column(String(100))
    job_title = Column(String(255))
    job_category = Column(String(100))
    company_name = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))
    region = Column(String(100))
    experience_level = Column(String(50))
    employment_type = Column(String(50))
    min_salary = Column(Float, nullable=True)
    max_salary = Column(Float, nullable=True)
    currency = Column(String(10))
    posting_date = Column(String(50))
    required_skills_raw = Column(Text)
    preferred_skills_raw = Column(Text)
    description = Column(Text)
    extracted_skills_json = Column(JSON)
    is_valid = Column(Boolean, default=True)
    validation_error = Column(Text, nullable=True)
    ingested_at = Column(DateTime, default=datetime.utcnow)


class EtlAuditLog(Base):
    __tablename__ = "etl_audit_log"

    run_id = Column(String(50), primary_key=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    source_name = Column(String(100))
    input_rows = Column(Integer, default=0)
    accepted_rows = Column(Integer, default=0)
    rejected_rows = Column(Integer, default=0)
    duplicate_rows = Column(Integer, default=0)
    data_quality_score = Column(Float, default=100.0)
    status = Column(String(50), default="IN_PROGRESS") # SUCCESS, FAILED, IN_PROGRESS
    details = Column(Text, nullable=True)


# ==========================================
# 4. CANDIDATE PROFILE & USER STATE
# ==========================================

class UserSkillProfile(Base):
    __tablename__ = "user_skill_profile"

    user_id = Column(String(50), primary_key=True, default="default_user")
    target_role = Column(String(100), default="Data Scientist")
    experience_level = Column(String(50), default="Mid Level")
    confirmed_skills = Column(JSON, default=list) # List of canonical skill names
    learned_skills = Column(JSON, default=list)
    resume_extracted_skills = Column(JSON, default=list)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SavedJob(Base):
    __tablename__ = "saved_job"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), default="default_user")
    job_key = Column(Integer, ForeignKey("dim_job.job_key"))
    saved_at = Column(DateTime, default=datetime.utcnow)
