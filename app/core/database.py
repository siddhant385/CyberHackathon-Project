# app/database.py
from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings

# Create the database engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=True,  # Set to False in production
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

def get_session():
    """Dependency to get a database session."""
    with Session(engine) as session:
        yield session

def init_db():
    """Initialize the database and create tables."""
    print("Initializing database and creating tables...")
    # Import all models here so they are registered with SQLModel
    from app.models.user_model import UserModel
    from app.models.ipdr_log_model import IPDRLogModel
    
    SQLModel.metadata.create_all(engine)
    print("Database initialized successfully.")