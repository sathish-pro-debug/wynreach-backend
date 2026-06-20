# Run this migration script to add the email_addresses table
from sqlalchemy import create_engine, MetaData, Table, Column, String, DateTime, Integer, Boolean, Text
from sqlalchemy.sql import func
import uuid

def upgrade():
    engine = create_engine("your_database_url")  # Replace with your DB URL
    metadata = MetaData()
    
    email_addresses = Table(
        'email_addresses', metadata,
        Column('id', String(50), primary_key=True, default=lambda: str(uuid.uuid4())),
        Column('user_id', String(50), nullable=False, index=True),
        Column('domain_id', String(50), nullable=False, index=True),
        Column('email', String(255), unique=True, nullable=False, index=True),
        Column('status', String(20), default='active'),
        Column('created_at', DateTime(timezone=True), server_default=func.now())
    )
    
    # Also add dmarc_status to email_domains if not exists
    email_domains = Table('email_domains', metadata, autoload_with=engine)
    
    metadata.create_all(engine)
    
    # Check if dmarc_status column exists, if not add it
    from sqlalchemy import inspect
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns('email_domains')]
    
    if 'dmarc_status' not in columns:
        with engine.connect() as conn:
            conn.execute("ALTER TABLE email_domains ADD COLUMN dmarc_status VARCHAR(20) DEFAULT 'pending'")
            conn.commit()

if __name__ == "__main__":
    upgrade()