# Janus - LessonSpace Integration Service

A FastAPI service that integrates with LessonSpace to create and manage virtual learning spaces.

## Features

- Create virtual learning spaces with tutor and student access
- Generate unique, authenticated URLs for each participant
- JWT-based authentication for secure space access
- Redis caching for improved performance
- Comprehensive logging with Logfire integration

## Prerequisites

- Python 3.12+
- Redis server
- LessonSpace API credentials

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd janus
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:
```env
APP_NAME=Janus
DEBUG=True
REDIS_URL=redis://localhost:6379/0
LESSONSPACE_API_KEY=your_api_key_here
LESSONSPACE_API_URL=https://api.thelessonspace.com/v2
SENTRY_DSN=your_sentry_dsn_here  # Optional
```

## Running the Service

Start the service using:
```bash
make run
```

Or directly with uvicorn:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Usage

### Create a Space

```bash
curl -X POST http://localhost:8000/api/space \
  -H "Content-Type: application/json" \
  -d '{
    "lesson_id": "your-lesson-id",
    "tutors": [
      {
        "name": "Tutor Name",
        "email": "tutor@example.com",
        "is_leader": true
      }
    ],
    "students": [
      {
        "name": "Student Name",
        "email": "student@example.com"
      }
    ]
  }'
```

Response:
```json
{
  "space_id": "unique-space-id",
  "lesson_id": "your-lesson-id",
  "tutor_spaces": [
    {
      "email": "tutor@example.com",
      "name": "Tutor Name",
      "role": "tutor",
      "space_url": "https://thelessonspace.com/space/unique-space-id?token=tutor-jwt-token"
    }
  ],
  "student_spaces": [
    {
      "email": "student@example.com",
      "name": "Student Name",
      "role": "student",
      "space_url": "https://thelessonspace.com/space/unique-space-id?token=student-jwt-token"
    }
  ]
}
```

Each participant receives a unique space URL containing their JWT token, which:
- Authenticates them in the space
- Sets their role (tutor/student)
- Controls their permissions (e.g., tutors can lead if is_leader is true)

## Development

### Running Tests

```bash
make test
```

### Code Style

The project uses Black for code formatting:
```bash
make format
```

## Architecture

- **FastAPI**: Modern, fast web framework for building APIs
- **Redis**: Caching layer for improved performance
- **Logfire**: Structured logging and monitoring
- **JWT**: Secure authentication for space access

## License

[Your License Here] 
