# Janus

A FastAPI-based service for managing Lessonspace integrations.

## Prerequisites

- Python 3.12 or higher
- Redis server
- Lessonspace API credentials

## Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   make install-dev
   ```

3. Create a `.env` file with the following content:
   ```
   APP_NAME=Janus
   DEBUG=True
   REDIS_URL=redis://localhost:6379/0
   LESSONSPACE_API_KEY=your_api_key_here
   LESSONSPACE_API_URL=https://api.thelessonspace.com/v2
   SENTRY_DSN=
   ```

4. Start Redis (if not already running):
   ```bash
   # On Ubuntu/Debian
   sudo service redis-server start
   
   # On macOS with Homebrew
   brew services start redis
   
   # On Windows
   redis-server
   ```

5. Run the service:
   ```bash
   make run
   ```

The service will be available at http://localhost:8000

## Development

### Available Make Commands

- `make install`: Install production dependencies
- `make install-dev`: Install development dependencies
- `make format`: Format code using ruff
- `make lint`: Run linting checks
- `make test`: Run tests
- `make run`: Start the service
- `make clean`: Clean up temporary files and virtual environment

### API Documentation

Once the service is running, you can access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Health Check

The service includes a health check endpoint at `/health` that returns:
```json
{
    "status": "healthy"
}
```

## Features

- Create/retrieve Lessonspace spaces by lesson ID
- Redis caching for space URLs
- Sentry integration for error tracking
- Logfire for structured logging

## API Usage

### Create/Get Space

```bash
curl -X POST http://localhost:8000/api/v1/spaces \
  -H "Content-Type: application/json" \
  -d '{
    "lesson_id": "lesson-123",
    "teacher_name": "John Doe",
    "student_name": "Jane Smith"
  }'
```

Response:
```json
{
  "space_url": "https://lessonspace.com/space/123",
  "space_id": "123",
  "lesson_id": "lesson-123"
}
``` 