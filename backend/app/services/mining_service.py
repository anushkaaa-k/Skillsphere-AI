import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.cluster import KMeans
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix, silhouette_score
from sklearn.decomposition import PCA
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder

from app.models import DimJob, FactJobSkill, DimSkill

# Global model cache to avoid expensive retraining on every request
_MODEL_CACHE: Dict[str, Any] = {}

def get_job_dataset(db: Session) -> pd.DataFrame:
    """Fetch job postings with descriptions and skills for data mining."""
    jobs = db.query(DimJob).all()
    if not jobs:
        return pd.DataFrame()

    data = []
    for j in jobs:
        skills = [f.skill.canonical_skill_name for f in j.facts if f.skill]
        combined_text = f"{j.job_title} {j.job_category} {j.description or ''} {' '.join(skills)}"
        data.append({
            "job_key": j.job_key,
            "source_job_id": j.source_job_id,
            "job_title": j.job_title,
            "job_category": j.job_category,
            "skills": skills,
            "combined_text": combined_text,
            "description": j.description or ""
        })
    return pd.DataFrame(data)

# ==========================================
# 1. CLASSIFICATION PIPELINE
# ==========================================

def run_classification_pipeline(db: Session, algorithm: str = "decision_tree") -> Dict[str, Any]:
    """
    Train Decision Tree or Naive Bayes classifier to predict job category.
    Prevents train/test leakage by fitting vectorizer strictly on training set.
    """
    df = get_job_dataset(db)
    if df.empty or len(df) < 10:
        return {"error": "Insufficient dataset for training."}

    X_text = df["combined_text"]
    y = df["job_category"]

    X_train_text, X_test_text, y_train, y_test = train_test_split(
        X_text, y, test_size=0.25, random_state=42, stratify=y
    )

    vectorizer = TfidfVectorizer(stop_words="english", max_features=1000)
    X_train_vec = vectorizer.fit_transform(X_train_text)
    X_test_vec = vectorizer.transform(X_test_text)

    if algorithm == "naive_bayes":
        clf = MultinomialNB()
    else:
        clf = DecisionTreeClassifier(random_state=42, max_depth=15)

    clf.fit(X_train_vec, y_train)
    y_pred = clf.predict(X_test_vec)

    acc = float(accuracy_score(y_test, y_pred))
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average="weighted", zero_division=0)
    
    unique_labels = sorted(list(y.unique()))
    cm = confusion_matrix(y_test, y_pred, labels=unique_labels).tolist()

    # Save to global cache for live predictions
    _MODEL_CACHE["clf"] = clf
    _MODEL_CACHE["vectorizer"] = vectorizer
    _MODEL_CACHE["labels"] = unique_labels

    class_distribution = y.value_counts().to_dict()

    return {
        "algorithm": "Decision Tree Classifier" if algorithm == "decision_tree" else "Multinomial Naive Bayes",
        "accuracy": round(acc, 4),
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1_score": round(float(f1), 4),
        "labels": unique_labels,
        "confusion_matrix": cm,
        "class_distribution": class_distribution,
        "sample_count": len(df),
        "train_count": len(y_train),
        "test_count": len(y_test)
    }

def predict_job_category(text: str) -> Dict[str, Any]:
    """Predict category for a custom job description using trained model."""
    if "clf" not in _MODEL_CACHE or "vectorizer" not in _MODEL_CACHE:
        return {"error": "Classifier model is not trained yet. Please run classification first."}

    vectorizer = _MODEL_CACHE["vectorizer"]
    clf = _MODEL_CACHE["clf"]

    vec = vectorizer.transform([text])
    pred_category = clf.predict(vec)[0]
    
    # Get probabilities if supported
    probs = {}
    if hasattr(clf, "predict_proba"):
        prob_arr = clf.predict_proba(vec)[0]
        labels = _MODEL_CACHE["labels"]
        probs = {labels[i]: round(float(prob_arr[i]), 4) for i in range(len(labels))}

    return {
        "predicted_category": pred_category,
        "confidence_probabilities": probs
    }

# ==========================================
# 2. CLUSTERING PIPELINE
# ==========================================

def run_clustering_pipeline(db: Session, num_clusters: int = 5) -> Dict[str, Any]:
    """
    K-Means clustering on TF-IDF feature vectors of job descriptions.
    Reduces features to 2D using PCA for scatter plot visualization.
    """
    df = get_job_dataset(db)
    if df.empty or len(df) < 10:
        return {"error": "Insufficient dataset for clustering."}

    vectorizer = TfidfVectorizer(stop_words="english", max_features=500)
    X_vec = vectorizer.fit_transform(df["combined_text"])

    num_clusters = max(2, min(num_clusters, 10))
    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(X_vec)

    df["cluster"] = cluster_labels
    silhouette = float(silhouette_score(X_vec, cluster_labels)) if len(set(cluster_labels)) > 1 else 0.0

    # 2D PCA reduction for scatter plot
    pca = PCA(n_components=2, random_state=42)
    coords_2d = pca.fit_transform(X_vec.toarray())

    terms = vectorizer.get_feature_names_out()
    order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]

    cluster_summaries = []
    scatter_points = []

    for i in range(num_clusters):
        top_terms = [terms[ind] for ind in order_centroids[i, :8]]
        cluster_jobs = df[df["cluster"] == i]
        cat_counts = cluster_jobs["job_category"].value_counts().to_dict()
        top_category = max(cat_counts.items(), key=lambda x: x[1])[0] if cat_counts else "General"

        cluster_summaries.append({
            "cluster_id": i,
            "size": len(cluster_jobs),
            "percentage": round(100.0 * len(cluster_jobs) / len(df), 2),
            "dominant_category": top_category,
            "top_terms": top_terms,
            "sample_jobs": cluster_jobs[["job_title", "job_category"]].head(4).to_dict(orient="records")
        })

    for idx, row in df.iterrows():
        scatter_points.append({
            "x": round(float(coords_2d[idx, 0]), 4),
            "y": round(float(coords_2d[idx, 1]), 4),
            "cluster": int(row["cluster"]),
            "job_title": row["job_title"],
            "job_category": row["job_category"]
        })

    return {
        "num_clusters": num_clusters,
        "silhouette_score": round(silhouette, 4),
        "cluster_summaries": cluster_summaries,
        "scatter_points": scatter_points
    }

# ==========================================
# 3. ASSOCIATION RULE MINING (APRIORI)
# ==========================================

def run_association_mining(db: Session, min_support: float = 0.08, min_confidence: float = 0.25) -> Dict[str, Any]:
    """
    Apriori algorithm extracting skill transaction rules (Support, Confidence, Lift).
    """
    jobs = db.query(DimJob).all()
    transactions = []
    for j in jobs:
        skills = [f.skill.canonical_skill_name for f in j.facts if f.skill]
        if skills:
            transactions.append(skills)

    if not transactions:
        return {"error": "No skill transactions found."}

    te = TransactionEncoder()
    te_ary = te.fit(transactions).transform(transactions)
    df_trans = pd.DataFrame(te_ary, columns=te.columns_)

    # Run Apriori
    frequent_itemsets = apriori(df_trans, min_support=min_support, use_colnames=True)
    if frequent_itemsets.empty:
        return {
            "min_support": min_support,
            "min_confidence": min_confidence,
            "rule_count": 0,
            "rules": [],
            "message": "No itemsets met the minimum support threshold. Try lowering min_support."
        }

    rules_df = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
    if rules_df.empty:
        return {
            "min_support": min_support,
            "min_confidence": min_confidence,
            "rule_count": 0,
            "rules": [],
            "message": "No rules met the minimum confidence threshold."
        }

    rules_list = []
    for _, row in rules_df.iterrows():
        ant = list(row["antecedents"])
        con = list(row["consequents"])
        rules_list.append({
            "antecedents": ant,
            "consequents": con,
            "antecedent_str": ", ".join(ant),
            "consequent_str": ", ".join(con),
            "support": round(float(row["support"]), 4),
            "confidence": round(float(row["confidence"]), 4),
            "lift": round(float(row["lift"]), 4)
        })

    # Sort rules by lift descending
    rules_list.sort(key=lambda x: x["lift"], reverse=True)

    return {
        "min_support": min_support,
        "min_confidence": min_confidence,
        "transaction_count": len(transactions),
        "frequent_itemsets_count": len(frequent_itemsets),
        "rule_count": len(rules_list),
        "rules": rules_list[:100] # Top 100 rules
    }

# ==========================================
# 4. TF-IDF & TEXT MINING
# ==========================================

def run_text_mining_analysis(db: Session, top_n: int = 30) -> Dict[str, Any]:
    """
    TF-IDF term frequency analysis and job description similarity search.
    """
    df = get_job_dataset(db)
    if df.empty:
        return {"error": "No text data available."}

    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=1000)
    X_vec = vectorizer.fit_transform(df["combined_text"])

    mean_tfidf = X_vec.mean(axis=0).A1
    terms = vectorizer.get_feature_names_out()

    top_indices = mean_tfidf.argsort()[::-1][:top_n]
    top_terms = [
        {"term": terms[i], "score": round(float(mean_tfidf[i]), 5)}
        for i in top_indices
    ]

    return {
        "document_count": len(df),
        "vocabulary_size": len(terms),
        "top_terms": top_terms
    }
