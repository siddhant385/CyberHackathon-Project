# app/handlers/investigation_handler.py
from app.handlers.base_handler import BaseHandler
from app.core.logger import get_logger
from app.services.investigation_service import InvestigationService
from app.core.database import engine
from sqlmodel import Session

logger = get_logger(__name__)

class InvestigationHandler(BaseHandler):
    """
    Handler for performing a detailed investigation on a specific user.
    """

    def __init__(self, aadhaar_no: str):
        if not aadhaar_no or not aadhaar_no.isdigit() or len(aadhaar_no) != 12:
            raise ValueError("A valid 12-digit Aadhaar number is required.")
        self.aadhaar_no = aadhaar_no

    def handle(self):
        """
        Executes the investigation process.
        """
        logger.info(f"🔍 Starting investigation for user: {self.aadhaar_no}")
        try:
            with Session(engine) as session:
                investigation_service = InvestigationService()
                investigation_service.investigate_user(
                    db=session,
                    aadhaar_no=self.aadhaar_no,
                    save_report=True,
                    visualize_graph=True
                )
            logger.info("✅ Investigation completed successfully.")
        except Exception as e:
            logger.error(f"❌ Investigation error: {str(e)}")
            raise
