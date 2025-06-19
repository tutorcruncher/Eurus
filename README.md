# Eurus - LessonSpace Integration Service
````
     ___           ___           ___           ___           ___     
    /  /\         /__/\         /  /\         /__/\         /  /\    
   /  /:/_        \  \:\       /  /::\        \  \:\       /  /:/_   
  /  /:/ /\        \  \:\     /  /:/\:\        \  \:\     /  /:/ /\  
 /  /:/ /:/_   ___  \  \:\   /  /:/~/:/    ___  \  \:\   /  /:/ /::\ 
/__/:/ /:/ /\ /__/\  \__\:\ /__/:/ /:/___ /__/\  \__\:\ /__/:/ /:/\:\
\  \:\/:/ /:/ \  \:\ /  /:/ \  \:\/:::::/ \  \:\ /  /:/ \  \:\/:/~/:/
 \  \::/ /:/   \  \:\  /:/   \  \::/~~~~   \  \:\  /:/   \  \::/ /:/ 
  \  \:\/:/     \  \:\/:/     \  \:\        \  \:\/:/     \__\/ /:/  
   \  \::/       \  \::/       \  \:\        \  \::/        /__/:/   
    \__\/         \__\/         \__\/         \__\/         \__\/    
 
````

[![codecov](https://codecov.io/gh/your-username/eurus/branch/main/graph/badge.svg)](https://codecov.io/gh/your-username/eurus)

Named after the Greek god of the east wind, Eurus serves as a gateway between lesson scheduling and actual virtual lessons,

A FastAPI service that integrates with LessonSpace to create and manage virtual learning spaces.

## Features

- Create virtual learning spaces with tutor and student access
- Generate unique, authenticated URLs for each participant
- Comprehensive API documentation with Swagger UI
- Automatic documentation generation

## Prerequisites

- Python 3.12+
- LessonSpace API credentials

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd eurus
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
# Make sure you have uv installed (https://docs.astral.sh/uv/)
curl -Ls https://astral.sh/uv/install.sh | sh

# Runtime dependencies
uv pip install -e .

# Development extras
uv pip install -e . --group dev
```

4. Create a `.env` file in the project root:
```env
APP_NAME=Eurus
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

## API Documentation

The API documentation is automatically generated from the FastAPI application and provides:

- Interactive API documentation with Swagger UI
- Request/response examples
- Authentication requirements
- Schema definitions
- API endpoints and their parameters

### Viewing Documentation

There are two ways to access the API documentation:

1. **Live Documentation** (when service is running):
   - Open http://{BASE_URL}/docs in your browser
   - This shows the current state of your API

2. **Static Documentation** (for reference/versioning):
   ```bash
   # Generate the documentation
   make docs
   
   # View the static documentation
   make serve-docs
   ```
   Then open http://localhost:8080 in your browser



## Development

### Running Tests

```bash
make test
```

### Code Style

The project uses Ruff for code formatting and linting:
```bash
make format
make lint
```

## Architecture

- **FastAPI**: Modern, fast web framework for building APIs
- **Logfire**: Structured logging with sensitive data scrubbing
- **Swagger UI**: Interactive API documentation
