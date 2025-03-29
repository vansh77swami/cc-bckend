# https://creative-clone-journey-9zkxj8nqp-vs465958gmailcoms-projects.vercel.app/, jing@grows.live

from fastapi import FastAPI, Request, File, Form, UploadFile, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
import aiofiles
import os
import uuid
from datetime import datetime
from app.db.database import Database
from app.core.config import get_settings
import logging
from typing import Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize settings
settings = get_settings()

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://creative-clone-journey-9zkxj8nqp-vs465958gmailcoms-projects.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup API key security
api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Could not validate API key"
        )
    return api_key

# Setup static files and templates
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
templates = Jinja2Templates(directory="app/templates")

# Initialize database
db = Database("data/image_processing.db")

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    try:
        await db.init_db()
        os.makedirs("uploads", exist_ok=True)
        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}")
        raise

@app.get("/")
async def root(request: Request):
    """Render the main page with all submissions."""
    try:
        submissions = await db.get_all_submissions()
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "submissions": submissions,
                "upload_dir": "uploads"
            }
        )
    except Exception as e:
        logger.error(f"Error in root endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/submit-image")
async def submit_image(
    email: str = Form(...),
    image: UploadFile = File(...),
    api_key: str = Depends(verify_api_key)
):
    """Handle image submission."""
    try:
        # Validate file size
        content = await image.read()
        if len(content) > settings.MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum allowed ({settings.MAX_IMAGE_SIZE} bytes)"
            )
        
        # Validate file type
        if image.content_type not in settings.ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed types: {settings.ALLOWED_IMAGE_TYPES}"
            )
        
        # Generate unique ID and filename
        submission_id = str(uuid.uuid4())
        file_extension = os.path.splitext(image.filename)[1]
        file_name = f"{submission_id}{file_extension}"
        file_path = os.path.join("uploads", file_name)
        
        # Save the file
        async with aiofiles.open(file_path, 'wb') as out_file:
            await out_file.write(content)
        
        # Create database entry
        submission = await db.create_submission(
            submission_id=submission_id,
            email=email,
            image_path=file_path
        )
        
        logger.info(f"New submission created: {submission_id}")
        return JSONResponse({
            "submission_id": submission_id,
            "status": "received",
            "message": "Image received and processing"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in submit_image: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )

@app.get("/api/status/{submission_id}")
async def get_status(
    submission_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Get the status of a submission."""
    try:
        submission = await db.get_submission(submission_id)
        if not submission:
            raise HTTPException(
                status_code=404,
                detail="Submission not found"
            )
        
        return {
            "submission_id": submission["id"],
            "status": submission["status"],
            "result_url": submission["result_image_path"] if submission["status"] == "completed" else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/api/submissions/{submission_id}")
async def delete_submission(
    submission_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Delete a submission and its associated image."""
    try:
        success = await db.delete_submission(submission_id)
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Submission not found"
            )
        logger.info(f"Submission deleted: {submission_id}")
        return {"message": "Submission deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in delete_submission: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error") 