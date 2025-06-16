from sqlalchemy import create_engine, text
from settings import get_settings

settings = get_settings()


def migrate():
    """Add unique constraint to lesson_id in transcripts table."""
    engine = create_engine(settings.database_url)

    with engine.connect() as conn:
        # Start transaction
        with conn.begin():
            # First, remove duplicates by keeping only the most recent transcript for each lesson_id
            conn.execute(
                text("""
                DELETE FROM transcripts a
                USING (
                    SELECT lesson_id, MAX(updated_at) as max_updated_at
                    FROM transcripts
                    GROUP BY lesson_id
                ) b
                WHERE a.lesson_id = b.lesson_id
                AND a.updated_at < b.max_updated_at;
            """)
            )

            # Drop existing index if it exists
            conn.execute(text('DROP INDEX IF EXISTS idx_transcripts_lesson_id;'))

            # Add unique constraint
            conn.execute(
                text("""
                ALTER TABLE transcripts 
                ADD CONSTRAINT transcripts_lesson_id_key UNIQUE (lesson_id);
            """)
            )

            # Create unique index
            conn.execute(
                text("""
                CREATE UNIQUE INDEX idx_transcripts_lesson_id 
                ON transcripts(lesson_id);
            """)
            )

            print('Successfully added unique constraint to lesson_id')


if __name__ == '__main__':
    print('Running migration to add unique constraint...')
    migrate()
    print('Migration completed successfully!')
