# app/services/user_service.py
from typing import Optional, List, Dict, Any
from sqlmodel import Session, select
from app.services.base_service import BaseService
from app.models.user_model import UserModel
from app.crud.user_crud import UserCRUD
from app.core.logger import get_logger
from app.core.config import settings


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
    
    def get_all_users(self, session: Session) -> List[UserModel]:
        """Get all users from database"""
        try:
            statement = select(UserModel)
            users = session.exec(statement).all()
            logger.info(f"Retrieved {len(users)} users from database")
            return users
        except Exception as e:
            logger.error(f"Error retrieving all users: {str(e)}")
            return []
    
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
    
    def find_suspicious_users(self, session: Session, limit: Optional[int] = None) -> List[UserModel]:
        """
        Find all suspicious users based on actual data analysis, not database flag.
        This method analyzes user behavior patterns to identify suspicious activities.
        """
        try:
            # Get all users for analysis
            statement = select(UserModel)
            all_users = session.exec(statement).all()
            
            suspicious_users = []
            
            # Import IPDR service for analysis
            from app.services.ipdr_service import IpdrService
            ipdr_service = IpdrService()
            
            for user in all_users:
                is_suspicious = False
                suspicious_reasons = []
                
                # Get user's IPDR logs for analysis
                user_logs = ipdr_service.find_logs_by_user(session, user.AadhaarNo)
                
                if not user_logs:
                    continue  # Skip users with no activity
                
                # Analysis 1: High data usage detection
                total_data = sum(log.BytesDownload + log.BytesUpload for log in user_logs)
                if total_data > settings.ANALYSIS_THRESHOLDS["high_data_usage_mb"] * 1024 * 1024:
                    is_suspicious = True
                    suspicious_reasons.append("HIGH_DATA_USAGE")
                
                # Analysis 2: Excessive session count
                if len(user_logs) > settings.ANALYSIS_THRESHOLDS["excessive_sessions"]:
                    is_suspicious = True
                    suspicious_reasons.append("EXCESSIVE_SESSIONS")
                
                # Analysis 3: Late night activity (assuming timestamps)
                late_night_count = 0
                for log in user_logs:
                    # Check if activity is between 11 PM - 5 AM (rough estimation)
                    hour = log.StartTime.hour if hasattr(log.StartTime, 'hour') else 0
                    if hour >= settings.ANALYSIS_THRESHOLDS["late_night_start_hour"] or hour <= settings.ANALYSIS_THRESHOLDS["late_night_end_hour"]:
                        late_night_count += 1
                
                if late_night_count > len(user_logs) * settings.ANALYSIS_THRESHOLDS["late_night_activity_ratio"]:
                    is_suspicious = True
                    suspicious_reasons.append("LATE_NIGHT_ACTIVITY")
                
                # Analysis 4: Multiple unique destinations (possible scanning)
                unique_destinations = len(set(log.DestinationIP for log in user_logs))
                if unique_destinations > settings.ANALYSIS_THRESHOLDS["multiple_destinations"]:
                    is_suspicious = True
                    suspicious_reasons.append("MULTIPLE_DESTINATIONS")
                
                # Analysis 5: Unusual service usage patterns
                services_used = set(log.Service for log in user_logs)
                if len(services_used) > settings.ANALYSIS_THRESHOLDS["unusual_services_count"]:
                    is_suspicious = True
                    suspicious_reasons.append("UNUSUAL_SERVICES")
                
                # Analysis 6: Short duration but high data sessions (possible data exfiltration)
                for log in user_logs:
                    duration_minutes = (log.EndTime - log.StartTime).total_seconds() / 60
                    data_mb = (log.BytesDownload + log.BytesUpload) / (1024 * 1024)
                    
                    if duration_minutes < settings.ANALYSIS_THRESHOLDS["short_duration_minutes"] and data_mb > settings.ANALYSIS_THRESHOLDS["high_data_session_mb"]:
                        is_suspicious = True
                        if "DATA_EXFILTRATION" not in suspicious_reasons:
                            suspicious_reasons.append("DATA_EXFILTRATION")
                        break
                
                # If user is found suspicious, mark them and add to list
                if is_suspicious:
                    # Update user's suspicious status in database
                    user.IsSuspicious = True
                    user.SuspiciousType = suspicious_reasons
                    session.add(user)
                    suspicious_users.append(user)

                if limit and len(suspicious_users) >= limit:
                    break
            
            session.commit()
            logger.info(f"Found {len(suspicious_users)} suspicious users.")
            return suspicious_users
            
        except Exception as e:
            logger.error(f"Error finding suspicious users: {str(e)}")
            return []

    def count_users(self, session: Session) -> int:
        """Count total number of users"""
        try:
            statement = select(UserModel)
            users_count = session.exec(statement).count()
            logger.info(f"Total users count: {users_count}")
            return users_count
        except Exception as e:
            logger.error(f"Error counting users: {str(e)}")
            return 0
    
    def update_record(self, session: Session, aadhaar_no: str, data: Dict[str, Any]) -> Optional[UserModel]:
        """Update user record"""
        try:
            user = self.get_record(session, aadhaar_no)
            if user:
                for key, value in data.items():
                    setattr(user, key, value)
                session.add(user)
                session.commit()
                logger.info(f"User record updated: {aadhaar_no}")
                return user
            return None
        except Exception as e:
            logger.error(f"Error updating user record: {str(e)}")
            return None
    
    def delete_record(self, session: Session, aadhaar_no: str) -> bool:
        """Delete user record"""
        try:
            user = self.get_record(session, aadhaar_no)
            if user:
                session.delete(user)
                session.commit()
                logger.info(f"User record deleted: {aadhaar_no}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting user record: {str(e)}")
            return False
    
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
