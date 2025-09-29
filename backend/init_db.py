# init_db.py
from backend.db import init_db

# Create all tables using the shared engine and metadata
init_db()

print("✅ Database tables created successfully")
