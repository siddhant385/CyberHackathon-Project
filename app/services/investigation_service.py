# app/services/investigation_service.py
from typing import List, Dict, Any, Optional, Tuple
from sqlmodel import Session, select, and_, or_, func
from datetime import datetime, timedelta
import networkx as nx
import matplotlib.pyplot as plt
import os

from app.services.user_service import UserService
from app.services.ipdr_service import IpdrService
from app.services.geoip_service import GeoIPService
from app.models.user_model import UserModel
from app.models.ipdr_log_model import IPDRLogModel
from app.core.logger import get_logger
from app.core.config import settings

logger = get_logger(__name__)

class InvestigationService:
    """
    High-level investigation service that combines user and IPDR data
    for comprehensive analysis and investigation features.
    """
    
    def __init__(self):
        self.user_service = UserService()
        self.ipdr_service = IpdrService()
        self.geoip_service = GeoIPService()

    def investigate_user(self, db: Session, aadhaar_no: str, save_report: bool = False, visualize_graph: bool = False) -> Optional[Dict[str, Any]]:
        """
        Complete investigation of a user's digital relationships and patterns.
        Core functionality for investigators.
        """
        try:
            logger.info(f"Starting full investigation for user: {aadhaar_no}")
            
            user = self.user_service.get_record(db, aadhaar_no)
            if not user:
                logger.error(f"User with Aadhaar No {aadhaar_no} not found.")
                return None

            summary = self.get_user_summary(db, aadhaar_no)
            
            if save_report:
                self._generate_investigation_report(user, summary)

            if visualize_graph:
                self._visualize_network_graph(user, summary['network_analysis']['nodes'], summary['network_analysis']['edges'])

            logger.info(f"Investigation completed for user: {aadhaar_no}")
            return summary

        except Exception as e:
            logger.error(f"Error during full investigation for {aadhaar_no}: {e}", exc_info=True)
            return None

    def get_user_summary(self, db: Session, aadhaar_no: str) -> Dict[str, Any]:
        """
        Gathers a comprehensive summary of a user's activity and network.
        """
        user = self.user_service.get_record(db, aadhaar_no)
        if not user:
            raise ValueError(f"User {aadhaar_no} not found")

        user_logs = self.ipdr_service.get_logs_by_user(db, aadhaar_no)
        
        # Basic stats
        total_data_usage_gb = sum(log.BytesUpload + log.BytesDownload for log in user_logs) / (1024**3)
        first_seen = min(log.StartTime for log in user_logs) if user_logs else None
        last_seen = max(log.EndTime for log in user_logs) if user_logs else None

        # Temporal analysis
        hourly_activity = [log.StartTime.hour for log in user_logs]
        off_hours_activity = [h for h in hourly_activity if h <= 5 or h >= 23]
        off_hours_percentage = (len(off_hours_activity) / len(hourly_activity) * 100) if hourly_activity else 0
        most_active_day = max(set(log.StartTime.strftime('%A') for log in user_logs), key=list(log.StartTime.strftime('%A') for log in user_logs).count) if user_logs else "N/A"

        # Communication network
        partners = self.ipdr_service.find_communication_partners(db, aadhaar_no)
        
        # Enrich partners with GeoIP data
        for partner in partners:
            partner['location'] = self.geoip_service.get_ip_location(partner['destination_ip'])

        top_partner_by_freq = partners[0]['destination_ip'] if partners else "N/A"
        top_partner_by_data = max(partners, key=lambda p: p['total_download_mb'] + p['total_upload_mb']) if partners else {}
        
        # NetworkX analysis
        network_analysis = self.analyze_network_cluster(db, aadhaar_no, depth=settings.NETWORK_ANALYSIS_MAX_DEPTH)

        return {
            "user_details": user,
            "total_sessions": len(user_logs),
            "total_data_usage_gb": total_data_usage_gb,
            "first_seen": first_seen,
            "last_seen": last_seen,
            "off_hours_activity_percentage": off_hours_percentage,
            "most_active_day": most_active_day,
            "unique_b_parties": len(partners),
            "top_b_party_by_freq": top_partner_by_freq,
            "top_b_party_by_data": top_partner_by_data.get('destination_ip', "N/A"),
            "top_b_party_data_gb": (top_partner_by_data.get('total_download_mb', 0) + top_partner_by_data.get('total_upload_mb', 0)) / 1024,
            "communication_partners": partners,
            "network_analysis": network_analysis
        }

    def _generate_investigation_report(self, user: UserModel, summary: Dict[str, Any]):
        """Generates and saves a detailed text report for an investigation."""
        report_path = f"reports/enhanced_investigation_{user.AadhaarNo}.txt"
        logger.info(f"Generating investigation report at {report_path}")
        
        os.makedirs("reports", exist_ok=True)
        
        with open(report_path, "w") as f:
            f.write("="*80 + "\n")
            f.write("ENHANCED INVESTIGATION REPORT\n")
            f.write("="*80 + "\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write(f"--- SUBJECT DETAILS ---\n")
            f.write(f"  Name: {user.Name}\n")
            f.write(f"  Aadhaar: {user.AadhaarNo}\n")
            f.write(f"  Phone: {user.PhoneNo}\n")
            f.write(f"  Address: {user.Address}\n")
            f.write(f"  ISP: {user.ISP}\n")
            f.write(f"  Known Devices: {', '.join(user.Devices)}\n\n")

            f.write(f"--- EXECUTIVE SUMMARY ---\n")
            f.write(f"  Subject '{user.Name}' was investigated based on suspicious activity flags: {', '.join(user.SuspiciousType)}.\n")
            f.write(f"  The subject conducted {summary['total_sessions']} sessions, consuming {summary['total_data_usage_gb']:.2f} GB of data.\n")
            f.write(f"  A significant portion of activity ({summary['off_hours_activity_percentage']:.2f}%) occurred during off-hours.\n")
            f.write(f"  The subject communicated with {summary['unique_b_parties']} unique B-parties.\n\n")

            f.write(f"--- TEMPORAL ANALYSIS ---\n")
            f.write(f"  First Activity: {summary['first_seen']}\n")
            f.write(f"  Last Activity: {summary['last_seen']}\n")
            f.write(f"  Most Active Day: {summary['most_active_day']}\n")
            f.write(f"  Off-Hours Activity (11pm-5am): {summary['off_hours_activity_percentage']:.2f}%\n\n")

            f.write(f"--- COMMUNICATION NETWORK ANALYSIS ---\n")
            f.write(f"  Unique B-Parties Contacted: {summary['unique_b_parties']}\n")
            f.write(f"  Most Frequent Contact (by sessions): {summary['top_b_party_by_freq']}\n")
            f.write(f"  Largest Data Transfer Contact: {summary['top_b_party_by_data']} ({summary['top_b_party_data_gb']:.2f} GB)\n\n")
            
            f.write("  Top 10 B-Party Contacts (Enriched with GeoIP):\n")
            for i, partner in enumerate(summary['communication_partners'][:10]):
                location_info = "Location: Private or Not Found"
                if partner.get('location'):
                    loc = partner['location']
                    location_info = f"Location: {loc.get('city', 'N/A')}, {loc.get('country', 'N/A')} (ISP: {loc.get('isp', 'N/A')})"

                f.write(f"    {i+1}. IP: {partner['destination_ip']}\n")
                f.write(f"       - {location_info}\n")
                f.write(f"       - Sessions: {partner['total_sessions']}\n")
                f.write(f"       - Data Exchanged: {partner['total_upload_mb'] + partner['total_download_mb']:.2f} MB\n")
            f.write("\n")

            f.write(f"--- RELATIONSHIP GRAPH (1st & 2nd Degree Connections) ---\n")
            nodes = summary['network_analysis']['nodes']
            edges = summary['network_analysis']['edges']
            f.write(f"  The network graph contains {len(nodes)} nodes and {len(edges)} edges.\n")
            for node in nodes:
                if node['id'] != user.AadhaarNo:
                    f.write(f"  - Connected User: {node['name']} ({node['id']}), Degree: {node['depth']}\n")
            f.write("\n")

            f.write("="*80 + "\n")
            f.write("END OF REPORT\n")
            f.write("="*80 + "\n")

    def _visualize_network_graph(self, user: UserModel, nodes: List[Dict], edges: List[Dict]):
        """Creates and saves a visualization of the network graph."""
        graph_path = f"reports/network_graph_{user.AadhaarNo}.png"
        logger.info(f"Generating network visualization at {graph_path}")

        os.makedirs("reports", exist_ok=True)

        G = nx.Graph()
        
        # Add nodes and edges
        for node in nodes:
            G.add_node(node['id'], name=node['name'], is_suspicious=node.get('is_suspicious', False), depth=node['depth'])
        for edge in edges:
            G.add_edge(edge['from'], edge['to'], weight=edge.get('strength', 1))

        # Position nodes
        pos = nx.spring_layout(G, k=0.5, iterations=50)

        # Drawing properties
        plt.figure(figsize=(16, 12))
        node_colors = ['red' if n == user.AadhaarNo else ('orange' if G.nodes[n].get('is_suspicious') else 'skyblue') for n in G.nodes]
        node_sizes = [5000 if n == user.AadhaarNo else 2500 for n in G.nodes]
        labels = {n: G.nodes[n]['name'] for n in G.nodes}

        nx.draw(G, pos, labels=labels, with_labels=True, node_color=node_colors, node_size=node_sizes, font_size=10, font_weight='bold', edge_color='gray')
        
        plt.title(f"Communication Network for {user.Name} ({user.AadhaarNo})", size=20)
        plt.savefig(graph_path)
        plt.close()

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
            
            logger.debug(f"Found {len(connected_users)} connected users for: {aadhaar_no}")
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
            nodes = []
            edges = []
            
            queue = [(center_aadhaar, 0)]
            
            while queue:
                current_aadhaar, current_depth = queue.pop(0)

                if current_aadhaar in visited or current_depth > depth:
                    continue
                
                visited.add(current_aadhaar)
                
                user = self.user_service.get_record(session, current_aadhaar)
                if not user:
                    continue

                nodes.append({
                    'id': user.AadhaarNo,
                    'name': user.Name,
                    'is_suspicious': user.IsSuspicious,
                    'depth': current_depth
                })

                # Find B-parties for the current user
                partners = self.ipdr_service.find_communication_partners(session, current_aadhaar)
                common_ips = {p['destination_ip'] for p in partners}

                # Find other users who communicated with these B-parties
                if not common_ips:
                    continue

                # This part can be slow, consider optimizing for a real application
                for ip in common_ips:
                    related_logs = session.exec(select(IPDRLogModel).where(
                        and_(IPDRLogModel.DestinationIP == ip, IPDRLogModel.AadhaarNo != current_aadhaar)
                    )).all()

                    for log in related_logs:
                        neighbor_aadhaar = log.AadhaarNo
                        if neighbor_aadhaar not in visited:
                            edges.append({
                                'from': current_aadhaar,
                                'to': neighbor_aadhaar,
                                'strength': 1 # Simplified strength
                            })
                            if (neighbor_aadhaar, current_depth + 1) not in queue:
                                queue.append((neighbor_aadhaar, current_depth + 1))

            # Deduplicate edges
            unique_edges = [dict(t) for t in {tuple(sorted(d.items())) for d in edges}]

            return {'nodes': nodes, 'edges': unique_edges}
            
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
            investigation = self.investigate_user(session, aadhaar_no)
            
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
                report.append(f"  {i+1}. IP: {partner.get('destination_ip', 'N/A')}")
                report.append(f"     Sessions: {partner.get('total_sessions', 0)}")
                report.append(f"     Upload: {partner.get('total_upload_mb', 0.0):.2f} MB")
                report.append(f"     Download: {partner.get('total_download_mb', 0.0):.2f} MB")
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
