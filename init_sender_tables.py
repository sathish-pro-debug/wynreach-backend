# init_sender_db.py - Place in E:\wynReach\ (root folder)
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from backend.database import main_engine, Base
from backend.models import sender_identity  # This imports the models

def create_tables():
    print("Creating sender identity tables...")
    Base.metadata.create_all(bind=main_engine)
    print("✅ Tables created successfully!")

if __name__ == "__main__":
    create_tables()