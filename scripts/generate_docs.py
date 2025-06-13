import json
import os
from fastapi.openapi.utils import get_openapi
from app.main import app


def generate_openapi_schema():
    """Generate OpenAPI schema from FastAPI app"""
    openapi_schema = get_openapi(
        title=app.title,
        version='1.0.0',
        description='Eurus API Documentation',
        routes=app.routes,
    )

    # Create docs directory if it doesn't exist
    os.makedirs('docs', exist_ok=True)

    # Save the schema
    with open('docs/openapi.json', 'w') as f:
        json.dump(openapi_schema, f, indent=2)

    print('OpenAPI schema generated successfully at docs/openapi.json')


if __name__ == '__main__':
    generate_openapi_schema()
