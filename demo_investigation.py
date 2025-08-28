# demo_investigation.py
"""
Demo script to showcase IPDR investigation capabilities
"""
from sqlmodel import Session
from app.core.database import init_db, engine
from app.core.logger import get_logger
from app.services.investigation_service import InvestigationService
from app.services.user_service import UserService
from app.services.ipdr_service import IPDRService

logger = get_logger(__name__)

def demo_investigation_features():
    """
    Demonstrate advanced investigation features
    """
    logger.info("=== IPDR Investigation Demo ===")
    
    try:
        # Initialize services
        investigation_service = InvestigationService()
        user_service = UserService()
        ipdr_service = IPDRService()
        
        with Session(engine) as session:
            # Get first user for demonstration
            users = user_service.get_multiple_records(session, limit=5)
            
            if not users:
                logger.warning("No users found. Please run main.py first to load data.")
                return
            
            demo_user = users[0]
            logger.info(f"Demo User: {demo_user.Name} ({demo_user.AadhaarNo})")
            
            # 1. User Activity Summary
            logger.info("\n--- User Activity Summary ---")
            activity_summary = ipdr_service.get_user_activity_summary(session, demo_user.AadhaarNo)
            for key, value in activity_summary.items():
                logger.info(f"{key}: {value}")
            
            # 2. Communication Partners (B-parties)
            logger.info("\n--- Communication Partners (B-parties) ---")
            partners = ipdr_service.find_communication_partners(session, demo_user.AadhaarNo)
            logger.info(f"Found {len(partners)} communication partners")
            
            for i, partner in enumerate(partners[:3]):  # Show top 3
                logger.info(f"{i+1}. IP: {partner['destination_ip']}")
                logger.info(f"   Sessions: {partner['total_sessions']}")
                logger.info(f"   Data: {partner['total_upload']/(1024*1024):.1f}MB up, {partner['total_download']/(1024*1024):.1f}MB down")
            
            # 3. Full Investigation Report
            logger.info("\n--- Comprehensive Investigation ---")
            investigation_report = investigation_service.investigate_user_relationships(session, demo_user.AadhaarNo)
            
            if 'error' not in investigation_report:
                logger.info("Investigation completed successfully!")
                logger.info(f"Anomalies detected: {len(investigation_report.get('anomalies', []))}")
                
                # Display anomalies
                for anomaly in investigation_report.get('anomalies', []):
                    logger.warning(f"Anomaly: {anomaly['description']}")
            
            # 4. Connected Users Network
            logger.info("\n--- Connected Users Network ---")
            connected_users = investigation_service.find_connected_users(session, demo_user.AadhaarNo)
            logger.info(f"Found {len(connected_users)} connected users")
            
            for connected in connected_users[:3]:  # Show top 3
                logger.info(f"Connected: {connected['name']} via {connected['common_destination']}")
            
            # 5. Generate Text Report
            logger.info("\n--- Generating Investigation Report ---")
            text_report = investigation_service.generate_investigation_report(session, demo_user.AadhaarNo)
            
            # Save report to file
            report_filename = f"investigation_report_{demo_user.AadhaarNo}.txt"
            with open(report_filename, 'w', encoding='utf-8') as f:
                f.write(text_report)
            
            logger.info(f"Investigation report saved to: {report_filename}")
            
            # 6. High Traffic Analysis
            logger.info("\n--- High Traffic Analysis ---")
            high_traffic = ipdr_service.analyze_high_traffic_sessions(session, threshold_mb=50)
            logger.info(f"Found {len(high_traffic)} high traffic sessions (>50MB)")
            
            # 7. Suspicious Activity
            logger.info("\n--- Suspicious Activity Analysis ---")
            suspicious_users = user_service.find_suspicious_users(session)
            suspicious_logs = ipdr_service.find_suspicious_logs(session)
            
            logger.info(f"Suspicious users: {len(suspicious_users)}")
            logger.info(f"Suspicious logs: {len(suspicious_logs)}")
            
        logger.info("\n=== Investigation Demo Completed ===")
        
    except Exception as e:
        logger.error(f"Error in investigation demo: {str(e)}")
        raise

if __name__ == "__main__":
    # Make sure database is initialized
    init_db()
    demo_investigation_features()
