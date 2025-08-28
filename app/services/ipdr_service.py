# app/services/ipdr_service.py
from typing import Optional, List, Dict, Any, Tuple
from sqlmodel import Session, select, and_, or_
from datetime import datetime, timedelta
from app.services.base_service import BaseService
from app.models.ipdr_log_model import IPDRLogModel
from app.crud.ipdr_crud import IPDRLogCRUD
from app.core.logger import get_logger

logger = get_logger(__name__)

class IPDRService(BaseService[IPDRLogModel]):
    """
    Business service for IPDR Log operations.
    Handles complex queries, analytics, and investigation features.
    """
    
    def __init__(self):
        super().__init__(IPDRLogCRUD())
    
    def create_record(self, session: Session, data: Dict[str, Any]) -> IPDRLogModel:
        """Create a new IPDR log with business validation"""
        try:
            # Validate IP addresses
            IPDRLogModel.validate_ip(data.get('SourceIP', ''))
            IPDRLogModel.validate_ip(data.get('DestinationIP', ''))
            
            ipdr_log = IPDRLogModel(**data)
            created_log = self.crud.create(session, ipdr_log)
            logger.info(f"IPDR log created successfully: ID {created_log.id}")
            return created_log
            
        except Exception as e:
            logger.error(f"Error creating IPDR log: {str(e)}")
            raise
    
    def get_record(self, session: Session, log_id: int) -> Optional[IPDRLogModel]:
        """Get IPDR log by ID"""
        return self.crud.read(session, log_id)
    
    def find_logs_by_user(self, session: Session, aadhaar_no: str) -> List[IPDRLogModel]:
        """Find all logs for a specific user"""
        try:
            statement = select(IPDRLogModel).where(IPDRLogModel.AadhaarNo == aadhaar_no)
            logs = session.exec(statement).all()
            logger.info(f"Found {len(logs)} logs for user: {aadhaar_no}")
            return logs
        except Exception as e:
            logger.error(f"Error finding logs by user: {str(e)}")
            return []
    
    def find_communication_partners(self, session: Session, aadhaar_no: str) -> List[Dict[str, Any]]:
        """
        Find all B-party (recipients) that this user communicated with.
        Core functionality for investigation.
        """
        try:
            statement = select(IPDRLogModel).where(IPDRLogModel.AadhaarNo == aadhaar_no)
            logs = session.exec(statement).all()
            
            partners = {}
            for log in logs:
                dest_ip = log.DestinationIP
                if dest_ip not in partners:
                    partners[dest_ip] = {
                        'destination_ip': dest_ip,
                        'destination_port': log.DestinationPort,
                        'total_sessions': 0,
                        'total_upload': 0,
                        'total_download': 0,
                        'services_used': set(),
                        'first_contact': log.StartTime,
                        'last_contact': log.EndTime,
                        'protocols': set()
                    }
                
                partner = partners[dest_ip]
                partner['total_sessions'] += 1
                partner['total_upload'] += log.BytesUpload
                partner['total_download'] += log.BytesDownload
                partner['services_used'].add(log.Service)
                partner['protocols'].add(log.Protocol)
                
                if log.StartTime < partner['first_contact']:
                    partner['first_contact'] = log.StartTime
                if log.EndTime > partner['last_contact']:
                    partner['last_contact'] = log.EndTime
            
            # Convert sets to lists for JSON serialization
            result = []
            for partner_data in partners.values():
                partner_data['services_used'] = list(partner_data['services_used'])
                partner_data['protocols'] = list(partner_data['protocols'])
                result.append(partner_data)
            
            logger.info(f"Found {len(result)} communication partners for user: {aadhaar_no}")
            return result
            
        except Exception as e:
            logger.error(f"Error finding communication partners: {str(e)}")
            return []
    
    def find_logs_by_ip_range(self, session: Session, start_ip: str, end_ip: str) -> List[IPDRLogModel]:
        """Find logs within IP range"""
        try:
            # Simple string comparison for IP range (can be improved with proper IP parsing)
            statement = select(IPDRLogModel).where(
                and_(
                    IPDRLogModel.SourceIP >= start_ip,
                    IPDRLogModel.SourceIP <= end_ip
                )
            )
            logs = session.exec(statement).all()
            logger.info(f"Found {len(logs)} logs in IP range: {start_ip} - {end_ip}")
            return logs
        except Exception as e:
            logger.error(f"Error finding logs by IP range: {str(e)}")
            return []
    
    def find_logs_by_time_range(self, session: Session, start_time: datetime, end_time: datetime) -> List[IPDRLogModel]:
        """Find logs within time range"""
        try:
            statement = select(IPDRLogModel).where(
                and_(
                    IPDRLogModel.StartTime >= start_time,
                    IPDRLogModel.EndTime <= end_time
                )
            )
            logs = session.exec(statement).all()
            logger.info(f"Found {len(logs)} logs in time range: {start_time} - {end_time}")
            return logs
        except Exception as e:
            logger.error(f"Error finding logs by time range: {str(e)}")
            return []
    
    def find_suspicious_logs(self, session: Session) -> List[IPDRLogModel]:
        """Find all logs marked as suspicious"""
        try:
            statement = select(IPDRLogModel).where(IPDRLogModel.IsSuspicious == True)
            logs = session.exec(statement).all()
            logger.info(f"Found {len(logs)} suspicious logs")
            return logs
        except Exception as e:
            logger.error(f"Error finding suspicious logs: {str(e)}")
            return []
    
    def analyze_high_traffic_sessions(self, session: Session, threshold_mb: int = 100) -> List[IPDRLogModel]:
        """Find sessions with high data usage"""
        try:
            threshold_bytes = threshold_mb * 1024 * 1024  # Convert MB to bytes
            statement = select(IPDRLogModel).where(
                (IPDRLogModel.BytesUpload + IPDRLogModel.BytesDownload) > threshold_bytes
            )
            logs = session.exec(statement).all()
            logger.info(f"Found {len(logs)} high traffic sessions (>{threshold_mb}MB)")
            return logs
        except Exception as e:
            logger.error(f"Error analyzing high traffic sessions: {str(e)}")
            return []
    
    def get_user_activity_summary(self, session: Session, aadhaar_no: str) -> Dict[str, Any]:
        """Get comprehensive activity summary for a user"""
        try:
            logs = self.find_logs_by_user(session, aadhaar_no)
            
            if not logs:
                return {'error': 'No logs found for user'}
            
            total_upload = sum(log.BytesUpload for log in logs)
            total_download = sum(log.BytesDownload for log in logs)
            total_duration = sum(log.Duration for log in logs)
            
            services = set(log.Service for log in logs)
            protocols = set(log.Protocol for log in logs)
            unique_destinations = set(log.DestinationIP for log in logs)
            
            first_activity = min(log.StartTime for log in logs)
            last_activity = max(log.EndTime for log in logs)
            
            summary = {
                'user_id': aadhaar_no,
                'total_sessions': len(logs),
                'total_upload_mb': round(total_upload / (1024 * 1024), 2),
                'total_download_mb': round(total_download / (1024 * 1024), 2),
                'total_duration_hours': round(total_duration / 3600, 2),
                'unique_services': list(services),
                'protocols_used': list(protocols),
                'unique_destinations': len(unique_destinations),
                'first_activity': first_activity,
                'last_activity': last_activity,
                'suspicious_sessions': len([log for log in logs if log.IsSuspicious])
            }
            
            logger.info(f"Generated activity summary for user: {aadhaar_no}")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating user activity summary: {str(e)}")
            return {'error': str(e)}
