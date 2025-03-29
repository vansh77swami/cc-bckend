import aiosqlite
import os
from datetime import datetime
from typing import List, Optional, Dict

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        
    async def init_db(self):
        """Initialize the database and create tables if they don't exist."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS image_submissions (
                    id TEXT PRIMARY KEY,
                    email TEXT NOT NULL,
                    original_image_path TEXT NOT NULL,
                    result_image_path TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()

    async def create_submission(self, submission_id: str, email: str, image_path: str) -> Dict:
        """Create a new image submission."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            await db.execute(
                """
                INSERT INTO image_submissions (id, email, original_image_path, status)
                VALUES (?, ?, ?, ?)
                """,
                (submission_id, email, image_path, "pending")
            )
            await db.commit()
            
            # Get the created submission
            cursor = await db.execute(
                "SELECT * FROM image_submissions WHERE id = ?",
                (submission_id,)
            )
            return dict(await cursor.fetchone())

    async def get_submission(self, submission_id: str) -> Optional[Dict]:
        """Get a submission by ID."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM image_submissions WHERE id = ?",
                (submission_id,)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def get_all_submissions(self) -> List[Dict]:
        """Get all submissions ordered by creation date."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM image_submissions ORDER BY created_at DESC"
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def update_submission_status(self, submission_id: str, status: str, result_path: Optional[str] = None):
        """Update submission status and optionally the result image path."""
        async with aiosqlite.connect(self.db_path) as db:
            if result_path:
                await db.execute(
                    """
                    UPDATE image_submissions 
                    SET status = ?, result_image_path = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (status, result_path, submission_id)
                )
            else:
                await db.execute(
                    """
                    UPDATE image_submissions 
                    SET status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (status, submission_id)
                )
            await db.commit()

    async def delete_submission(self, submission_id: str) -> bool:
        """Delete a submission and return True if successful."""
        async with aiosqlite.connect(self.db_path) as db:
            # First get the submission to get the image path
            cursor = await db.execute(
                "SELECT original_image_path FROM image_submissions WHERE id = ?",
                (submission_id,)
            )
            row = await cursor.fetchone()
            if not row:
                return False
            
            # Delete the database record
            await db.execute(
                "DELETE FROM image_submissions WHERE id = ?",
                (submission_id,)
            )
            await db.commit()
            
            # Return True to indicate successful deletion
            return True 