from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import (
    MiningClassificationRequest, SinglePredictRequest, 
    MiningClusteringRequest, MiningAprioriRequest
)
from app.services.mining_service import (
    run_classification_pipeline, predict_job_category,
    run_clustering_pipeline, run_association_mining,
    run_text_mining_analysis
)

router = APIRouter(prefix="/mining", tags=["Data Mining Lab"])

@router.post("/classification/train")
def train_classification_model(
    req: MiningClassificationRequest,
    db: Session = Depends(get_db)
):
    """Train Decision Tree or Naive Bayes classifier on job dataset."""
    result = run_classification_pipeline(db, algorithm=req.algorithm)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/classification/predict")
def predict_category(req: SinglePredictRequest):
    """Classify a custom job description using trained model."""
    result = predict_job_category(req.job_description)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/clustering/run")
def run_clustering(
    req: MiningClusteringRequest,
    db: Session = Depends(get_db)
):
    """Run K-Means clustering on TF-IDF vectors of job postings."""
    result = run_clustering_pipeline(db, num_clusters=req.num_clusters)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/association/apriori")
def run_apriori(
    req: MiningAprioriRequest,
    db: Session = Depends(get_db)
):
    """Run Apriori algorithm to extract skill co-occurrence rules."""
    result = run_association_mining(db, min_support=req.min_support, min_confidence=req.min_confidence)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.get("/text-mining/tfidf")
def get_text_mining(
    top_n: int = Query(30, ge=5, le=100),
    db: Session = Depends(get_db)
):
    """Fetch TF-IDF term frequency analysis."""
    result = run_text_mining_analysis(db, top_n=top_n)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
