import psycopg2
import os
from app.core.config import get_settings

settings = get_settings()


def setup_test_db():
    # Connect to postgres to create/drop database
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="waffle",
        host="localhost",
        port="5432",
    )
    conn.autocommit = True
    cur = conn.cursor()

    # Drop database if it exists
    cur.execute("DROP DATABASE IF EXISTS eurus_test")

    # Create database
    cur.execute("CREATE DATABASE eurus_test")

    # Close connection to postgres
    cur.close()
    conn.close()

    # Connect to the new database and create schema
    conn = psycopg2.connect(
        dbname="eurus_test",
        user="postgres",
        password="waffle",
        host="localhost",
        port="5432",
    )
    cur = conn.cursor()

    # Read and execute schema.sql
    schema_path = os.path.join(os.path.dirname(__file__), "..", "schema.sql")
    with open(schema_path, "r") as f:
        schema = f.read()
        cur.execute(schema)

    # Commit and close
    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    setup_test_db()
