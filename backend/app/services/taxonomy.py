import re
from typing import Dict, List, Optional, Set

SKILL_TAXONOMY: Dict[str, Dict] = {
    "Python": {
        "aliases": ["python", "python3", "python 3", "py"],
        "category": "Programming Languages",
        "related": ["Pandas", "NumPy", "Scikit-Learn", "FastAPI", "Django", "PyTorch"]
    },
    "JavaScript": {
        "aliases": ["javascript", "js", "es6", "vanilla js"],
        "category": "Programming Languages",
        "related": ["TypeScript", "React", "Node.js", "HTML/CSS", "Vue.js"]
    },
    "TypeScript": {
        "aliases": ["typescript", "ts"],
        "category": "Programming Languages",
        "related": ["JavaScript", "React", "Node.js", "Next.js"]
    },
    "SQL": {
        "aliases": ["sql", "structured query language", "tsql", "plsql", "ansi sql"],
        "category": "Databases & Warehouses",
        "related": ["PostgreSQL", "MySQL", "BigQuery", "Snowflake", "Data Warehousing"]
    },
    "Java": {
        "aliases": ["java", "core java", "java EE", "jdk"],
        "category": "Programming Languages",
        "related": ["Spring Boot", "Kotlin", "Microservices", "Hibernate"]
    },
    "C++": {
        "aliases": ["c++", "cpp", "c plus plus"],
        "category": "Programming Languages",
        "related": ["C", "System Programming", "CUDA", "Algorithms"]
    },
    "R": {
        "aliases": ["r", "r language", "r programming", "rstudio"],
        "category": "Data Science & Analytics",
        "related": ["Statistics", "ggplot2", "Data Visualization", "Biostatistics"]
    },
    "React": {
        "aliases": ["react", "reactjs", "react.js", "react framework"],
        "category": "Web & Frontend",
        "related": ["JavaScript", "TypeScript", "Next.js", "Tailwind CSS", "Redux"]
    },
    "Node.js": {
        "aliases": ["nodejs", "node.js", "node"],
        "category": "Web & Backend",
        "related": ["JavaScript", "TypeScript", "Express.js", "REST APIs", "MongoDB"]
    },
    "Pandas": {
        "aliases": ["pandas"],
        "category": "Data Science & Analytics",
        "related": ["Python", "NumPy", "Data Cleaning", "Data Analysis"]
    },
    "NumPy": {
        "aliases": ["numpy"],
        "category": "Data Science & Analytics",
        "related": ["Python", "Pandas", "Scipy", "Linear Algebra"]
    },
    "Scikit-Learn": {
        "aliases": ["scikit-learn", "sklearn", "scikit learn"],
        "category": "Machine Learning & AI",
        "related": ["Python", "Machine Learning", "Classification", "Clustering"]
    },
    "PyTorch": {
        "aliases": ["pytorch", "torch"],
        "category": "Machine Learning & AI",
        "related": ["Python", "Deep Learning", "Transformers", "Computer Vision", "NLP"]
    },
    "TensorFlow": {
        "aliases": ["tensorflow", "tf", "keras"],
        "category": "Machine Learning & AI",
        "related": ["Python", "Deep Learning", "Neural Networks"]
    },
    "Statistics": {
        "aliases": ["statistics", "statistical analysis", "hypothesis testing", "biostatistics"],
        "category": "Data Science & Analytics",
        "related": ["Python", "R", "A/B Testing", "Data Analysis"]
    },
    "Data Visualization": {
        "aliases": ["data visualization", "data viz", "charting", "plotting"],
        "category": "Data Science & Analytics",
        "related": ["Tableau", "Power BI", "Matplotlib", "Seaborn"]
    },
    "Tableau": {
        "aliases": ["tableau", "tableau desktop", "tableau server"],
        "category": "Business Intelligence",
        "related": ["SQL", "Data Visualization", "Power BI", "Dashboards"]
    },
    "Power BI": {
        "aliases": ["power bi", "powerbi", "dax"],
        "category": "Business Intelligence",
        "related": ["SQL", "Tableau", "Excel", "Data Visualization"]
    },
    "A/B Testing": {
        "aliases": ["a/b testing", "ab testing", "split testing", "experimentation"],
        "category": "Data Science & Analytics",
        "related": ["Statistics", "Python", "Product Strategy"]
    },
    "Machine Learning": {
        "aliases": ["machine learning", "ml", "predictive modeling"],
        "category": "Machine Learning & AI",
        "related": ["Python", "Scikit-Learn", "PyTorch", "Deep Learning"]
    },
    "Deep Learning": {
        "aliases": ["deep learning", "dl", "neural networks"],
        "category": "Machine Learning & AI",
        "related": ["PyTorch", "TensorFlow", "Computer Vision", "NLP"]
    },
    "NLP": {
        "aliases": ["nlp", "natural language processing", "text mining"],
        "category": "Machine Learning & AI",
        "related": ["Python", "Transformers", "LLMs", "HuggingFace"]
    },
    "Computer Vision": {
        "aliases": ["computer vision", "cv", "image processing", "opencv"],
        "category": "Machine Learning & AI",
        "related": ["PyTorch", "Deep Learning", "OpenCV"]
    },
    "Transformers": {
        "aliases": ["transformers", "bert", "gpt", "llm", "large language models"],
        "category": "Machine Learning & AI",
        "related": ["PyTorch", "NLP", "HuggingFace", "Vector Databases"]
    },
    "MLOps": {
        "aliases": ["mlops", "machine learning operations", "ml deployment"],
        "category": "Machine Learning & AI",
        "related": ["Python", "Docker", "Kubernetes", "Airflow", "MLflow"]
    },
    "AWS": {
        "aliases": ["aws", "amazon web services", "ec2", "s3", "lambda"],
        "category": "Cloud & Infrastructure",
        "related": ["Docker", "Kubernetes", "Terraform", "GCP", "Azure"]
    },
    "GCP": {
        "aliases": ["gcp", "google cloud", "google cloud platform", "bigquery"],
        "category": "Cloud & Infrastructure",
        "related": ["AWS", "BigQuery", "Kubernetes", "Terraform"]
    },
    "Azure": {
        "aliases": ["azure", "microsoft azure"],
        "category": "Cloud & Infrastructure",
        "related": ["AWS", "Cloud Security", "DevOps"]
    },
    "Docker": {
        "aliases": ["docker", "containerization", "containers"],
        "category": "DevOps & Infrastructure",
        "related": ["Kubernetes", "AWS", "CI/CD", "Linux"]
    },
    "Kubernetes": {
        "aliases": ["kubernetes", "k8s", "container orchestration"],
        "category": "DevOps & Infrastructure",
        "related": ["Docker", "AWS", "Helm", "DevOps"]
    },
    "Terraform": {
        "aliases": ["terraform", "iac", "infrastructure as code"],
        "category": "DevOps & Infrastructure",
        "related": ["AWS", "GCP", "Azure", "DevOps"]
    },
    "CI/CD": {
        "aliases": ["ci/cd", "ci cd", "continuous integration", "github actions", "jenkins"],
        "category": "DevOps & Infrastructure",
        "related": ["Docker", "Git", "Kubernetes", "DevOps"]
    },
    "Linux": {
        "aliases": ["linux", "ubuntu", "centos", "bash", "shell scripting"],
        "category": "Operating Systems & Admin",
        "related": ["Bash", "Docker", "Network Security", "DevOps"]
    },
    "Git": {
        "aliases": ["git", "github", "gitlab", "version control"],
        "category": "Development Tools",
        "related": ["CI/CD", "Software Engineering", "Linux"]
    },
    "PostgreSQL": {
        "aliases": ["postgresql", "postgres", "psql"],
        "category": "Databases & Warehouses",
        "related": ["SQL", "Data Warehousing", "Database Administration"]
    },
    "MongoDB": {
        "aliases": ["mongodb", "mongo", "nosql"],
        "category": "Databases & Warehouses",
        "related": ["Node.js", "Express.js", "JavaScript"]
    },
    "Snowflake": {
        "aliases": ["snowflake", "snowflake data warehouse"],
        "category": "Databases & Warehouses",
        "related": ["SQL", "BigQuery", "Data Warehousing", "dbt"]
    },
    "BigQuery": {
        "aliases": ["bigquery", "google bigquery", "bq"],
        "category": "Databases & Warehouses",
        "related": ["SQL", "GCP", "Snowflake", "Data Warehousing"]
    },
    "Apache Spark": {
        "aliases": ["apache spark", "pyspark", "spark"],
        "category": "Data Engineering",
        "related": ["Python", "Hadoop", "Data Warehousing", "Kafka"]
    },
    "Airflow": {
        "aliases": ["airflow", "apache airflow", "dag"],
        "category": "Data Engineering",
        "related": ["Python", "ETL Pipelines", "Data Engineering"]
    },
    "dbt": {
        "aliases": ["dbt", "data build tool"],
        "category": "Data Engineering",
        "related": ["SQL", "Snowflake", "BigQuery", "Data Warehousing"]
    },
    "Data Warehousing": {
        "aliases": ["data warehousing", "dw", "star schema", "data modeling"],
        "category": "Data Engineering",
        "related": ["SQL", "Snowflake", "BigQuery", "ETL Pipelines"]
    },
    "ETL Pipelines": {
        "aliases": ["etl pipelines", "etl", "data ingestion", "data pipeline"],
        "category": "Data Engineering",
        "related": ["Python", "SQL", "Airflow", "Apache Spark"]
    },
    "Network Security": {
        "aliases": ["network security", "firewalls", "cybersecurity"],
        "category": "Cybersecurity",
        "related": ["Linux", "SIEM", "Penetration Testing"]
    },
    "SIEM": {
        "aliases": ["siem", "splunk", "security monitoring"],
        "category": "Cybersecurity",
        "related": ["Network Security", "Incident Response"]
    },
    "Penetration Testing": {
        "aliases": ["penetration testing", "ethical hacking", "pen testing"],
        "category": "Cybersecurity",
        "related": ["Network Security", "Linux", "Python"]
    },
    "REST APIs": {
        "aliases": ["rest apis", "rest api", "restful", "web apis"],
        "category": "Web & Backend",
        "related": ["FastAPI", "Node.js", "Python", "GraphQL"]
    },
    "FastAPI": {
        "aliases": ["fastapi", "fast api"],
        "category": "Web & Backend",
        "related": ["Python", "REST APIs", "Pydantic"]
    },
    "Product Strategy": {
        "aliases": ["product strategy", "product roadmap", "feature prioritization"],
        "category": "Product & Management",
        "related": ["Agile/Scrum", "User Research", "Jira"]
    },
    "Agile/Scrum": {
        "aliases": ["agile", "scrum", "kanban", "agile/scrum"],
        "category": "Product & Management",
        "related": ["Jira", "Product Strategy"]
    },
    "Jira": {
        "aliases": ["jira", "confluence", "atlassian"],
        "category": "Product & Management",
        "related": ["Agile/Scrum", "Product Strategy"]
    }
}

def clean_skill_key(s: str) -> str:
    """
    Clean and normalize a skill string for comparison key generation.
    - Trims whitespace
    - Converts to lowercase
    - Replaces hyphens and underscores with spaces
    - Replaces multiple spaces with a single space
    """
    if not s:
        return ""
    s_clean = s.strip().lower()
    s_clean = re.sub(r'[\-_]+', ' ', s_clean)
    s_clean = re.sub(r'\s+', ' ', s_clean)
    return s_clean

# Build reverse alias mapping for fast lookup
ALIAS_MAP: Dict[str, str] = {}
for canonical, info in SKILL_TAXONOMY.items():
    ALIAS_MAP[clean_skill_key(canonical)] = canonical
    for alias in info["aliases"]:
        ALIAS_MAP[clean_skill_key(alias)] = canonical

def normalize_skill(skill_raw: str) -> str:
    """Map a raw skill string or alias to canonical skill name, preserving user input cleanly if unmapped."""
    if not skill_raw or not skill_raw.strip():
        return ""
    cleaned_key = clean_skill_key(skill_raw)
    if cleaned_key in ALIAS_MAP:
        return ALIAS_MAP[cleaned_key]
    
    # If unmapped custom skill, convert hyphens/underscores to spaces and title case cleanly
    cleaned_spaces = re.sub(r'[\-_]+', ' ', skill_raw.strip())
    cleaned_spaces = re.sub(r'\s+', ' ', cleaned_spaces)
    return cleaned_spaces.title()

def normalize_skill_list(skills: List[str]) -> List[str]:
    """Normalize a list of skills, maintaining canonical display names and deduplicating case-insensitively."""
    seen_keys = set()
    canonical_list = []
    for s in skills:
        if not s or not s.strip():
            continue
        norm = normalize_skill(s)
        key = clean_skill_key(norm)
        if key and key not in seen_keys:
            seen_keys.add(key)
            canonical_list.append(norm)
    return canonical_list

def extract_skills_from_text(text: str) -> List[str]:
    """
    Extract canonical skills from job descriptions or resumes using token-aware word-boundary matching.
    Prevents short skill names (e.g. 'R' or 'C') matching inside unrelated words like 'and' or 'case'.
    """
    found_skills: Set[str] = set()
    text_lower = text.lower()

    for alias, canonical in ALIAS_MAP.items():
        # Word boundary pattern for precise skill matching
        if len(alias) <= 2:
            # Short skills require explicit whitespace/punctuation boundaries
            pattern = r'(?<![a-zA-Z0-9])' + re.escape(alias) + r'(?![a-zA-Z0-9])'
        else:
            pattern = r'\b' + re.escape(alias) + r'\b'

        if re.search(pattern, text_lower):
            found_skills.add(canonical)

    return sorted(list(found_skills))

def get_taxonomy_summary():
    """Return taxonomy categories and full skill list."""
    categories: Dict[str, List[str]] = {}
    for canonical, info in SKILL_TAXONOMY.items():
        cat = info["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(canonical)
    return {
        "total_skills": len(SKILL_TAXONOMY),
        "categories": categories,
        "taxonomy": SKILL_TAXONOMY
    }
