import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import engine, Base, SessionLocal
from app.models import DimJob
from app.services.etl_service import run_etl_pipeline

# Ensure DB tables exist before running test suite
Base.metadata.create_all(bind=engine)
db = SessionLocal()
if db.query(DimJob).count() == 0:
    run_etl_pipeline(db)
db.close()

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["health"] == "OK"

def test_overview_kpi_endpoint():
    response = client.get("/api/overview/kpi")
    assert response.status_code == 200
    data = response.json()
    assert "total_job_postings" in data
    assert data["total_job_postings"] > 0

def test_market_skills_demand():
    response = client.get("/api/market/skills-demand")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_olap_query():
    payload = {"operation_type": "slice", "category": "Data Science & Analytics"}
    response = client.post("/api/olap/query", json=payload)
    assert response.status_code == 200
    assert response.json()["operation"] == "slice"

def test_apriori_association():
    payload = {"min_support": 0.05, "min_confidence": 0.2}
    response = client.post("/api/mining/association/apriori", json=payload)
    assert response.status_code == 200
    assert "rule_count" in response.json()

def test_classification():
    payload = {"algorithm": "decision_tree"}
    response = client.post("/api/mining/classification/train", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "accuracy" in data
    assert data["accuracy"] > 0.0

def test_skill_gap_analysis():
    payload = {
        "confirmed_skills": ["Python", "SQL", "Pandas"],
        "target_role": "Data Scientist",
        "experience_level": "Mid Level"
    }
    response = client.post("/api/skill-gap/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "coverage_percentage" in data
    assert "roadmap" in data

def test_skill_gap_case_insensitivity():
    """Verify that lowercase, uppercase, and hyphenated skills match canonically."""
    payload_lower = {
        "confirmed_skills": ["python", "sql", "machine-learning"],
        "target_role": "Data Scientist",
        "experience_level": "Mid Level"
    }
    res_lower = client.post("/api/skill-gap/analyze", json=payload_lower)
    assert res_lower.status_code == 200
    data = res_lower.json()
    matched_names = [s["skill_name"] for s in data["matched_skills"]]
    assert "Python" in matched_names
    assert "SQL" in matched_names
    assert "Machine Learning" in matched_names

def test_pdf_report_single_source_of_truth():
    """Verify PDF report dynamically reflects active target role profile."""
    # 1. Update candidate profile to Data Engineer
    payload = {
        "confirmed_skills": ["python", "sql", "airflow"],
        "target_role": "Data Engineer",
        "experience_level": "Senior Level"
    }
    client.post("/api/skill-gap/analyze", json=payload)

    # 2. Download PDF report
    pdf_res = client.get("/api/reports/pdf/skill-gap")
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert "Data_Engineer" in pdf_res.headers["content-disposition"]
