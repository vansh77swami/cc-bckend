import aiofiles
import os
import uuid
from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import get_settings
from app.models.image_submission import ImageSubmission

settings = get_settings()

async def save_upload_file(upload_file: UploadFile) -> str:
    """Save an uploaded file and return the file path."""
    if upload_file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {settings.ALLOWED_IMAGE_TYPES}"
        )
    
    # Ensure upload directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Generate unique filename
    file_extension = os.path.splitext(upload_file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await upload_file.read()
        if len(content) > settings.MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum allowed ({settings.MAX_IMAGE_SIZE} bytes)"
            )
        await out_file.write(content)
    
    return file_path

async def create_image_submission(
    db: AsyncSession,
    email: str,
    file_path: str
) -> ImageSubmission:
    """Create a new image submission record."""
    submission = ImageSubmission(
        id=str(uuid.uuid4()),
        email=email,
        original_image_path=file_path,
        status="pending"
    )
    
    db.add(submission)
    await db.commit()
    await db.refresh(submission)
    
    return submission

async def get_submission_status(
    db: AsyncSession,
    submission_id: str
) -> ImageSubmission:
    """Get the status of an image submission."""
    result = await db.execute(
        select(ImageSubmission).where(ImageSubmission.id == submission_id)
    )
    submission = result.scalar_one_or_none()
    
    if not submission:
        raise HTTPException(
            status_code=404,
            detail="Submission not found"
        )
    
    return submission 