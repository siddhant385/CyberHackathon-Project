# app/services/base_service.py
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List, Dict, Any
from sqlmodel import Session
from app.core.database import engine

ModelType = TypeVar("ModelType")

class BaseService(Generic[ModelType], ABC):
    """
    Abstract base class for business services.
    Provides common functionality and enforces service patterns.
    """
    
    def __init__(self, crud_instance):
        """Initialize with CRUD instance"""
        self.crud = crud_instance
    
    def get_session(self) -> Session:
        """Get database session"""
        return Session(engine)
    
    @abstractmethod
    def create_record(self, session: Session, data: Dict[str, Any]) -> ModelType:
        """Create a new record with business logic validation"""
        pass
    
    @abstractmethod
    def get_record(self, session: Session, identifier: Any) -> Optional[ModelType]:
        """Get a record by identifier"""
        pass
    
    def get_multiple_records(self, session: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get multiple records with pagination"""
        return self.crud.read_multi(session, skip=skip, limit=limit)
    
    def update_record(self, session: Session, identifier: Any, update_data: Dict[str, Any]) -> Optional[ModelType]:
        """Update a record with business logic validation"""
        existing_record = self.get_record(session, identifier)
        if existing_record:
            return self.crud.update(session, existing_record, update_data)
        return None
    
    def delete_record(self, session: Session, identifier: Any) -> bool:
        """Delete a record"""
        existing_record = self.get_record(session, identifier)
        if existing_record:
            self.crud.delete(session, identifier)
            return True
        return False
    
    def count_records(self, session: Session) -> int:
        """Count total records"""
        return self.crud.count(session)
