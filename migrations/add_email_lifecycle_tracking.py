"""
Idempotent migration for email lifecycle tracking fields.

Run from the backend directory:
    python migrations/add_email_lifecycle_tracking.py
"""

import os
import sys

from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import main_engine


TABLE_COLUMNS = {
    "email_events": [
        ("campaign_id", "VARCHAR"),
        ("contact_id", "INTEGER"),
        ("message_id", "VARCHAR"),
        ("created_at", "TIMESTAMP WITH TIME ZONE DEFAULT now()"),
    ],
    "email_logs": [
        ("tenant_id", "VARCHAR"),
        ("message_id", "VARCHAR"),
        ("delivery_status", "VARCHAR"),
        ("complaint_reason", "TEXT"),
        ("unsubscribe_reason", "TEXT"),
        ("provider", "VARCHAR DEFAULT 'aws_ses'"),
        ("retry_count", "INTEGER DEFAULT 0"),
        ("smtp_response", "TEXT"),
        ("ip_address", "VARCHAR"),
        ("user_agent", "TEXT"),
        ("country", "VARCHAR"),
        ("city", "VARCHAR"),
        ("ses_event_data", "JSONB"),
        ("bounced_at", "TIMESTAMP WITH TIME ZONE"),
        ("complaint_at", "TIMESTAMP WITH TIME ZONE"),
        ("failed_at", "TIMESTAMP WITH TIME ZONE"),
        ("unsubscribed_at", "TIMESTAMP WITH TIME ZONE"),
    ],
    "campaigns": [
        ("total_failed", "INTEGER DEFAULT 0"),
        ("total_complained", "INTEGER DEFAULT 0"),
        ("complaint_rate", "DOUBLE PRECISION DEFAULT 0.0"),
    ],
    "suppressions": [
        ("source", "VARCHAR(255)"),
    ],
}

INDEXES = [
    ("email_events", "ix_email_events_campaign_event", "campaign_id, event_type"),
    ("email_events", "ix_email_events_message_event", "message_id, event_type"),
    ("email_logs", "ix_email_logs_message_id", "message_id"),
]


def run():
    with main_engine.begin() as conn:
        for table_name, columns in TABLE_COLUMNS.items():
            for column_name, column_type in columns:
                conn.execute(
                    text(
                        f'ALTER TABLE "{table_name}" '
                        f'ADD COLUMN IF NOT EXISTS "{column_name}" {column_type}'
                    )
                )

        for table_name, index_name, column_expr in INDEXES:
            conn.execute(
                text(
                    f'CREATE INDEX IF NOT EXISTS "{index_name}" '
                    f'ON "{table_name}" ({column_expr})'
                )
            )

    print("Email lifecycle tracking migration completed.")


if __name__ == "__main__":
    run()
