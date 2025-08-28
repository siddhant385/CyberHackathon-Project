# app/handlers/load_data_handler.py
from app.handlers.base_handler import BaseHandler
from app.core.logger import get_logger
from app.services.user_service import UserService
from app.services.ipdr_service import IpdrService
from app.core.database import engine
from sqlmodel import Session, text

logger = get_logger(__name__)

class LoadDataHandler(BaseHandler):
    """
    Handler for loading sample data into the system.
    """

    def __init__(self, clear_data: bool = False):
        self.clear_data = clear_data

    def handle(self):
        """
        Executes the data loading process.
        """
        if self.clear_data:
            self._clear_existing_data()

        logger.info("🚀 Loading sample data...")
        try:
            user_service = UserService()
            ipdr_service = IpdrService()

            # Define paths to the sample data files
            user_data_path = "Generator/realistic_users_24h_20250824_021654.csv"
            ipdr_data_path = "Generator/realistic_ipdr_24h_20250824_021654.csv"

            # Load users
            if user_service.count_users() == 0:
                logger.info(f"Loading users from {user_data_path}...")
                user_service.load_users_from_csv(user_data_path)
                logger.info("✅ Users loaded successfully.")
            else:
                logger.info("Users already exist in the database. Skipping user loading.")

            # Load IPDR logs
            if ipdr_service.count_logs() == 0:
                logger.info(f"Loading IPDR logs from {ipdr_data_path}...")
                ipdr_service.load_ipdr_logs_from_csv(ipdr_data_path)
                logger.info("✅ IPDR logs loaded successfully.")
            else:
                logger.info("IPDR logs already exist in the database. Skipping log loading.")
            
            logger.info("✅ Sample data loading process completed.")

        except Exception as e:
            logger.error(f"❌ Failed to load sample data: {str(e)}")
            raise

    def _clear_existing_data(self):
        """Clears existing user and IPDR data from the database."""
        logger.info("🔄 Clearing existing data...")
        try:
            with Session(engine) as session:
                session.exec(text("DELETE FROM ipdrlogmodel"))
                session.exec(text("DELETE FROM usermodel"))
                session.commit()
                logger.info("🗑️ Existing data cleared successfully.")
        except Exception as e:
            logger.error(f"❌ Failed to clear data: {str(e)}")
            raise
