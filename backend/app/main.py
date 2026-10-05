from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base, SessionLocal
from app.models import DimJob
from app.services.etl_service import run_etl_pipeline

# API Routers
from app.api.overview import router as overview_router
from app.api.market_intelligence import router as market_router
from app.api.resume import router as resume_router
from app.api.skill_gap import router as skill_gap_router
from app.api.jobs import router as jobs_router
from app.api.mining import router as mining_router
from app.api.olap import router as olap_router
from app.api.etl import router as etl_router
from app.api.reports import router as reports_router
from app.api.settings import router as settings_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Intelligent Job Market Analytics & Personalized Skill Gap Intelligence Platform (DWM Academic Mini-Project)",
    version="1.0.0"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(overview_router, prefix=settings.API_V1_STR)
app.include_router(market_router, prefix=settings.API_V1_STR)
app.include_router(resume_router, prefix=settings.API_V1_STR)
app.include_router(skill_gap_router, prefix=settings.API_V1_STR)
app.include_router(jobs_router, prefix=settings.API_V1_STR)
app.include_router(mining_router, prefix=settings.API_V1_STR)
app.include_router(olap_router, prefix=settings.API_V1_STR)
app.include_router(etl_router, prefix=settings.API_V1_STR)
app.include_router(reports_router, prefix=settings.API_V1_STR)
app.include_router(settings_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
def startup_event():
    """Auto-create tables and populate initial ETL data if database is empty."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(DimJob).count() == 0:
            print("Database empty. Auto-running initial ETL pipeline...")
            run_etl_pipeline(db)
            print("Initial ETL completed!")
    except Exception as e:
        print(f"Startup ETL notice: {e}")
    finally:
        db.close()

@app.get("/")
def root():
    return {
        "message": "Welcome to SkillSphere AI API",
        "docs": "/docs",
        "health": "OK"
    }
