import json
import csv
import random
from datetime import datetime, timedelta

# Seed for reproducibility
random.seed(42)

CATEGORIES = {
    "Data Science & Analytics": {
        "titles": ["Data Scientist", "Senior Data Scientist", "Data Analyst", "Lead Data Scientist", "Quantitative Analyst", "Biostatistician", "Business Intelligence Analyst"],
        "required_skills": ["Python", "SQL", "Statistics", "Pandas", "Data Visualization"],
        "optional_skills": ["R", "NumPy", "Scikit-Learn", "Tableau", "Power BI", "A/B Testing", "BigQuery", "Snowflake", "Machine Learning", "Excel"],
        "salary_range": (85000, 175000)
    },
    "Software Engineering": {
        "titles": ["Software Engineer", "Full Stack Developer", "Backend Engineer", "Frontend Developer", "Senior Software Engineer", "Systems Engineer", "API Engineer"],
        "required_skills": ["JavaScript", "TypeScript", "Python", "Git", "REST APIs"],
        "optional_skills": ["React", "Node.js", "Java", "C++", "Docker", "PostgreSQL", "MongoDB", "GraphQL", "Microservices", "Redis", "Next.js", "Tailwind CSS"],
        "salary_range": (90000, 185000)
    },
    "Machine Learning & AI": {
        "titles": ["Machine Learning Engineer", "AI Research Scientist", "NLP Engineer", "Computer Vision Engineer", "MLOps Engineer", "LLM Engineer", "Applied AI Specialist"],
        "required_skills": ["Python", "PyTorch", "TensorFlow", "Scikit-Learn", "Machine Learning"],
        "optional_skills": ["Deep Learning", "NLP", "Computer Vision", "Transformers", "MLOps", "Vector Databases", "HuggingFace", "C++", "CUDA", "LangChain", "OpenCV"],
        "salary_range": (110000, 210000)
    },
    "DevOps & Cloud Engineering": {
        "titles": ["DevOps Engineer", "Cloud Solutions Architect", "Site Reliability Engineer", "Infrastructure Engineer", "Platform Engineer", "Kubernetes Specialist"],
        "required_skills": ["AWS", "Docker", "Kubernetes", "Linux", "CI/CD"],
        "optional_skills": ["GCP", "Azure", "Terraform", "Ansible", "Bash", "Prometheus", "Grafana", "Python", "Cloud Security", "Helm"],
        "salary_range": (95000, 190000)
    },
    "Data Engineering": {
        "titles": ["Data Engineer", "Senior Data Engineer", "ETL Developer", "Data Platform Engineer", "Big Data Engineer", "Analytics Engineer"],
        "required_skills": ["Python", "SQL", "Apache Spark", "Airflow", "Data Warehousing"],
        "optional_skills": ["Kafka", "Snowflake", "BigQuery", "dbt", "ETL Pipelines", "Hadoop", "Data Modeling", "PostgreSQL", "Scala", "AWS Glue"],
        "salary_range": (100000, 195000)
    },
    "Cybersecurity": {
        "titles": ["Cybersecurity Analyst", "Security Engineer", "Penetration Tester", "Information Security Specialist", "SOC Analyst", "Security Architect"],
        "required_skills": ["Network Security", "Linux", "Python", "SIEM", "Security Compliance"],
        "optional_skills": ["Penetration Testing", "Risk Assessment", "Cryptography", "Identity Access Management", "Incident Response", "Firewalls", "Wireshark", "CISSP", "Cloud Security"],
        "salary_range": (88000, 180000)
    },
    "Database & Systems": {
        "titles": ["Database Administrator", "PostgreSQL Administrator", "Systems Administrator", "Database Architect", "SQL Server DBA"],
        "required_skills": ["SQL", "Linux", "PostgreSQL", "Database Administration", "Backup & Recovery"],
        "optional_skills": ["MySQL", "Oracle", "SQL Tuning", "Bash", "Performance Optimization", "Python", "Replication", "Disaster Recovery"],
        "salary_range": (82000, 165000)
    },
    "Product & Tech Management": {
        "titles": ["Product Manager", "Technical Product Manager", "Data Product Manager", "Scrum Master", "Agile Project Manager"],
        "required_skills": ["Product Strategy", "Agile/Scrum", "User Research", "Jira", "Data Analytics"],
        "optional_skills": ["Product Roadmap", "Stakeholder Management", "A/B Testing", "SQL", "User Stories", "Feature Prioritization", "OKRs"],
        "salary_range": (95000, 175000)
    }
}

COMPANIES = [
    "TechCorp Global", "CloudScale Labs", "DataMind AI", "CyberShield Systems", 
    "NextGen AI Solutions", "FinTech Hub", "Global Logistics Corp", "Apex Health Tech",
    "OmniData Analytics", "Quantum Systems", "EcoTech Innovations", "Starlight Software",
    "BlueHorizon Cloud", "Veritas Data", "Hyperion Robotics", "Pulse Media",
    "Acme Digital", "Vanguard Security", "Alpha Peak Technologies", "BrightPath AI"
]

LOCATIONS = [
    {"city": "San Francisco", "state": "CA", "country": "USA", "region": "North America"},
    {"city": "New York", "state": "NY", "country": "USA", "region": "North America"},
    {"city": "Austin", "state": "TX", "country": "USA", "region": "North America"},
    {"city": "Seattle", "state": "WA", "country": "USA", "region": "North America"},
    {"city": "Chicago", "state": "IL", "country": "USA", "region": "North America"},
    {"city": "London", "state": "Greater London", "country": "UK", "region": "Europe"},
    {"city": "Bengaluru", "state": "Karnataka", "country": "India", "region": "Asia-Pacific"},
    {"city": "Remote", "state": "Remote", "country": "Global", "region": "Remote"}
]

EXPERIENCE_LEVELS = ["Entry Level", "Mid Level", "Senior Level", "Lead / Executive"]
EMPLOYMENT_TYPES = ["Full-Time", "Contract", "Part-Time"]

START_DATE = datetime(2025, 1, 1)

def generate_postings(num_postings=650):
    postings = []
    
    for i in range(1, num_postings + 1):
        cat_name = random.choice(list(CATEGORIES.keys()))
        cat_info = CATEGORIES[cat_name]
        
        title = random.choice(cat_info["titles"])
        company = random.choice(COMPANIES)
        loc = random.choice(LOCATIONS)
        exp_level = random.choices(EXPERIENCE_LEVELS, weights=[0.2, 0.45, 0.25, 0.1])[0]
        emp_type = random.choices(EMPLOYMENT_TYPES, weights=[0.85, 0.12, 0.03])[0]
        
        # Determine skills
        num_req = random.randint(3, len(cat_info["required_skills"]))
        req_skills = random.sample(cat_info["required_skills"], num_req)
        
        num_opt = random.randint(2, 5)
        opt_skills = random.sample(cat_info["optional_skills"], min(num_opt, len(cat_info["optional_skills"])))
        
        all_skills = list(set(req_skills + opt_skills))
        
        # Salary calculation based on experience level
        min_base, max_base = cat_info["salary_range"]
        mult = {"Entry Level": 0.8, "Mid Level": 1.0, "Senior Level": 1.35, "Lead / Executive": 1.65}[exp_level]
        min_salary = int(min_base * mult + random.randint(-5000, 5000))
        max_salary = int(max_base * mult + random.randint(-5000, 5000))
        
        # Random date within last 18 months
        days_offset = random.randint(0, 500)
        post_date = START_DATE + timedelta(days=days_offset)
        
        # Construct realistic description
        description = (
            f"We are seeking a highly skilled {title} to join our engineering team at {company} in {loc['city']}. "
            f"As a {title}, you will work on mission-critical projects using state-of-the-art technologies. "
            f"Key responsibilities include designing scalable architecture, collaborating with cross-functional teams, "
            f"and driving data-driven innovations. The ideal candidate will have strong proficiency in {', '.join(req_skills[:3])} "
            f"and experience with {', '.join(opt_skills[:3])}. Candidates with a background in {cat_name} and proven problem-solving "
            f"abilities are strongly encouraged to apply."
        )
        
        posting = {
            "source_job_id": f"JOB-{10000 + i}",
            "job_title": title,
            "job_category": cat_name,
            "company_name": company,
            "city": loc["city"],
            "state": loc["state"],
            "country": loc["country"],
            "region": loc["region"],
            "experience_level": exp_level,
            "employment_type": emp_type,
            "min_salary": min_salary,
            "max_salary": max_salary,
            "currency": "USD",
            "posting_date": post_date.strftime("%Y-%m-%d"),
            "required_skills": req_skills,
            "preferred_skills": opt_skills,
            "all_extracted_skills": all_skills,
            "description": description,
            "source": "SkillSphere Job Network"
        }
        postings.append(posting)
        
    return postings

if __name__ == "__main__":
    data = generate_postings(650)
    
    # Save JSON
    with open("C:/Users/hp/.gemini/antigravity/scratch/skillsphere-ai/data/raw/job_postings.json", "w") as f:
        json.dump(data, f, indent=2)
        
    # Save CSV
    fieldnames = [
        "source_job_id", "job_title", "job_category", "company_name", "city", "state", 
        "country", "region", "experience_level", "employment_type", "min_salary", "max_salary", 
        "currency", "posting_date", "required_skills", "preferred_skills", "all_extracted_skills", "description", "source"
    ]
    with open("C:/Users/hp/.gemini/antigravity/scratch/skillsphere-ai/data/raw/job_postings.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            row_copy = row.copy()
            row_copy["required_skills"] = "|".join(row["required_skills"])
            row_copy["preferred_skills"] = "|".join(row["preferred_skills"])
            row_copy["all_extracted_skills"] = "|".join(row["all_extracted_skills"])
            writer.writerow(row_copy)
            
    print(f"Successfully generated {len(data)} job postings in JSON and CSV formats!")
