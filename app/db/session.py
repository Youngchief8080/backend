# app/db/session.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base  # Import Base from declarative
from dotenv import load_dotenv
import os
import logging
from sqlalchemy.pool import QueuePool

# Load environment variables
load_dotenv()

# Fetch the database URL from the environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Check if DATABASE_URL exists
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL is not set. Please check your .env file.")

# Set up logging for better error handling
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Log the database URL for debugging (mask for security)
logger.debug(f"Using DATABASE_URL: {DATABASE_URL[:50]}...")

# Create the database engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,  # Adjust based on your requirements
    max_overflow=20,  # Allows overflow connections
    pool_timeout=30  # Timeout for connections
)

# SessionLocal factory for SQLAlchemy
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the Base class for ORM models
Base = declarative_base()

# Dependency function to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        raise
    finally:
        db.close()
