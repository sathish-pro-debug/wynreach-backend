# backend/app/database.py
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

main_engine = create_engine(
    settings.MAIN_DB_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=20,
    max_overflow=40,
    pool_timeout=60,
    connect_args={
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
        "sslmode": "require",
        "connect_timeout": 10,
    },
)

MainSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=main_engine)

# Both Base and LogBase point to same DB
Base = declarative_base()
LogBase = declarative_base()

def get_main_db():
    import time
    from sqlalchemy.exc import OperationalError

    attempts = 3
    last_exc = None
    for attempt in range(attempts):
        try:
            db = MainSessionLocal()
            break
        except OperationalError as e:
            last_exc = e
            backoff = 0.5 * (2 ** attempt)
            time.sleep(backoff)
    else:
        # all attempts failed
        raise last_exc

    try:
        yield db
    finally:
        try:
            db.close()
        except Exception:
            pass

# get_log_db also uses main_engine now
def get_log_db():
    import time
    from sqlalchemy.exc import OperationalError

    attempts = 3
    last_exc = None
    for attempt in range(attempts):
        try:
            db = MainSessionLocal()
            break
        except OperationalError as e:
            last_exc = e
            backoff = 0.5 * (2 ** attempt)
            time.sleep(backoff)
    else:
        raise last_exc

    try:
        yield db
    finally:
        try:
            db.close()
        except Exception:
            pass


# Optional lightweight SQL logging for debug environments
if settings.DEBUG:
    import logging
    import time
    logger = logging.getLogger("sqlalchemy.engine")

    @event.listens_for(main_engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        conn.info.setdefault("query_start_time", []).append(time.time())

    @event.listens_for(main_engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        start = conn.info.get("query_start_time", []).pop(-1) if conn.info.get("query_start_time") else None
        if start:
            duration = time.time() - start
            logger.debug(f"SQL %0.6fs %s", duration, statement)