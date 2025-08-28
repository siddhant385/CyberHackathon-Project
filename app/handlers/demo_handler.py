# app/handlers/demo_handler.py
from app.handlers.base_handler import BaseHandler
from app.core.logger import get_logger
from app.services.user_service import UserService
from app.services.investigation_service import InvestigationService
from sqlmodel import Session
from app.core.database import engine

logger = get_logger(__name__)

class DemoHandler(BaseHandler):
    """
    Handler for running the investigation demonstration.
    """

    def handle(self):
        """
        Executes the demonstration by finding a suspicious user and investigating them.
        """
        logger.info("🔍 Running investigation demonstration...")
        try:
            with Session(engine) as session:
                user_service = UserService()
                investigation_service = InvestigationService()

                # 1. Find a suspicious user to be the subject of the demo
                logger.info("Identifying a suspicious user for the demo...")
                suspicious_users = user_service.find_suspicious_users(session, limit=1)
                
                if not suspicious_users:
                    logger.warning("⚠️ No suspicious users found to run the demo. Please load data first.")
                    return

                target_user = suspicious_users[0]
                logger.info(f"🎯 Selected suspicious user for demo: {target_user.Name} ({target_user.AadhaarNo})")

                # 2. Run the investigation service on that user
                logger.info(f"Running a full investigation on {target_user.AadhaarNo}...")
                investigation_service.investigate_user(
                    db=session, 
                    aadhaar_no=target_user.AadhaarNo, 
                    save_report=True, 
                    visualize_graph=True
                )

            logger.info("✅ Investigation demo completed successfully.")

        except Exception as e:
            logger.error(f"❌ Investigation demo failed: {str(e)}")
            # In a real scenario, you might want to handle this more gracefully
            # For the demo, re-raising helps in debugging.
            raise
        except Exception as e:
            logger.error(f"❌ Investigation demo failed: {str(e)}")
            raise
