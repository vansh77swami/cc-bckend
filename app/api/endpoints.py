from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.image_service import save_upload_file, create_image_submission, get_submission_status
from app.schemas.image_submission import ImageSubmissionResponse, ImageSubmissionStatus
from typing import Optional

router = APIRouter()

@router.post("/submit-image", response_model=ImageSubmissionStatus)
async def submit_image(
    email: str = Form(...),
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Submit an image for processing."""
    try:
        # Save the uploaded file
        file_path = await save_upload_file(image)
        
        # Create submission record
        submission = await create_image_submission(db, email, file_path)
        
        return ImageSubmissionStatus(
            submission_id=submission.id,
            status="received",
            result_url=None
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/status/{submission_id}", response_model=ImageSubmissionStatus)
async def get_status(
    submission_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get the status of an image submission."""
    submission = await get_submission_status(db, submission_id)
    
    return ImageSubmissionStatus(
        submission_id=submission.id,
        status=submission.status,
        result_url=submission.result_image_path if submission.status == "completed" else None
    ) 