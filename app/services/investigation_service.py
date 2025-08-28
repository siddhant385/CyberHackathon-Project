# app/services/investigation_service.py
from typing import List, Dict, Any, Optional, Tuple
from sqlmodel import Session, select, and_, or_, func
from datetime import datetime, timedelta
from app.services.user_service import UserService
from app.services.ipdr_service import IPDRService
from app.models.user_model import UserModel
from app.models.ipdr_log_model import IPDRLogModel
from app.core.logger import get_logger

logger = get_logger(__name__)

class InvestigationService:
    """
    High-level investigation service that combines user and IPDR data
    for comprehensive analysis and investigation features.
    """
    
    def __init__(self):
        self.user_service = UserService()
        self.ipdr_service = IPDRService()
    
    def investigate_user_relationships(self, session: Session, aadhaar_no: str) -> Dict[str, Any]:
        """
        Complete investigation of a user's digital relationships and patterns.
        Core functionality for investigators.
        """
        try:
            logger.info(f"Starting investigation for user: {aadhaar_no}")
            
            # Get user details
            user = self.user_service.get_record(session, aadhaar_no)
            if not user:
                return {'error': f'User {aadhaar_no} not found'}
            
            # Get communication partners (B-parties)
            partners = self.ipdr_service.find_communication_partners(session, aadhaar_no)
            
            # Get activity summary
            activity_summary = self.ipdr_service.get_user_activity_summary(session, aadhaar_no)
            
            # Analyze patterns
            patterns = self._analyze_communication_patterns(session, aadhaar_no)
            
            # Check for anomalies
            anomalies = self._detect_anomalies(session, aadhaar_no)
            
            investigation_report = {
                'user_details': {
                    'aadhaar_no': user.AadhaarNo,
                    'name': user.Name,
                    'phone': user.PhoneNo,
                    'city': user.City,
                    'is_suspicious': user.IsSuspicious,
                    'suspicious_types': user.SuspiciousType
                },
                'communication_partners': partners,
                'activity_summary': activity_summary,
                'patterns': patterns,
                'anomalies': anomalies,
                'investigation_timestamp': datetime.now()
            }
            
            logger.info(f"Investigation completed for user: {aadhaar_no}")
            return investigation_report
            
        except Exception as e:
            logger.error(f"Error in user investigation: {str(e)}")
            return {'error': str(e)}
    
    def find_connected_users(self, session: Session, aadhaar_no: str) -> List[Dict[str, Any]]:
        """
        Find users who communicated with same IP addresses (common contacts).
        Useful for network analysis.
        """
        try:
            # Get all destination IPs this user communicated with
            user_logs = self.ipdr_service.find_logs_by_user(session, aadhaar_no)
            destination_ips = set(log.DestinationIP for log in user_logs)
            
            if not destination_ips:
                return []
            
            # Find other users who communicated with same IPs
            connected_users = []
            
            for dest_ip in destination_ips:
                statement = select(IPDRLogModel).where(
                    and_(
                        IPDRLogModel.DestinationIP == dest_ip,
                        IPDRLogModel.AadhaarNo != aadhaar_no
                    )
                )
                related_logs = session.exec(statement).all()
                
                related_users = set(log.AadhaarNo for log in related_logs)
                
                for related_user in related_users:
                    user_details = self.user_service.get_record(session, related_user)
                    if user_details:
                        connected_users.append({
                            'aadhaar_no': related_user,
                            'name': user_details.Name,
                            'phone': user_details.PhoneNo,
                            'common_destination': dest_ip,
                            'connection_count': len([log for log in related_logs if log.AadhaarNo == related_user])
                        })
            
            logger.info(f"Found {len(connected_users)} connected users for: {aadhaar_no}")
            return connected_users
            
        except Exception as e:
            logger.error(f"Error finding connected users: {str(e)}")
            return []
    
    def analyze_network_cluster(self, session: Session, center_aadhaar: str, depth: int = 2) -> Dict[str, Any]:
        """
        Analyze network cluster around a central user.
        Shows connections up to specified depth.
        """
        try:
            visited = set()
            network = {'nodes': [], 'edges': []}
            
            def add_user_connections(aadhaar_no: str, current_depth: int):
                if current_depth > depth or aadhaar_no in visited:
                    return
                
                visited.add(aadhaar_no)
                
                # Add user node
                user = self.user_service.get_record(session, aadhaar_no)
                if user:
                    network['nodes'].append({
                        'id': aadhaar_no,
                        'name': user.Name,
                        'phone': user.PhoneNo,
                        'is_suspicious': user.IsSuspicious,
                        'depth': current_depth
                    })
                
                # Find connected users
                connected = self.find_connected_users(session, aadhaar_no)
                
                for connection in connected:
                    connected_aadhaar = connection['aadhaar_no']
                    
                    # Add edge
                    network['edges'].append({
                        'from': aadhaar_no,
                        'to': connected_aadhaar,
                        'common_destination': connection['common_destination'],
                        'strength': connection['connection_count']
                    })
                    
                    # Recursively add connections
                    add_user_connections(connected_aadhaar, current_depth + 1)
            
            add_user_connections(center_aadhaar, 0)
            
            logger.info(f"Network analysis completed for {center_aadhaar}: {len(network['nodes'])} nodes, {len(network['edges'])} edges")
            return network
            
        except Exception as e:
            logger.error(f"Error in network cluster analysis: {str(e)}")
            return {'nodes': [], 'edges': [], 'error': str(e)}
    
    def _analyze_communication_patterns(self, session: Session, aadhaar_no: str) -> Dict[str, Any]:
        """Analyze communication patterns for a user"""
        try:
            logs = self.ipdr_service.find_logs_by_user(session, aadhaar_no)
            
            if not logs:
                return {}
            
            # Time-based patterns
            hourly_activity = {}
            daily_activity = {}
            
            for log in logs:
                hour = log.StartTime.hour
                day = log.StartTime.strftime('%A')
                
                hourly_activity[hour] = hourly_activity.get(hour, 0) + 1
                daily_activity[day] = daily_activity.get(day, 0) + 1
            
            # Most active hours and days
            most_active_hour = max(hourly_activity, key=hourly_activity.get) if hourly_activity else None
            most_active_day = max(daily_activity, key=daily_activity.get) if daily_activity else None
            
            # Service usage patterns
            service_usage = {}
            for log in logs:
                service_usage[log.Service] = service_usage.get(log.Service, 0) + 1
            
            return {
                'hourly_activity': hourly_activity,
                'daily_activity': daily_activity,
                'most_active_hour': most_active_hour,
                'most_active_day': most_active_day,
                'service_usage': service_usage,
                'total_unique_destinations': len(set(log.DestinationIP for log in logs))
            }
            
        except Exception as e:
            logger.error(f"Error analyzing communication patterns: {str(e)}")
            return {}
    
    def _detect_anomalies(self, session: Session, aadhaar_no: str) -> List[Dict[str, Any]]:
        """Detect anomalous behavior patterns"""
        try:
            anomalies = []
            logs = self.ipdr_service.find_logs_by_user(session, aadhaar_no)
            
            if not logs:
                return anomalies
            
            # High data usage sessions
            high_data_sessions = [
                log for log in logs 
                if (log.BytesUpload + log.BytesDownload) > 100 * 1024 * 1024  # 100MB
            ]
            
            if high_data_sessions:
                anomalies.append({
                    'type': 'high_data_usage',
                    'description': f'Found {len(high_data_sessions)} sessions with high data usage (>100MB)',
                    'count': len(high_data_sessions),
                    'severity': 'medium'
                })
            
            # Unusual time activity (late night sessions)
            late_night_sessions = [
                log for log in logs 
                if log.StartTime.hour >= 23 or log.StartTime.hour <= 5
            ]
            
            if len(late_night_sessions) > len(logs) * 0.3:  # More than 30% late night activity
                anomalies.append({
                    'type': 'unusual_timing',
                    'description': f'High late-night activity: {len(late_night_sessions)} sessions',
                    'count': len(late_night_sessions),
                    'severity': 'low'
                })
            
            # Multiple unique destinations
            unique_destinations = set(log.DestinationIP for log in logs)
            if len(unique_destinations) > 50:  # More than 50 unique destinations
                anomalies.append({
                    'type': 'high_connectivity',
                    'description': f'High number of unique destinations: {len(unique_destinations)}',
                    'count': len(unique_destinations),
                    'severity': 'medium'
                })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {str(e)}")
            return []
    
    def generate_investigation_report(self, session: Session, aadhaar_no: str) -> str:
        """Generate a comprehensive text report for investigators"""
        try:
            investigation = self.investigate_user_relationships(session, aadhaar_no)
            
            if 'error' in investigation:
                return f"Investigation Error: {investigation['error']}"
            
            report = []
            report.append("=" * 60)
            report.append("IPDR INVESTIGATION REPORT")
            report.append("=" * 60)
            report.append(f"Generated: {investigation['investigation_timestamp']}")
            report.append("")
            
            # User Details
            user = investigation['user_details']
            report.append("USER DETAILS:")
            report.append(f"  Aadhaar: {user['aadhaar_no']}")
            report.append(f"  Name: {user['name']}")
            report.append(f"  Phone: {user['phone']}")
            report.append(f"  City: {user['city']}")
            report.append(f"  Suspicious: {user['is_suspicious']}")
            if user['suspicious_types']:
                report.append(f"  Suspicious Types: {', '.join(user['suspicious_types'])}")
            report.append("")
            
            # Activity Summary
            activity = investigation['activity_summary']
            report.append("ACTIVITY SUMMARY:")
            report.append(f"  Total Sessions: {activity.get('total_sessions', 0)}")
            report.append(f"  Data Upload: {activity.get('total_upload_mb', 0)} MB")
            report.append(f"  Data Download: {activity.get('total_download_mb', 0)} MB")
            report.append(f"  Unique Destinations: {activity.get('unique_destinations', 0)}")
            report.append(f"  Suspicious Sessions: {activity.get('suspicious_sessions', 0)}")
            report.append("")
            
            # Communication Partners
            partners = investigation['communication_partners']
            report.append(f"COMMUNICATION PARTNERS ({len(partners)}):")
            for i, partner in enumerate(partners[:10]):  # Show top 10
                report.append(f"  {i+1}. IP: {partner['destination_ip']}")
                report.append(f"     Sessions: {partner['total_sessions']}")
                report.append(f"     Upload: {partner['total_upload'] / (1024*1024):.2f} MB")
                report.append(f"     Download: {partner['total_download'] / (1024*1024):.2f} MB")
                report.append("")
            
            # Anomalies
            anomalies = investigation['anomalies']
            if anomalies:
                report.append("DETECTED ANOMALIES:")
                for anomaly in anomalies:
                    report.append(f"  • {anomaly['description']} (Severity: {anomaly['severity']})")
                report.append("")
            
            report.append("=" * 60)
            report.append("END OF REPORT")
            report.append("=" * 60)
            
            return "\n".join(report)
            
        except Exception as e:
            logger.error(f"Error generating investigation report: {str(e)}")
            return f"Error generating report: {str(e)}"
