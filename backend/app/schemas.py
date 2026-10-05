from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime

# Overview
class KpiMetricsResponse(BaseModel):
    total_job_postings: int
    unique_companies: int
    unique_skills: int
    job_categories: int
    latest_dataset_refresh: str
    etl_quality_score: float

# Market Intelligence
class MarketFilters(BaseModel):
    category: Optional[str] = None
    job_title: Optional[str] = None
    company: Optional[str] = None
    city: Optional[str] = None
    skill: Optional[str] = None
    exp_level: Optional[str] = None

class RoleComparisonRequest(BaseModel):
    role_1: str
    role_2: str

# Resume & Candidate
class SkillGapRequest(BaseModel):
    confirmed_skills: List[str]
    target_role: str = "Data Scientist"
    experience_level: str = "Mid Level"

# Data Mining
class MiningClassificationRequest(BaseModel):
    algorithm: str = "decision_tree" # "decision_tree" or "naive_bayes"

class SinglePredictRequest(BaseModel):
    job_description: str

class MiningClusteringRequest(BaseModel):
    num_clusters: int = 5

class MiningAprioriRequest(BaseModel):
    min_support: float = 0.08
    min_confidence: float = 0.25

# OLAP
class OlapQueryRequest(BaseModel):
    operation_type: str # "rollup", "drilldown", "slice", "dice", "pivot"
    category: Optional[str] = None
    job_title: Optional[str] = None
    skill_name: Optional[str] = None
    location_city: Optional[str] = None
    year: Optional[int] = None
    limit: int = 50
