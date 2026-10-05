import os
import sys
import json
import csv
import re
import pandas as pd
import numpy as np

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend"))
from app.services.taxonomy import extract_skills_from_text, normalize_skill

def preprocess_kaggle_jobs(
    input_csv_path: str = "data/raw/fake_job_postings.csv",
    output_json_path: str = "data/processed/kaggle_job_market.json",
    output_csv_path: str = "data/processed/kaggle_job_market.csv",
    sample_size: int = 2000,
    random_seed: int = 42
):
    """
    Reproducible preprocessing pipeline for Kaggle Real/Fake Job Postings Dataset.
    - Filter non-fraudulent listings (fraudulent == 0)
    - Deduplicate by title & description
    - Parse locations (country, state, city)
    - Map titles/industries/functions cleanly to 8 standard job categories
    - Parse salary ranges (min, max) or keep None (do not invent salaries)
    - Extract & normalize skills via token-aware taxonomy NLP matching
    - Sample 2,000 clean non-fraudulent listings deterministically using seed 42
    """
    print(f"Reading raw Kaggle dataset from {input_csv_path}...")
    df_raw = pd.read_csv(input_csv_path)
    print(f"Original Raw Shape: {df_raw.shape}")

    # 1. Filter Non-Fraudulent Postings
    df_real = df_raw[df_raw["fraudulent"] == 0].copy()

    # 2. Deduplicate
    df_clean = df_real.drop_duplicates(subset=["title", "description"]).copy()
    df_clean = df_clean.dropna(subset=["title", "description"])

    # 3. Deterministic Sample Selection (Seed 42)
    if len(df_clean) > sample_size:
        df_sample = df_clean.sample(n=sample_size, random_state=random_seed).copy()
    else:
        df_sample = df_clean.copy()

    print(f"Sampled Dataset Size: {len(df_sample)} (Seed: {random_seed})")

    # Helper functions for text normalization
    def parse_location(loc_str):
        if pd.isna(loc_str) or not str(loc_str).strip():
            return "Remote", "N/A", "Global", "Remote"
        parts = [p.strip() for p in str(loc_str).split(",")]
        country = parts[0] if len(parts) > 0 and parts[0] else "Global"
        state = parts[1] if len(parts) > 1 and parts[1] else "N/A"
        city = parts[2] if len(parts) > 2 and parts[2] else (parts[0] if len(parts) == 1 else "Remote")
        region = "North America" if country in ["US", "CA"] else ("Europe" if country in ["GB", "DE", "FR"] else "Asia-Pacific")
        return city, state, country, region

    def map_job_category(title, industry, function):
        t = str(title).lower()
        f = (str(function) if pd.notna(function) else "").lower()
        i = (str(industry) if pd.notna(industry) else "").lower()

        # Direct title keyword signals
        if any(w in t for w in ["data scientist", "data analyst", "analytics", "bi ", "business intelligence", "statistician", "quantitative"]):
            return "Data Science & Analytics"
        elif any(w in t for w in ["machine learning", "ai ", "nlp", "deep learning", "computer vision", "algorithm"]):
            return "Machine Learning & AI"
        elif any(w in t for w in ["devops", "cloud", "aws", "kubernetes", "sre", "infrastructure", "system admin", "network"]):
            return "DevOps & Cloud Engineering"
        elif any(w in t for w in ["data engineer", "etl", "big data", "spark", "data warehouse", "data platform"]):
            return "Data Engineering"
        elif any(w in t for w in ["security", "cyber", "penetration", "soc analyst", "information security"]):
            return "Cybersecurity"
        elif any(w in t for w in ["database", "dba", "sql server", "postgres", "oracle", "mysql"]):
            return "Database & Systems"
        elif any(w in t for w in ["product manager", "scrum", "agile", "project manager", "program manager", "product owner"]):
            return "Product & Tech Management"
        elif any(w in t for w in ["developer", "software", "engineer", "frontend", "backend", "full stack", "fullstack", "web", "java", "python", "c++", ".net", "mobile", "ios", "android", "qa", "test"]):
            return "Software Engineering"

        # Secondary function/industry signals
        if "data" in f or "data" in i:
            return "Data Science & Analytics"
        elif "security" in f or "security" in i:
            return "Cybersecurity"
        elif "management" in f or "project" in f:
            return "Product & Tech Management"
        elif "engineering" in f or "information technology" in i or "software" in i:
            return "Software Engineering"
        else:
            return "Software Engineering"

    def parse_salary(sal_str):
        if pd.isna(sal_str) or not str(sal_str).strip():
            return None, None
        match = re.search(r'(\d+)\s*-\s*(\d+)', str(sal_str))
        if match:
            try:
                min_s = float(match.group(1))
                max_s = float(match.group(2))
                if min_s < 500:
                    min_s *= 1000
                    max_s *= 1000
                return min_s, max_s
            except Exception:
                pass
        return None, None

    processed_list = []

    for idx, row in df_sample.iterrows():
        job_id = f"KAG-{row['job_id']}"
        title = str(row['title']).strip()
        ind = str(row['industry']) if pd.notna(row['industry']) else ""
        func = str(row['function']) if pd.notna(row['function']) else ""
        category = map_job_category(title, ind, func)

        city, state, country, region = parse_location(row['location'])

        exp_level = str(row['required_experience']) if pd.notna(row['required_experience']) else "Mid Level"
        if exp_level.lower() in ["not applicable", "unspecified"]:
            exp_level = "Mid Level"

        emp_type = str(row['employment_type']) if pd.notna(row['employment_type']) else "Full-Time"

        min_sal, max_sal = parse_salary(row['salary_range'])

        desc = str(row['description']) if pd.notna(row['description']) else ""
        reqs = str(row['requirements']) if pd.notna(row['requirements']) else ""
        comp_profile = str(row['company_profile']) if pd.notna(row['company_profile']) else ""

        full_text = f"{title} {category} {desc} {reqs} {comp_profile} {ind} {func}"

        # Extract skills using NLP taxonomy matching
        extracted_skills = extract_skills_from_text(full_text)

        # Company Name Extraction
        company_name = "Real Employer Posting"
        if comp_profile:
            match_comp = re.search(r'([A-Z][A-Za-z0-9\s,&]{2,30})\s+(is|was|provides|builds|helps|offers)', comp_profile)
            if match_comp:
                company_name = match_comp.group(1).strip()
            else:
                company_name = comp_profile.split('.')[0][:35].strip()

        item = {
            "source_job_id": job_id,
            "job_title": title,
            "job_category": category,
            "company_name": company_name if company_name else "Real Employer Posting",
            "city": city,
            "state": state,
            "country": country,
            "region": region,
            "experience_level": exp_level,
            "employment_type": emp_type,
            "min_salary": min_sal,
            "max_salary": max_sal,
            "currency": "USD" if min_sal else "N/A",
            "posting_date": "2025-06-15",
            "required_skills": extracted_skills[:4],
            "preferred_skills": extracted_skills[4:],
            "all_extracted_skills": extracted_skills,
            "description": desc[:1500],
            "requirements": reqs[:1000],
            "source": "Kaggle EMSI Real Job Postings Dataset"
        }
        processed_list.append(item)

    # Save Processed JSON
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(processed_list, f, indent=2)

    # Save Processed CSV
    fieldnames = list(processed_list[0].keys())
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in processed_list:
            row_copy = row.copy()
            row_copy["required_skills"] = "|".join(row["required_skills"])
            row_copy["preferred_skills"] = "|".join(row["preferred_skills"])
            row_copy["all_extracted_skills"] = "|".join(row["all_extracted_skills"])
            writer.writerow(row_copy)

    print(f"Successfully processed & saved {len(processed_list)} Kaggle job postings to {output_json_path} and {output_csv_path}!")

if __name__ == "__main__":
    preprocess_kaggle_jobs()
