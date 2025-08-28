# app/crud/base.py
from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from sqlmodel import SQLModel, Session, select, func
from abc import ABC

ModelType = TypeVar("ModelType", bound=SQLModel)

class BaseCRUD(Generic[ModelType], ABC):
    """
    Abstract base class for generic CRUD operations.
    Provides standard Create, Read, Update, Delete methods.
    """
    
    def __init__(self, model: Type[ModelType]):
        """Initialize with the SQLModel class"""
        self.model = model
    
    def create(self, session: Session, obj_in: ModelType) -> ModelType:
        """Create a new record in the database."""
        session.add(obj_in)
        session.commit()
        session.refresh(obj_in)
        return obj_in
    
    def read(self, session: Session, id: Any) -> Optional[ModelType]:
        """
        Read a single record by its primary key (assumes 'id' field).
        NOTE: This method must be overridden if the primary key is not named 'id'.
        """
        # This will fail for models without an 'id' primary key.
        # UserCRUD correctly overrides this.
        return session.get(self.model, id)
    
    def read_multi(self, session: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Read multiple records with pagination."""
        statement = select(self.model).offset(skip).limit(limit)
        return session.exec(statement).all()
    
    def update(self, session: Session, db_obj: ModelType, obj_in: Dict[str, Any]) -> ModelType:
        """Update an existing record."""
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj
    
    def delete(self, session: Session, id: Any) -> Optional[ModelType]:
        """
        Delete a record by its primary key (assumes 'id' field).
        NOTE: This method must be overridden if the primary key is not named 'id'.
        """
        obj = self.read(session, id)
        if obj:
            session.delete(obj)
            session.commit()
        return obj
    
    def count(self, session: Session) -> int:
        """
        Count total records in the table.
        NOTE: Works for simple primary keys. May need override for complex cases.
        """
        # Using a generic count approach
        statement = select(func.count()).select_from(self.model)
        return session.exec(statement).one()