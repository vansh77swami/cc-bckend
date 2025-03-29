# Image Processing API

A FastAPI backend service for handling image uploads and processing.

## Features

- Image upload with email association
- Async processing
- Status tracking
- PostgreSQL database integration
- File size and type validation
- Docker support

## Running with Docker (Recommended)

1. Make sure you have Docker and Docker Compose installed on your system.

2. Build and start the services:
```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000` and the interactive API documentation at `http://localhost:8000/docs`.

To stop the services:
```bash
docker-compose down
```

To stop the services and remove all data (including the database):
```bash
docker-compose down -v
```

## Manual Setup (Alternative)

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy the environment template and update with your values:
```bash
cp .env.example .env
```

4. Create the database:
```bash
# Using psql
createdb image_processing_db
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

- `POST /api/submit-image`
  - Parameters:
    - `email` (form field)
    - `image` (file upload)
  - Returns submission ID and status

- `GET /api/status/{submission_id}`
  - Returns current status and result URL if processing is complete

## Development

The application uses:
- FastAPI for the web framework
- SQLAlchemy for database operations
- Pydantic for data validation
- PostgreSQL as the database
- Docker for containerization

## Directory Structure

```
.
├── app/
│   ├── api/
│   │   └── endpoints.py
│   ├── core/
│   │   └── config.py
│   ├── db/
│   │   └── session.py
│   ├── models/
│   │   └── image_submission.py
│   ├── schemas/
│   │   └── image_submission.py
│   ├── services/
│   │   └── image_service.py
│   └── main.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## Docker Volumes

The application uses two Docker volumes:
- `postgres_data`: Persists PostgreSQL database data
- `./uploads`: Mounts the local uploads directory to the container for image storage

## Environment Variables

When running with Docker, the environment variables are set in the `docker-compose.yml` file. For manual setup, you'll need to set them in the `.env` file. 