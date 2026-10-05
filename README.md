# SkillSphere AI 🚀
### Intelligent Job Market Analytics & Personalized Skill Gap Intelligence Platform
*Third-Year Computer Engineering Mini-Project — Data Warehousing and Data Mining (DWM)*

---

## 🌟 Executive Overview
**SkillSphere AI** bridges the gap between macro job-market intelligence and personalized career development. By combining **Data Warehousing (ETL & Star Schema OLAP)**, **Data Mining (Classification, K-Means Clustering, Apriori Association Rule Mining, TF-IDF Text Mining)**, and **NLP Resume Intelligence**, SkillSphere AI provides evidence-based career roadmap guidance.

---

## 🎨 Design System & Palette Compliance
The application strictly reproduces the exact visual palette requested:
- **Pale Mint Background**: `--color-background` (`#eef7f5`)
- **Deep Muted Teal Sidebar & Dark Panels**: `--color-sidebar` (`#0f3838`)
- **Mustard Gold Highlights & Actions**: `--color-primary` (`#d99b00`)
- **White Card Surfaces**: `--color-surface` (`#ffffff`)
- **Pale Mint Input Fields**: `--color-input` (`#e4f2ef`)

---

## 🏗 System Architecture & DWM Concept Mapping

| DWM Syllabus Concept | Technical Implementation | Module / File Location |
| :--- | :--- | :--- |
| **Data Warehouse** | PostgreSQL Compatible Relational Analytical Storage | `backend/app/models.py` |
| **Star Schema** | `FactJobSkill` Fact Table + 5 Dimensions (`DimJob`, `DimSkill`, `DimCompany`, `DimLocation`, `DimDate`) | `backend/app/models.py` |
| **ETL Pipeline** | Extraction, Normalization, Duplicate Detection, Quality Auditing | `backend/app/services/etl_service.py` |
| **OLAP Operations** | Real SQL Roll-Up, Drill-Down, Slice, Dice, and Pivot | `backend/app/services/olap_service.py` |
| **Classification** | Decision Tree & Multinomial Naive Bayes Classifiers | `backend/app/services/mining_service.py` |
| **Clustering** | K-Means Clustering on TF-IDF Vectors | `backend/app/services/mining_service.py` |
| **Association Mining** | Apriori Algorithm calculating Support, Confidence, and Lift | `backend/app/services/mining_service.py` |
| **Text Mining** | Token-Aware Skill Extraction & TF-IDF Similarity Search | `backend/app/services/taxonomy.py` |
| **Resume Intelligence** | PDF/DOCX/TXT parsing & Taxonomy Synonym Mapping | `backend/app/services/resume_service.py` |
| **Reporting & Export** | ReportLab PDF Report Generator & CSV Data Exporters | `backend/app/services/report_service.py` |

---

## 📂 Repository Structure

```
skillsphere-ai/
├── backend/
│   ├── app/
│   │   ├── api/             # 10 FastAPI router endpoints
│   │   ├── services/        # ETL, OLAP, Mining, Resume, Skill Gap, Report services
│   │   ├── config.py        # Config settings
│   │   ├── database.py      # SQLAlchemy session factory
│   │   ├── models.py        # DWM Star Schema & Staging models
│   │   ├── schemas.py       # Pydantic request/response contracts
│   │   └── main.py          # FastAPI application entrypoint
│   ├── requirements.txt     # Python dependencies
│   └── venv/                # Python virtual environment
├── frontend/
│   ├── src/
│   │   ├── components/      # Sidebar & Header shell components
│   │   ├── pages/           # 10 Full-stack feature pages
│   │   ├── services/        # API client service
│   │   ├── types/           # TypeScript contracts
│   │   ├── App.tsx          # Main application router
│   │   └── index.css        # Palette design tokens
│   ├── tailwind.config.js   # Tailwind custom design tokens
│   └── package.json         # React + Vite dependencies
├── data/
│   ├── raw/                 # Versioned job_postings.json & job_postings.csv (650 postings)
│   └── generate_dataset.py  # Dataset generator script
└── tests/
    └── test_backend.py      # Pytest automated test suite (100% passing)
```

---

## ⚡ How to Run the Application

### 1. Backend Setup (FastAPI & Database)
```bash
cd backend
# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies (already installed in setup)
pip install -r requirements.txt

# Launch FastAPI Server
uvicorn app.main:app --reload --port 8000
```
*Backend API documentation will be active at:* `http://localhost:8000/docs`

### 2. Frontend Setup (React + Vite)
```bash
cd frontend

# Launch Vite Dev Server
npm run dev
```
*Frontend application will be accessible at:* `http://localhost:3000`

---

## 🧪 Automated Testing
Run the comprehensive backend test suite:
```bash
cd backend
.\venv\Scripts\python -m pytest C:\Users\hp\.gemini\antigravity\scratch\skillsphere-ai\tests\test_backend.py -v
```
*Result:* **7 / 7 automated API & ML tests passing cleanly.**
