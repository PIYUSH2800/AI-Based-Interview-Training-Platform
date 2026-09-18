import os
import uuid
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models import models
from app.api.profile_routes import get_current_user
from app.services.resume_parser import extract_text_from_file, ResumeAnalyzer

router = APIRouter(
    prefix="/api/users/resume",
    tags=["Resume"]
)

# Upload storage directory
UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads", "resumes"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/x-pdf",
    "application/octet-stream"
}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post("")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Validate file extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{ext}'. Only PDF (.pdf) and Word (.docx) files are supported."
        )

    # 2. Validate MIME content-type
    if file.content_type and file.content_type.lower() not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file content-type '{file.content_type}'. Only PDF and DOCX files are allowed."
        )

    # 3. Validate file size (max 5 MB)
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum limit of 5 MB (received {round(len(contents)/(1024*1024), 2)} MB)."
        )

    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # Get or create user profile
    profile = db.query(models.Profile).filter(models.Profile.user_id == current_user.id).first()
    if not profile:
        profile = models.Profile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)

    # 4. Remove old resume file if it exists
    if profile.resume_path:
        old_full_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", profile.resume_path))
        if os.path.exists(old_full_path) and os.path.isfile(old_full_path):
            try:
                os.remove(old_full_path)
            except Exception as e:
                print(f"Warning: Failed to clean up old resume file: {e}")

    # 5. Generate safe unique filename
    safe_uuid = uuid.uuid4().hex[:8]
    unique_filename = f"resume_user_{current_user.id}_{safe_uuid}{ext}"
    dest_path = os.path.join(UPLOAD_DIR, unique_filename)

    # Write file securely to storage
    with open(dest_path, "wb") as f:
        f.write(contents)

    # Store relative path in profile.resume_path
    relative_path = os.path.join("uploads", "resumes", unique_filename).replace("\\", "/")
    profile.resume_path = relative_path
    db.commit()
    db.refresh(profile)

    return {
        "message": "Resume uploaded successfully",
        "filename": unique_filename,
        "original_filename": file.filename,
        "file_type": ext[1:].upper(),
        "size": len(contents),
        "resume_path": relative_path
    }


@router.get("")
def get_resume_info(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(models.Profile).filter(models.Profile.user_id == current_user.id).first()
    if not profile or not profile.resume_path:
        return {"has_resume": False, "resume": None}

    full_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", profile.resume_path))
    if not os.path.exists(full_path):
        return {"has_resume": False, "resume": None}

    file_size = os.path.getsize(full_path)
    filename = os.path.basename(full_path)
    ext = os.path.splitext(filename)[1].upper().replace(".", "")

    return {
        "has_resume": True,
        "resume": {
            "filename": filename,
            "file_type": ext,
            "size": file_size,
            "resume_path": profile.resume_path
        }
    }


@router.get("/download")
def download_resume(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(models.Profile).filter(models.Profile.user_id == current_user.id).first()
    if not profile or not profile.resume_path:
        raise HTTPException(status_code=404, detail="No resume file found for current user.")

    full_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", profile.resume_path))
    
    # Path traversal check: ensure file is inside UPLOAD_DIR
    if not os.path.abspath(full_path).startswith(UPLOAD_DIR):
        raise HTTPException(status_code=403, detail="Access denied.")

    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        raise HTTPException(status_code=404, detail="Resume file not found on server.")

    filename = os.path.basename(full_path)
    ext = os.path.splitext(filename)[1].lower()
    media_type = "application/pdf" if ext == ".pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    return FileResponse(
        path=full_path,
        media_type=media_type,
        filename=filename,
        headers={"Content-Disposition": f'inline; filename="{filename}"'}
    )


@router.delete("")
def delete_resume(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(models.Profile).filter(models.Profile.user_id == current_user.id).first()
    if not profile or not profile.resume_path:
        raise HTTPException(status_code=404, detail="No resume uploaded to delete.")

    full_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", profile.resume_path))
    if os.path.exists(full_path) and os.path.isfile(full_path):
        try:
            os.remove(full_path)
        except Exception as e:
            print(f"Warning: Failed to delete physical resume file: {e}")

    profile.resume_path = None
    db.commit()
    db.refresh(profile)

    return {"message": "Resume deleted successfully"}


@router.post("/analyze")
def analyze_resume(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(models.Profile).filter(models.Profile.user_id == current_user.id).first()
    if not profile or not profile.resume_path:
        raise HTTPException(status_code=400, detail="No resume uploaded to analyze. Please upload a resume first.")

    full_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", profile.resume_path))
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="Resume file missing on server.")

    text = extract_text_from_file(full_path)
    analysis_result = ResumeAnalyzer.analyze(text)

    return analysis_result
