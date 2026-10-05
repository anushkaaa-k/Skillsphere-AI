import re
import io
from typing import Dict, List, Any
from pypdf import PdfReader
from docx import Document
from app.services.taxonomy import extract_skills_from_text, SKILL_TAXONOMY, normalize_skill

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract clean text from PDF bytes using pypdf."""
    reader = PdfReader(io.BytesIO(file_bytes))
    text_parts = []
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text_parts.append(extracted)
    return "\n".join(text_parts)

def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract clean text from DOCX bytes using python-docx."""
    doc = Document(io.BytesIO(file_bytes))
    text_parts = [p.text for p in doc.paragraphs if p.text]
    return "\n".join(text_parts)

def parse_resume_text(text: str) -> Dict[str, Any]:
    """
    Parse resume text to extract skills, experience indicators, education hints, and categories.
    """
    cleaned_text = re.sub(r'\s+', ' ', text).strip()

    # Detect skills
    detected_skills = extract_skills_from_text(cleaned_text)

    # Group skills by taxonomy category
    categorized_skills: Dict[str, List[str]] = {}
    for skill in detected_skills:
        cat = SKILL_TAXONOMY.get(skill, {}).get("category", "General Tech")
        if cat not in categorized_skills:
            categorized_skills[cat] = []
        categorized_skills[cat].append(skill)

    # Simple heuristic extraction for education and experience
    education = []
    if re.search(r'\b(bachelor|master|phd|b\.s|m\.s|b\.tech|m\.tech|degree|university|college)\b', cleaned_text, re.IGNORECASE):
        education.append("Higher Education Degree Detected")

    experience_years = 0
    exp_match = re.search(r'(\d+)\+?\s*years?\s*(of)?\s*experience', cleaned_text, re.IGNORECASE)
    if exp_match:
        try:
            experience_years = int(exp_match.group(1))
        except ValueError:
            experience_years = 2
    else:
        experience_years = 2 if len(detected_skills) > 4 else 1

    return {
        "raw_text_length": len(cleaned_text),
        "detected_skills": detected_skills,
        "skill_count": len(detected_skills),
        "categorized_skills": categorized_skills,
        "education_summary": education if education else ["Self-Taught / Degree Not Explicitly Mentioned"],
        "estimated_experience_years": experience_years,
        "parsing_warnings": [] if len(detected_skills) > 0 else ["No standard taxonomy skills detected in file. Check formatting or paste text directly."]
    }
