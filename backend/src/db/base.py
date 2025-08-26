"""
Base database configuration and imports
"""
from sqlalchemy.ext.declarative import declarative_base

# Create base class for all models
Base = declarative_base()

# Import all models here to ensure they are registered with SQLAlchemy
# This is important for Alembic migrations to work properly

# When models are created, import them here:
# from models.user import User
# from models.child import Child
# from models.followup import FollowUp
# from models.community import Community
# from models.alert import Alert
# from models.image import Image
# from models.who_standard import WHOStandard
# from models.import_log import ImportLog

# Metadata will be used by Alembic for migrations
metadata = Base.metadata
