from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.models import models
from app.schemas import schemas
from fastapi.security import OAuth2PasswordBearer
from app.auth.auth import SECRET_KEY, ALGORITHM
from jose import JWTError, jwt

router = APIRouter(
    prefix="/api/users/profile",
    tags=["Profile"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

def build_user_profile_response(user: models.User, profile: models.Profile) -> schemas.UserProfileResponse:
    return schemas.UserProfileResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        education=user.education,
        experience_level=user.experience_level,
        phone=profile.phone if profile else None,
        college=profile.college if profile else None,
        degree=profile.degree if profile else None,
        skills=profile.skills if profile else None,
        certifications=profile.certifications if profile else None,
        target_role=profile.target_role if profile else None,
        resume_path=profile.resume_path if profile else None,
    )

@router.get("", response_model=schemas.UserProfileResponse)
def get_profile(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(models.Profile).filter(models.Profile.user_id == current_user.id).first()
    if not profile:
        profile = models.Profile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return build_user_profile_response(current_user, profile)

@router.put("", response_model=schemas.UserProfileResponse)
def update_profile(profile_data: schemas.UserProfileUpdate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(models.Profile).filter(models.Profile.user_id == current_user.id).first()
    if not profile:
        profile = models.Profile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    if hasattr(profile_data, "model_dump"):
        update_data = profile_data.model_dump(exclude_unset=True)
    else:
        update_data = profile_data.dict(exclude_unset=True)

    if "email" in update_data and update_data["email"] and update_data["email"] != current_user.email:
        existing_user = db.query(models.User).filter(models.User.email == update_data["email"]).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email is already registered by another account")

    if "name" in update_data and update_data["name"] is not None and not str(update_data["name"]).strip():
        raise HTTPException(status_code=400, detail="Name cannot be empty")

    user_fields = {"name", "email", "education", "experience_level"}
    profile_fields = {"phone", "college", "degree", "skills", "certifications", "target_role", "resume_path"}

    for key, value in update_data.items():
        if key in user_fields:
            setattr(current_user, key, value)
        elif key in profile_fields:
            setattr(profile, key, value)

    db.commit()
    db.refresh(current_user)
    db.refresh(profile)

    return build_user_profile_response(current_user, profile)
