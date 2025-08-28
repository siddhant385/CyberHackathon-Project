# app/handlers/suspicious_analysis_handler.py
from sqlmodel import Session
from app.handlers.base_handler import BaseHandler
from app.core.logger import get_logger
from app.core.database import engine
from app.services.user_service import UserService
from app.services.ipdr_service import IpdrService
from app.services.investigation_service import InvestigationService
import pandas as pd

logger = get_logger(__name__)

class SuspiciousAnalysisHandler(BaseHandler):
    """
    Handler for running suspicious user analysis.
    """

    def handle(self):
        """
        Executes the suspicious user analysis and report generation.
        """
        logger.info("🚨 Running suspicious user analysis...")
        try:
            with Session(engine) as session:
                user_service = UserService()
                investigation_service = InvestigationService()

                logger.info("Identifying suspicious users based on activity patterns...")
                suspicious_users = user_service.find_suspicious_users(session)
                
                if not suspicious_users:
                    logger.warning("⚠️ No suspicious users found in the database.")
                    return

                report_path = "reports/suspicious_analysis_report.txt"
                logger.info(f"Generating suspicious analysis report at: {report_path}")

                with open(report_path, "w") as f:
                    self._write_report_header(f, len(suspicious_users))

                    for i, user in enumerate(suspicious_users, 1):
                        self._write_user_section(f, user, i, session, investigation_service)

                logger.info(f"✅ Suspicious analysis report generated successfully.")
                print(f"\n📄 Report saved to {report_path}")

        except Exception as e:
            logger.error(f"❌ Suspicious analysis failed: {str(e)}")
            raise

    def _write_report_header(self, f, count):
        f.write("="*80 + "\n")
        f.write("🚨 SUSPICIOUS USER ACTIVITY ANALYSIS REPORT\n")
        f.write("="*80 + "\n\n")
        f.write(f"A total of {count} suspicious users were identified based on their activity patterns, such as:\n")
        f.write("- Unusually high data consumption\n")
        f.write("- Communication with a large number of unique B-parties\n")
        f.write("- Activity during odd hours (e.g., 1 AM - 5 AM)\n\n")

    def _write_user_section(self, f, user, index, session, investigation_service):
        f.write("-" * 70 + "\n")
        f.write(f"SUSPICIOUS USER #{index}\n")
        f.write("-" * 70 + "\n")
        f.write(f"👤 Name:         {user.Name}\n")
        f.write(f"🆔 Aadhaar:      {user.AadhaarNo}\n")
        f.write(f"📞 Phone:        {user.PhoneNo}\n")
        f.write(f"🏠 Address:      {user.Address}\n\n")

        # Get a summary from the investigation service
        summary = investigation_service.get_user_summary(session, user.AadhaarNo)
        
        f.write("📊 Activity Summary:\n")
        f.write(f"   - Total Sessions: {summary['total_sessions']}\n")
        f.write(f"   - Total Data Usage: {summary['total_data_usage_gb']:.2f} GB\n")
        f.write(f"   - First Seen: {summary['first_seen']}\n")
        f.write(f"   - Last Seen: {summary['last_seen']}\n\n")

        f.write("🕒 Temporal Analysis:\n")
        if summary['off_hours_activity_percentage'] > 0:
            f.write(f"   - ❗️ Operates during odd hours: {summary['off_hours_activity_percentage']:.2f}% of activity is between 1 AM and 5 AM.\n")
        else:
            f.write("   - Normal operating hours observed.\n")
        
        f.write(f"   - Most Active Day: {summary['most_active_day']}\n\n")

        f.write("🤝 Communication Network:\n")
        f.write(f"   - Unique B-Parties: {summary['unique_b_parties']}\n")
        f.write(f"   - Top Contact (by frequency): {summary['top_b_party_by_freq']}\n")
        f.write(f"   - Top Contact (by data): {summary['top_b_party_by_data']} ({summary['top_b_party_data_gb']:.2f} GB)\n\n")
        
        f.write("✍️ Analyst's Note: This user is flagged due to a combination of high data usage, a wide communication network, and/or off-hours activity. Further investigation is recommended.\n\n")

