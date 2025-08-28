# app/services/user_service.py
from typing import Optional, List, Dict, Any
from sqlmodel import Session, select
from app.services.base_service import BaseService
from app.models.user_model import UserModel
from app.crud.user_crud import UserCRUD
from app.core.logger import get_logger

logger = get_logger(__name__)

class UserService(BaseService[UserModel]):
    """
    Business service for User operations.
    Handles business logic, validation, and complex queries.
    """
    
    def __init__(self):
        super().__init__(UserCRUD())
    
    def create_record(self, session: Session, data: Dict[str, Any]) -> UserModel:
        """Create a new user with business validation"""
        try:
            # Business logic validation
            if self.get_record(session, data.get('AadhaarNo')):
                raise ValueError(f"User with Aadhaar {data.get('AadhaarNo')} already exists")
            
            user = UserModel(**data)
            created_user = self.crud.create(session, user)
            logger.info(f"User created successfully: {created_user.AadhaarNo}")
            return created_user
            
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise
    
    def get_record(self, session: Session, aadhaar_no: str) -> Optional[UserModel]:
        """Get user by Aadhaar number"""
        return self.crud.read(session, aadhaar_no)
    
    def find_users_by_phone(self, session: Session, phone_no: str) -> List[UserModel]:
        """Find users by phone number"""
        try:
            statement = select(UserModel).where(UserModel.PhoneNo == phone_no)
            users = session.exec(statement).all()
            logger.info(f"Found {len(users)} users with phone: {phone_no}")
            return users
        except Exception as e:
            logger.error(f"Error finding users by phone: {str(e)}")
            return []
    
    def find_users_by_city(self, session: Session, city: str) -> List[UserModel]:
        """Find users by city"""
        try:
            statement = select(UserModel).where(UserModel.City == city)
            users = session.exec(statement).all()
            logger.info(f"Found {len(users)} users in city: {city}")
            return users
        except Exception as e:
            logger.error(f"Error finding users by city: {str(e)}")
            return []
    
    def find_suspicious_users(self, session: Session) -> List[UserModel]:
        """Find all suspicious users"""
        try:
            statement = select(UserModel).where(UserModel.IsSuspicious == True)
            users = session.exec(statement).all()
            logger.info(f"Found {len(users)} suspicious users")
            return users
        except Exception as e:
            logger.error(f"Error finding suspicious users: {str(e)}")
            return []
    
    def mark_user_suspicious(self, session: Session, aadhaar_no: str, suspicious_type: str) -> Optional[UserModel]:
        """Mark a user as suspicious with reason"""
        try:
            user = self.get_record(session, aadhaar_no)
            if user:
                current_types = user.SuspiciousType or []
                if suspicious_type not in current_types:
                    current_types.append(suspicious_type)
                
                update_data = {
                    'IsSuspicious': True,
                    'SuspiciousType': current_types
                }
                updated_user = self.update_record(session, aadhaar_no, update_data)
                logger.warning(f"User {aadhaar_no} marked suspicious: {suspicious_type}")
                return updated_user
            return None
        except Exception as e:
            logger.error(f"Error marking user suspicious: {str(e)}")
            return None
    
    def assign_ip_to_user(self, session: Session, aadhaar_no: str, ip_address: str) -> Optional[UserModel]:
        """Assign IP address to user"""
        try:
            user = self.get_record(session, aadhaar_no)
            if user:
                current_ips = user.AssignedIPs or []
                if ip_address not in current_ips:
                    current_ips.append(ip_address)
                    update_data = {'AssignedIPs': current_ips}
                    updated_user = self.update_record(session, aadhaar_no, update_data)
                    logger.info(f"IP {ip_address} assigned to user {aadhaar_no}")
                    return updated_user
            return None
        except Exception as e:
            logger.error(f"Error assigning IP to user: {str(e)}")
            return None
