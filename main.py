# main.py
from sqlmodel import Session
from app.core.database import init_db, engine
from app.core.logger import get_logger

# Business Service classes ko import karein
from app.services.user_service import UserService
from app.services.ipdr_service import IPDRService

# Parser classes ko import karein
from app.operators.dummy_parser import UserCSVParser
from app.operators.ipdr_log_parser import IPDRLogCSVParser

# Logger setup
logger = get_logger(__name__)

def main():
    """
    Main function to initialize the database and load data from CSV files.
    Uses business service layer for better separation of concerns.
    """
    logger.info("=== IPDR Analysis System Started ===")
    
    try:
        # Step 1: Database aur Tables ko initialize karein
        logger.info("Initializing database...")
        init_db()
        
        # Step 2: Business Service instances banayein
        user_service = UserService()
        ipdr_service = IPDRService()
        
        # Step 3: Parser instances banayein with CRUD from services
        user_parser = UserCSVParser(crud_instance=user_service.crud)
        ipdr_parser = IPDRLogCSVParser(crud_instance=ipdr_service.crud)

        # Step 4: Database session praapt karein
        with Session(engine) as session:
            logger.info("Loading User Data...")
            user_parser.parse_and_load(
                file_path="Generator/realistic_users_24h_20250824_021654.csv", 
                session=session
            )
            
            logger.info("Loading IPDR Log Data...")
            ipdr_parser.parse_and_load(
                file_path="Generator/realistic_ipdr_24h_20250824_021654.csv", 
                session=session
            )
            
            # Demonstration of business service capabilities
            logger.info("=== Demonstrating Business Service Features ===")
            
            # Count records
            user_count = user_service.count_records(session)
            ipdr_count = ipdr_service.count_records(session)
            logger.info(f"Total Users: {user_count}")
            logger.info(f"Total IPDR Logs: {ipdr_count}")
            
            # Find suspicious users
            suspicious_users = user_service.find_suspicious_users(session)
            logger.info(f"Suspicious Users Found: {len(suspicious_users)}")
            
            # Find suspicious logs
            suspicious_logs = ipdr_service.find_suspicious_logs(session)
            logger.info(f"Suspicious Logs Found: {len(suspicious_logs)}")

        logger.info("=== IPDR Analysis System Completed Successfully ===")
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        raise

if __name__ == "__main__":
    main()