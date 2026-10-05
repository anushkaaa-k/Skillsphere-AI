import os

class Settings:
    PROJECT_NAME: str = "SkillSphere AI"
    API_V1_STR: str = "/api"
    
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR: str = os.path.join(os.path.dirname(BASE_DIR), "data")
    RAW_DATA_PATH: str = os.path.join(DATA_DIR, "processed", "kaggle_job_market.json")
    
    # SQLite default, PostgreSQL ready via env variable
    DATABASE_URL: str = os.environ.get("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'skillsphere_dw.db')}")

settings = Settings()
