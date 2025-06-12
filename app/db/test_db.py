from app.db.session import SessionLocal
from app.dal.transcript import create_transcript


def test_db_connection():
    """Test the database connection by creating a test transcript."""
    db = SessionLocal()
    try:
        # Create a test transcript
        transcript = create_transcript(
            db=db, lesson_id="test-lesson-123", transcription={"test": "data"}
        )
        print(f"Successfully created test transcript with ID: {transcript.id}")
    except Exception as e:
        print(f"Error testing database connection: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    test_db_connection()
