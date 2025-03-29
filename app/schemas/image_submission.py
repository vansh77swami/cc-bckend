from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class ImageSubmissionBase(BaseModel):
    email: EmailStr

class ImageSubmissionCreate(ImageSubmissionBase):
    pass

class ImageSubmissionResponse(ImageSubmissionBase):
    id: str
    status: str
    original_image_path: str
    result_image_path: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ImageSubmissionStatus(BaseModel):
    submission_id: str
    status: str
    result_url: Optional[str] = None 