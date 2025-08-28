# app/core/database.py
from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

# Create the database engine with improved configuration
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,  # Set to True only for debugging SQL queries
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {},
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600    # Recycle connections every hour
)

def get_session():
    """
    Dependency to get a database session.
    Use this for dependency injection in APIs.
    """
    with Session(engine) as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()

def init_db():
    """
    Initialize the database and create tables.
    This should be called once at application startup.
    """
    try:
        logger.info("Initializing database and creating tables...")
        
        # Import all models here so they are registered with SQLModel
        from app.models.user_model import UserModel
        from app.models.ipdr_log_model import IPDRLogModel
        
        # Create all tables
        SQLModel.metadata.create_all(engine)
        
        logger.info("Database initialized successfully.")
        logger.info(f"Database URL: {settings.DATABASE_URL}")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise

def check_db_connection():
    """
    Check if database connection is working.
    Useful for health checks.
    """
    try:
        from sqlmodel import text
        with Session(engine) as session:
            session.exec(text("SELECT 1"))
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False