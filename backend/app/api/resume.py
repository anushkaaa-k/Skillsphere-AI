from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.services.resume_service import extract_text_from_pdf, extract_text_from_docx, parse_resume_text
from app.models import UserSkillProfile

router = APIRouter(prefix="/resume", tags=["Resume Intelligence"])

@router.post("/parse")
async def parse_resume_file(
    file: Optional[UploadFile] = File(None),
    pasted_text: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Parse PDF/DOCX resume file or raw pasted text and extract canonical skills."""
    extracted_text = ""

    if file:
        filename = file.filename.lower()
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size exceeds 10MB limit.")

        if filename.endswith(".pdf"):
            extracted_text = extract_text_from_pdf(content)
        elif filename.endswith(".docx") or filename.endswith(".doc"):
            extracted_text = extract_text_from_docx(content)
        elif filename.endswith(".txt"):
            extracted_text = content.decode("utf-8", errors="ignore")
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload PDF, DOCX, or TXT.")

    elif pasted_text and pasted_text.strip():
        extracted_text = pasted_text.strip()
    else:
        raise HTTPException(status_code=400, detail="Please upload a resume file or paste resume text.")

    parsed_data = parse_resume_text(extracted_text)

    # Update candidate profile in DB
    profile = db.query(UserSkillProfile).filter(UserSkillProfile.user_id == "default_user").first()
    if not profile:
        profile = UserSkillProfile(user_id="default_user")
        db.add(profile)

    profile.resume_extracted_skills = parsed_data["detected_skills"]
    db.commit()

    return parsed_data
