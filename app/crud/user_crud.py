# app/crud/user_crud.py
from typing import Optional, List
from sqlmodel import Session, select
from app.models.user_model import UserModel
from app.crud.base import BaseCRUD
from sqlalchemy.orm.attributes import flag_modified

class UserCRUD(BaseCRUD[UserModel]):
    """
    CRUD operations for UserModel.
    Overrides methods from BaseCRUD to handle 'AadhaarNo' as the primary key.
    """
    
    def __init__(self):
        super().__init__(UserModel)
    
    def read(self, session: Session, aadhaar_no: str) -> Optional[UserModel]:
        """Override base read method to use AadhaarNo as primary key."""
        return session.get(UserModel, aadhaar_no)
    
    def delete(self, session: Session, aadhaar_no: str) -> Optional[UserModel]:
        """Override base delete method for AadhaarNo primary key."""
        obj = self.read(session, aadhaar_no)
        if obj:
            session.delete(obj)
            session.commit()
        return obj
        
    def get_user_by_phone(self, session: Session, phone_no: str) -> Optional[UserModel]:
        """Find user by their unique phone number."""
        statement = select(UserModel).where(UserModel.PhoneNo == phone_no)
        return session.exec(statement).first()
    
    def get_users_by_city(self, session: Session, city: str) -> List[UserModel]:
        """Get all users from a specific city (case-insensitive)."""
        statement = select(UserModel).where(UserModel.City.ilike(f"%{city}%"))
        return session.exec(statement).all()
        
    def get_users_by_state(self, session: Session, state: str) -> List[UserModel]:
        """Get all users from a specific state (case-insensitive)."""
        statement = select(UserModel).where(UserModel.State.ilike(f"%{state}%"))
        return session.exec(statement).all()
        
    def get_suspicious_users(self, session: Session) -> List[UserModel]:
        """Get all users flagged as suspicious."""
        statement = select(UserModel).where(UserModel.IsSuspicious == True)
        return session.exec(statement).all()
        
    def get_users_by_isp(self, session: Session, isp: str) -> List[UserModel]:
        """Get all users by Internet Service Provider (case-insensitive)."""
        statement = select(UserModel).where(UserModel.ISP.ilike(f"%{isp}%"))
        return session.exec(statement).all()
    
    def get_users_by_age_range(self, session: Session, min_age: int, max_age: int) -> List[UserModel]:
        """Get users within a specified age range (inclusive)."""
        statement = select(UserModel).where(UserModel.Age >= min_age, UserModel.Age <= max_age)
        return session.exec(statement).all()
        
    def search_users_by_name(self, session: Session, name_pattern: str) -> List[UserModel]:
        """Search users by name pattern (case-insensitive partial match)."""
        statement = select(UserModel).where(UserModel.Name.ilike(f"%{name_pattern}%"))
        return session.exec(statement).all()
    
    def get_users_with_multiple_devices(self, session: Session, min_devices: int = 2) -> List[UserModel]:
        """
        Get users with multiple devices registered.
        
        NOTE: This method filters in Python, which can be inefficient.
        For databases like PostgreSQL, a query using `jsonb_array_length` would be much faster.
        For SQLite, this is a reasonable approach for smaller datasets.
        """
        statement = select(UserModel)
        users = session.exec(statement).all()
        return [user for user in users if user.Devices and len(user.Devices) >= min_devices]
    
    def update_user_suspicion_status(
        self, 
        session: Session, 
        aadhaar_no: str, 
        is_suspicious: bool,
        suspicious_types: List[str] = None
    ) -> Optional[UserModel]:
        """Update a user's suspicious activity status and flags."""
        user = self.read(session, aadhaar_no)
        if user:
            user.IsSuspicious = is_suspicious
            if suspicious_types is not None:
                user.SuspiciousType = suspicious_types
                # Mark the JSON field as modified for SQLAlchemy to detect changes
                flag_modified(user, "SuspiciousType")
            session.add(user)
            session.commit()
            session.refresh(user)
        return user