from sqlalchemy import text


CAMPAIGN_COLUMNS = [
    ("current_step", "INTEGER DEFAULT 1"),
    ("subject_line", "VARCHAR"),
    ("preview_text", "VARCHAR"),
    ("template_id", "VARCHAR"),
    ("sender_identity_id", "VARCHAR"),
    ("audience_list_ids", "JSONB"),
    ("exclude_list_ids", "JSONB"),
    ("estimated_recipients", "INTEGER DEFAULT 0"),
    ("suppressed_count", "INTEGER DEFAULT 0"),
    ("send_mode", "VARCHAR"),
    ("scheduled_at", "TIMESTAMP WITH TIME ZONE"),
    ("timezone", "VARCHAR"),
    ("email_sent_at", "TIMESTAMP WITH TIME ZONE"),
    ("total_sent", "INTEGER DEFAULT 0"),
    ("total_delivered", "INTEGER DEFAULT 0"),
    ("total_opened", "INTEGER DEFAULT 0"),
    ("total_clicked", "INTEGER DEFAULT 0"),
    ("total_bounced", "INTEGER DEFAULT 0"),
    ("total_failed", "INTEGER DEFAULT 0"),
    ("total_complained", "INTEGER DEFAULT 0"),
    ("total_unsubscribed", "INTEGER DEFAULT 0"),
    ("open_rate", "DOUBLE PRECISION DEFAULT 0.0"),
    ("click_rate", "DOUBLE PRECISION DEFAULT 0.0"),
    ("delivery_rate", "DOUBLE PRECISION DEFAULT 0.0"),
    ("bounce_rate", "DOUBLE PRECISION DEFAULT 0.0"),
    ("complaint_rate", "DOUBLE PRECISION DEFAULT 0.0"),
]


EMAIL_LOG_COLUMNS = [
    ("campaign_id", "INTEGER"),
    ("contact_id", "INTEGER"),
    ("recipient_name", "VARCHAR"),
    ("recipient_email", "VARCHAR"),
    ("recipient_phone", "VARCHAR"),
    ("subject", "VARCHAR"),
    ("template_name", "VARCHAR"),
    ("campaign_name", "VARCHAR"),
    ("status", "VARCHAR DEFAULT 'sent'"),
    ("opens", "INTEGER DEFAULT 0"),
    ("clicks", "INTEGER DEFAULT 0"),
    ("ses_message_id", "VARCHAR"),
    ("message_id", "VARCHAR"),
    ("delivery_status", "VARCHAR"),
    ("bounce_reason", "TEXT"),
    ("complaint_reason", "TEXT"),
    ("error_message", "TEXT"),
    ("unsubscribe_reason", "TEXT"),
    ("provider", "VARCHAR DEFAULT 'aws_ses'"),
    ("retry_count", "INTEGER DEFAULT 0"),
    ("smtp_response", "TEXT"),
    ("ip_address", "VARCHAR"),
    ("user_agent", "TEXT"),
    ("country", "VARCHAR"),
    ("city", "VARCHAR"),
    ("ses_event_data", "JSONB"),
    ("sent_at", "TIMESTAMP WITH TIME ZONE DEFAULT now()"),
    ("delivered_at", "TIMESTAMP WITH TIME ZONE"),
    ("opened_at", "TIMESTAMP WITH TIME ZONE"),
    ("clicked_at", "TIMESTAMP WITH TIME ZONE"),
    ("bounced_at", "TIMESTAMP WITH TIME ZONE"),
    ("complaint_at", "TIMESTAMP WITH TIME ZONE"),
    ("failed_at", "TIMESTAMP WITH TIME ZONE"),
    ("unsubscribed_at", "TIMESTAMP WITH TIME ZONE"),
    ("created_at", "TIMESTAMP WITH TIME ZONE DEFAULT now()"),
]


def add_missing_columns(engine, table_name, columns):
    with engine.begin() as connection:
        for column_name, column_type in columns:
            connection.execute(
                text(
                    f'ALTER TABLE "{table_name}" '
                    f'ADD COLUMN IF NOT EXISTS "{column_name}" {column_type}'
                )
            )


def sync_main_campaign_table(engine):
    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))
        connection.execute(
            text(
                'ALTER TABLE "campaigns" '
                'ALTER COLUMN "id" SET DEFAULT gen_random_uuid()'
            )
        )
        connection.execute(
            text('ALTER TABLE "campaigns" ALTER COLUMN "workspace_id" DROP NOT NULL')
        )
        connection.execute(
            text('ALTER TABLE "campaigns" ALTER COLUMN "created_by_user_id" DROP NOT NULL')
        )
        connection.execute(
            text(
                'ALTER TABLE "campaigns" '
                'ALTER COLUMN "created_at" SET DEFAULT now()'
            )
        )
        connection.execute(
            text(
                'ALTER TABLE "campaigns" '
                'ALTER COLUMN "updated_at" SET DEFAULT now()'
            )
        )
        connection.execute(
            text('ALTER TABLE "campaigns" DROP CONSTRAINT IF EXISTS "campaigns_template_id_fkey"')
        )
        connection.execute(
            text('ALTER TABLE "campaigns" DROP CONSTRAINT IF EXISTS "campaigns_sender_identity_id_fkey"')
        )
        connection.execute(
            text(
                'ALTER TABLE "campaigns" ALTER COLUMN "template_id" '
                'TYPE VARCHAR USING "template_id"::text'
            )
        )
        connection.execute(
            text(
                'ALTER TABLE "campaigns" ALTER COLUMN "sender_identity_id" '
                'TYPE VARCHAR USING "sender_identity_id"::text'
            )
        )

def sync_campaign_schema(main_engine, log_engine):
    add_missing_columns(main_engine, "campaigns", CAMPAIGN_COLUMNS)
    add_missing_columns(log_engine, "email_logs", EMAIL_LOG_COLUMNS)
    sync_main_campaign_table(main_engine)
    with log_engine.begin() as connection:
        connection.execute(
            text(
                'ALTER TABLE "email_logs" ALTER COLUMN "campaign_id" '
                'TYPE VARCHAR USING "campaign_id"::text'
            )
        )
