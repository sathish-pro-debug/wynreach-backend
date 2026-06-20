from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import automation_webhook
from app.routers import webhook_proxy
from app.routers import ai_template

# =====================================================
# DATABASE
# =====================================================
from app.database import Base, LogBase, main_engine
from app.db.schema_sync import sync_campaign_schema
from app.scheduler.campaign_scheduler import start_scheduler
from app.routers.track_open import router as track_open_router
from app.routers.track_click import router as track_click_router
from app.routers.s3_upload import router as s3_upload_router
from app.routers.r2_upload import router as r2_upload_router
from app.routers.sequence_scheduler import router as sequence_scheduler_router

# =====================================================
# MODELS
# =====================================================
from app.models import (
    user,
    chatbot,
    sender_identity,
    lists,
    Suppression,
    contact,
    campaign,
    template,
    notification,
)

# =====================================================
# ROUTERS
# =====================================================
from app.routers import (
    auth,
    users,
    chatbot as chatbot_router,
    lists as lists_router,
    campaigns,
    team,
    sender_identity as sender_identity_router,
)
from app.routers import automation_webhook
from app.routers import automation
from app.routers import webhook_proxy
from app.routers.dashboard import router as dashboard_router
from app.routers.notifications import router as notifications_router
from app.routers.templates import router as templates_router
from app.routers.contact import router as contacts_router
from app.routers.suppression import router as suppression_router
from app.routers.inbox import router as inbox_router
from app.routers.whatsapp import router as whatsapp_router
from app.routers.email_routes import router as email_router
from app.routers.ses_webhooks import router as webhook_router
from app.routers.unsubscribe import router as unsubscribe_router
from app.routers.email_logs import router as email_logs_router
from app.routers.messagelog import router as messagelog_router
from app.routers.notification_items import router as notification_items_router

# =====================================================
# OPTIONAL ROUTERS
# =====================================================
HAS_AUTOMATION = True
try:
    from app.routers.automation import router as automation_router
    from app.routers.analytics import router as analytics_router
    print("✅ Automation router loaded")
except ImportError:
    HAS_AUTOMATION = False
    print("⚠️ Automation router missing")

# =====================================================
# CREATE TABLES (best-effort)
# =====================================================
try:
    Base.metadata.create_all(bind=main_engine)
    LogBase.metadata.create_all(bind=main_engine)
except Exception as e:
    # If DB is unreachable at import time we don't want the whole app to crash.
    # Log and continue; startup will attempt migrations in a guarded way.
    print(f"⚠️ Skipping create_all due to DB error: {e}")

# =====================================================
# SYNC SCHEMA
# =====================================================
try:
    sync_campaign_schema(main_engine, main_engine)
    print("✅ Campaign schema synced")
except Exception as e:
    print(f"⚠️ Schema sync failed: {e}")

# =====================================================
# MIGRATIONS
# =====================================================
try:
    from sqlalchemy import text

    with main_engine.connect() as conn:
        result = conn.execute(
            text(
                "SELECT column_name FROM information_schema.columns WHERE table_name = 'contacts' AND column_name = 'is_whatsapp'"
            )
        )
        if not result.fetchone():
            conn.execute(
                text(
                    "ALTER TABLE contacts ADD COLUMN is_whatsapp BOOLEAN DEFAULT FALSE"
                )
            )
            conn.commit()
            print("✅ is_whatsapp column added!")
        else:
            print("✅ is_whatsapp column already exists")
except Exception as e:
    print(f"⚠️ Migration failed: {e}")

try:
    from sqlalchemy import text

    with main_engine.connect() as conn:
        check = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'suppressions' 
            AND column_name = 'source'
        """))
        exists = check.fetchone()
        if not exists:
            conn.execute(text("""
                ALTER TABLE suppressions 
                ADD COLUMN source VARCHAR(255)
            """))
            conn.commit()
            print("✅ source column added to suppressions!")
        else:
            print("✅ suppressions source column already exists")
except Exception as e:
    print(f"⚠️ suppressions migration failed: {e}")

try:
    from sqlalchemy import text

    with main_engine.connect() as conn:
        result = conn.execute(
            text(
                "SELECT column_name FROM information_schema.columns WHERE table_name = 'message_logs' AND column_name = 'source'"
            )
        )
        if not result.fetchone():
            conn.execute(
                text(
                    "ALTER TABLE message_logs ADD COLUMN source VARCHAR DEFAULT 'campaign'"
                )
            )
            conn.commit()
            print("✅ source column added to message_logs!")
        else:
            print("✅ source column already exists")
except Exception as e:
    print(f"⚠️ source migration failed: {e}")

try:
    from sqlalchemy import text

    with main_engine.connect() as conn:
        result = conn.execute(
            text(
                "SELECT column_name FROM information_schema.columns WHERE table_name = 'message_logs' AND column_name = 'direction'"
            )
        )
        if not result.fetchone():
            conn.execute(
                text(
                    "ALTER TABLE message_logs ADD COLUMN direction VARCHAR DEFAULT 'outgoing'"
                )
            )
            conn.commit()
            print("✅ direction column added to message_logs!")
        else:
            print("✅ direction column already exists")
except Exception as e:
    print(f"⚠️ direction migration failed: {e}")

try:
    from sqlalchemy import text

    with main_engine.connect() as conn:
        for col_name, col_type in [("campaign_id", "VARCHAR"), ("contact_id", "INTEGER"), ("message_id", "VARCHAR"), ("created_at", "TIMESTAMP DEFAULT now()")]:
            check = conn.execute(text(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'email_events' 
                AND column_name = '{col_name}'
            """))
            if not check.fetchone():
                conn.execute(text(f"ALTER TABLE email_events ADD COLUMN {col_name} {col_type}"))
                conn.commit()
                print(f"✅ {col_name} column added to email_events!")
            else:
                print(f"✅ {col_name} column already exists on email_events")

        for col_name, col_type in [("total_failed", "INTEGER DEFAULT 0"), ("total_complained", "INTEGER DEFAULT 0"), ("complaint_rate", "DOUBLE PRECISION DEFAULT 0.0")]:
            check = conn.execute(text(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'campaigns' 
                AND column_name = '{col_name}'
            """))
            if not check.fetchone():
                conn.execute(text(f"ALTER TABLE campaigns ADD COLUMN {col_name} {col_type}"))
                conn.commit()
                print(f"✅ {col_name} column added to campaigns!")
            else:
                print(f"✅ {col_name} column already exists on campaigns")
except Exception as e:
    print(f"⚠️ email_events and campaigns migration failed: {e}")

# =====================================================
# FASTAPI APP
# =====================================================
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Middleware for SQL counting and per-route request counts
try:
    from app.middleware.metrics import SQLCountMiddleware

    app.add_middleware(SQLCountMiddleware)
    print("✅ SQLCountMiddleware registered")
except Exception as e:
    print(f"⚠️ Failed to register SQLCountMiddleware: {e}")

# =====================================================
# CORS
# =====================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://reach.wynsync.tech",
        "https://wynreach-frontend.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# BASIC ROUTERS
# =====================================================
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(dashboard_router, prefix="/api", tags=["Dashboard"])

# =====================================================
# CAMPAIGN ROUTERS
# =====================================================
app.include_router(campaigns.router, prefix="/api/campaigns", tags=["Campaigns"])
app.include_router(templates_router, prefix="/api/templates", tags=["Templates"])
app.include_router(inbox_router, prefix="/api/inbox", tags=["Inbox"])
app.include_router(
    notifications_router, prefix="/api/notifications", tags=["Notifications"]
)

# =====================================================
# CONTACT ROUTERS
# =====================================================
app.include_router(lists_router.router, prefix="/api/lists", tags=["Lists"])
app.include_router(contacts_router, prefix="/api/contacts", tags=["Contacts"])
app.include_router(
    suppression_router, prefix="/api/suppressions", tags=["Suppressions"]
)

# =====================================================
# CHAT + AUTOMATION
# =====================================================
app.include_router(chatbot_router.router, prefix="/api/chatbots", tags=["Chatbots"])
if HAS_AUTOMATION:
    app.include_router(automation_router, prefix="/api/automation", tags=["Automation"])
    app.include_router(analytics_router, prefix="/api/analytics", tags=["Analytics"])

# =====================================================
# SENDER + EMAIL
# =====================================================
app.include_router(
    sender_identity_router.router,
    prefix="/api/sender-identity",
    tags=["Sender Identity"],
)
app.include_router(whatsapp_router, prefix="/api/whatsapp", tags=["WhatsApp"])
app.include_router(email_router, prefix="/api/emails", tags=["Emails"])
app.include_router(webhook_router, prefix="/api/webhooks", tags=["Webhooks"])
app.include_router(unsubscribe_router, prefix="/api/unsubscribe", tags=["Unsubscribe"])
app.include_router(email_logs_router, prefix="/api/email-logs", tags=["Email Logs"])
app.include_router(messagelog_router, prefix="/api/messagelog", tags=["Message Logs"])

# ✅ Only ONE registration for notification_items
app.include_router(
    notification_items_router,
    prefix="/api/notification-items",
    tags=["Notification Items"],
)

# ✅ Only ONE registration for automation_webhook
app.include_router(automation_webhook.router)
app.include_router(webhook_proxy.router)
app.include_router(automation_webhook.router)
try:
    from app.routers.metrics import router as metrics_router
    app.include_router(metrics_router, prefix="/api/metrics", tags=["Metrics"])
    print("✅ Metrics router loaded")
except Exception as e:
    print(f"⚠️ Metrics router failed to load: {e}")

# =====================================================
# TEAM ROUTER
# =====================================================
app.include_router(team.router, prefix="/api/team", tags=["Team Management"])
app.include_router(track_open_router, prefix="/api")
app.include_router(track_click_router, prefix="/api")
app.include_router(s3_upload_router, prefix="/api/uploads", tags=["Uploads"])
app.include_router(r2_upload_router, prefix="/api/uploads", tags=["Uploads"])
app.include_router(sequence_scheduler_router, tags=["Sequence Scheduler"])
app.include_router(automation.router, tags=["automation"])
app.include_router(ai_template.router)
# =====================================================
# ROOT ENDPOINTS
# =====================================================
@app.get("/")
async def root():
    return {"message": "WynReach API running", "status": "active"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# =====================================================
# STARTUP EVENTS
# =====================================================
@app.on_event("startup")
async def startup_event():
    """Start campaign scheduler and load sequences on startup"""
    # Start campaign scheduler
    start_scheduler()
    print("✅ Campaign Scheduler Started")
    
    # Load sequences from database
    try:
        from app.database import get_main_db
        from app.routers.automation import load_sequences_from_db
        
        db = next(get_main_db())
        load_sequences_from_db(db)
        db.close()
        print("✅ Sequences loaded from database on startup")
    except Exception as e:
        print(f"⚠️ Could not load sequences from database: {str(e)}")

# =====================================================
# STARTUP LOGS
# =====================================================
print("=" * 60)
print("🚀 WynReach Backend Started")
print("=" * 60)
print("✅ Auth Router")
print("✅ Users Router")
print("✅ Dashboard Router")
print("✅ Campaign Router")
print("✅ Template Router")
print("✅ Inbox Router")
print("✅ Notification Router")
print("✅ Lists Router")
print("✅ Contacts Router")
print("✅ Suppression Router")
print("✅ Chatbot Router")
print("✅ Sender Identity Router")
print("✅ WhatsApp Router")
print("✅ Email Router")
print("✅ Webhook Router")
print("✅ Unsubscribe Router")
print("✅ Email Logs Router")
print("✅ Team Router")
if HAS_AUTOMATION:
    print("✅ Automation Router")
    print("✅ Analytics Router")
print("=" * 60)