from setuptools import setup, find_packages

setup(
    name="eurus",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "psycopg2-binary",
        "python-dotenv",
        "pydantic",
        "logfire",
        "sentry-sdk",
    ],
    python_requires=">=3.12",
) 