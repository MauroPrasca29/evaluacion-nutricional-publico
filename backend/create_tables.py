"""Create database tables for testing (uses the same DB URL env var)."""
from src.db.base import Base
from src.db.session import engine
import importlib

# Import the models so they are registered with Base.metadata
importlib.import_module("src.db.models")

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Done.")
