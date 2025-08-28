# app/services/ipdr_service.py
from typing import Optional, List, Dict, Any, Tuple
from sqlmodel import Session, select, and_, or_
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

from app.services.base_service import BaseService
from app.models.ipdr_log_model import IPDRLogModel
from app.crud.ipdr_crud import IPDRLogCRUD
from app.core.logger import get_logger

logger = get_logger(__name__)

class IpdrService(BaseService[IPDRLogModel]):
    """Service class for IPDR log operations and analysis."""
    
    def __init__(self):
        super().__init__(IPDRLogCRUD())
    
    def get_record(self, session: Session, record_id: str) -> Optional[IPDRLogModel]:
        """Get a single IPDR log by its RecordID."""
        try:
            record = self.crud.read(session, record_id)
            if record:
                logger.info(f"Retrieved IPDR log with RecordID: {record_id}")
            else:
                logger.warning(f"No IPDR log found with RecordID: {record_id}")
            return record
        except Exception as e:
            logger.error(f"Error retrieving IPDR log {record_id}: {str(e)}")
            return None

    def create_record(self, session: Session, data: Dict[str, Any]) -> IPDRLogModel:
        """Create a new IPDR log."""
        try:
            ipdr_log = IPDRLogModel(**data)
            created_log = self.crud.create(session, ipdr_log)
            logger.info(f"Successfully created IPDR log with RecordID: {created_log.RecordID}")
            return created_log
        except Exception as e:
            logger.error(f"Error creating IPDR log: {str(e)}")
            raise

    def find_suspicious_logs(self, session: Session) -> List[IPDRLogModel]:
        """Find suspicious IPDR logs based on actual data analysis patterns."""
        try:
            all_logs = session.exec(select(IPDRLogModel)).all()
            
            if not all_logs:
                logger.warning("No IPDR logs found for analysis")
                return []
            
            suspicious_logs = []
            user_logs = defaultdict(list)
            
            for log in all_logs:
                user_logs[log.AadhaarNo].append(log)
            
            for user_aadhaar, logs in user_logs.items():
                if self._analyze_user_logs_for_suspicious_activity(logs):
                    suspicious_logs.extend(logs)
            
            logger.info(f"Found {len(suspicious_logs)} suspicious logs from {len(all_logs)} total logs")
            return suspicious_logs
            
        except Exception as e:
            logger.error(f"Error finding suspicious logs: {str(e)}")
            return []
    
    def _analyze_user_logs_for_suspicious_activity(self, logs: List[IPDRLogModel]) -> bool:
        """Analyze a user's logs to determine if they show suspicious patterns."""
        if not logs:
            return False
        
        try:
            total_data_up = sum(log.BytesUpload or 0 for log in logs)
            total_data_down = sum(log.BytesDownload or 0 for log in logs)
            total_data = total_data_up + total_data_down
            
            # High data usage (>500MB total)
            if total_data > 500 * 1024 * 1024:
                return True
            
            # Unusual upload/download ratio
            if total_data_down > 0 and (total_data_up / total_data_down) > 2.0:
                return True
            
            # High session frequency (>50 sessions)
            if len(logs) > 50:
                return True
            
            # Multiple unique destinations (>20 different IPs)
            unique_destinations = set()
            for log in logs:
                if hasattr(log, 'DestinationIP') and log.DestinationIP:
                    unique_destinations.add(log.DestinationIP)
            
            if len(unique_destinations) > 20:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error analyzing user logs for suspicious activity: {str(e)}")
            return False
    
    def get_logs_by_user(self, session: Session, aadhaar_no: str) -> List[IPDRLogModel]:
        """Get all IPDR logs for a specific user using AadhaarNo."""
        try:
            logs = session.exec(
                select(IPDRLogModel).where(IPDRLogModel.AadhaarNo == aadhaar_no)
            ).all()
            logger.info(f"Found {len(logs)} logs for user {aadhaar_no}")
            return logs
        except Exception as e:
            logger.error(f"Error getting logs for user {aadhaar_no}: {str(e)}")
            return []
    
    def find_logs_by_user(self, session: Session, aadhaar_no: str) -> List[IPDRLogModel]:
        """Alias for get_logs_by_user for backward compatibility."""
        return self.get_logs_by_user(session, aadhaar_no)
    
    def get_all_ipdr_logs(self, session: Session, limit: int = 1000) -> List[IPDRLogModel]:
        """Get all IPDR logs with optional limit."""
        try:
            logs = session.exec(select(IPDRLogModel).limit(limit)).all()
            logger.info(f"Retrieved {len(logs)} IPDR logs")
            return logs
        except Exception as e:
            logger.error(f"Error getting all logs: {str(e)}")
            return []
    
    def get_user_activity_summary(self, session: Session, aadhaar_no: str) -> Dict[str, Any]:
        """Get comprehensive activity summary for a user."""
        try:
            logs = self.get_logs_by_user(session, aadhaar_no)
            
            if not logs:
                return {
                    'total_sessions': 0,
                    'total_upload_mb': 0.0,
                    'total_download_mb': 0.0,
                    'total_duration_hours': 0.0,
                    'unique_services': [],
                    'protocols_used': [],
                    'unique_destinations': 0
                }
            
            total_upload = sum(log.BytesUpload or 0 for log in logs)
            total_download = sum(log.BytesDownload or 0 for log in logs)
            total_duration = sum(log.Duration or 0 for log in logs)
            
            unique_services = list(set(log.Service for log in logs if log.Service))
            protocols_used = list(set(log.Protocol for log in logs if log.Protocol))
            unique_destinations = len(set(log.DestinationIP for log in logs if log.DestinationIP))
            
            summary = {
                'total_sessions': len(logs),
                'total_upload_mb': round(total_upload / (1024 * 1024), 2),
                'total_download_mb': round(total_download / (1024 * 1024), 2),
                'total_duration_hours': round(total_duration / 3600, 2),
                'unique_services': unique_services,
                'protocols_used': protocols_used,
                'unique_destinations': unique_destinations
            }
            
            logger.info(f"Generated activity summary for {aadhaar_no}")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating activity summary for {aadhaar_no}: {str(e)}")
            return {}
    
    def find_communication_partners(self, session: Session, aadhaar_no: str) -> List[Dict[str, Any]]:
        """Find all communication partners for a user."""
        try:
            logs = self.get_logs_by_user(session, aadhaar_no)
            
            if not logs:
                return []
            
            # Group by destination IP
            partners = defaultdict(lambda: {
                'total_sessions': 0,
                'total_upload': 0,
                'total_download': 0,
                'services': set(),
                'protocols': set()
            })
            
            for log in logs:
                dest_ip = log.DestinationIP
                if dest_ip:
                    partners[dest_ip]['total_sessions'] += 1
                    partners[dest_ip]['total_upload'] += log.BytesUpload or 0
                    partners[dest_ip]['total_download'] += log.BytesDownload or 0
                    if log.Service:
                        partners[dest_ip]['services'].add(log.Service)
                    if log.Protocol:
                        partners[dest_ip]['protocols'].add(log.Protocol)
            
            # Convert to list and sort by session count
            result = []
            for dest_ip, data in partners.items():
                result.append({
                    'destination_ip': dest_ip,
                    'total_sessions': data['total_sessions'],
                    'total_upload_mb': round(data['total_upload'] / (1024 * 1024), 2),
                    'total_download_mb': round(data['total_download'] / (1024 * 1024), 2),
                    'services': list(data['services']),
                    'protocols': list(data['protocols'])
                })
            
            # Sort by session count
            result.sort(key=lambda x: x['total_sessions'], reverse=True)
            
            logger.info(f"Found {len(result)} communication partners for {aadhaar_no}")
            return result
            
        except Exception as e:
            logger.error(f"Error finding communication partners for {aadhaar_no}: {str(e)}")
            return []
    
    def get_communication_stats(self, session: Session, aadhaar_no: str) -> Dict[str, Any]:
        """Get comprehensive communication statistics for a user."""
        try:
            logs = self.get_logs_by_user(session, aadhaar_no)
            
            if not logs:
                return {}
            
            total_sessions = len(logs)
            total_data_up = sum(log.BytesUpload or 0 for log in logs)
            total_data_down = sum(log.BytesDownload or 0 for log in logs)
            total_data = total_data_up + total_data_down
            
            # Get unique destinations
            unique_destinations = set()
            for log in logs:
                if log.DestinationIP:
                    unique_destinations.add(log.DestinationIP)
            
            # Get service types
            service_types = set()
            for log in logs:
                if log.Service:
                    service_types.add(log.Service)
            
            stats = {
                'total_sessions': total_sessions,
                'total_data_bytes': total_data,
                'total_data_mb': round(total_data / (1024 * 1024), 2),
                'data_upload_bytes': total_data_up,
                'data_download_bytes': total_data_down,
                'unique_destinations': len(unique_destinations),
                'service_types': list(service_types),
                'unique_services_count': len(service_types),
                'upload_download_ratio': round(total_data_up / total_data_down, 2) if total_data_down > 0 else 0
            }
            
            logger.info(f"Generated communication stats for {aadhaar_no}")
            return stats
            
        except Exception as e:
            logger.error(f"Error generating communication stats: {str(e)}")
            return {}
    
    def create_log(self, session: Session, log_data: Dict[str, Any]) -> Optional[IPDRLogModel]:
        """Create a new IPDR log entry."""
        try:
            log = IPDRLogModel(**log_data)
            result = self.ipdr_crud.create(session, log)
            logger.info(f"Created IPDR log for {log.AadhaarNo}")
            return result
        except Exception as e:
            logger.error(f"Error creating IPDR log: {str(e)}")
            return None
    
    def get_logs_count(self, session: Session) -> int:
        """Get total count of IPDR logs."""
        try:
            count = session.exec(select(IPDRLogModel)).all()
            return len(count)
        except Exception as e:
            logger.error(f"Error getting logs count: {str(e)}")
            return 0
    
    def analyze_communication_patterns(self, session: Session, aadhaar_no: str) -> Dict[str, Any]:
        """Analyze communication patterns for a specific user."""
        try:
            logs = self.get_logs_by_user(session, aadhaar_no)
            
            if not logs:
                return {"error": "No logs found for user"}
            
            # Time-based analysis
            time_patterns = defaultdict(int)
            destination_frequency = defaultdict(int)
            service_usage = defaultdict(int)
            
            for log in logs:
                # Analyze destinations
                if log.DestinationIP:
                    destination_frequency[log.DestinationIP] += 1
                
                # Analyze services
                if log.Service:
                    service_usage[log.Service] += 1
            
            # Sort by frequency
            top_destinations = sorted(destination_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
            top_services = sorted(service_usage.items(), key=lambda x: x[1], reverse=True)
            
            analysis = {
                'total_logs': len(logs),
                'analysis_period': 'Available data range',
                'top_destinations': top_destinations,
                'service_distribution': top_services,
                'communication_summary': {
                    'unique_destinations': len(destination_frequency),
                    'unique_services': len(service_usage),
                    'most_contacted': top_destinations[0] if top_destinations else None,
                    'primary_service': top_services[0] if top_services else None
                }
            }
            
            logger.info(f"Completed communication pattern analysis for {aadhaar_no}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing communication patterns: {str(e)}")
            return {"error": str(e)}