# main.py
from sqlmodel import Session
from app.core.database import init_db, get_session, engine

# CRUD classes ko import karein
from app.crud.user_crud import UserCRUD
from app.crud.ipdr_crud import IPDRLogCRUD

# Parser classes ko import karein
from app.operators.dummy_parser import UserCSVParser
from app.operators.ipdr_log_parser import IPDRLogCSVParser

def main():
    """
    Main function to initialize the database and load data from CSV files.
    """
    print("--- Script Started ---")
    
    # Step 1: Database aur Tables ko initialize karein
    # Yeh function aapke models ke aadhar par saari tables bana dega.
    # Isko sirf pehli baar chalane ki zaroorat hai.
    init_db()

    # Step 2: CRUD aur Parser instances banayein
    user_crud = UserCRUD()
    ipdr_crud = IPDRLogCRUD()
    
    user_parser = UserCSVParser(crud_instance=user_crud)
    ipdr_parser = IPDRLogCSVParser(crud_instance=ipdr_crud)

    # Step 3: Database session praapt karein
    # 'with' statement use karne se session automatically close ho jaata hai.
    with Session(engine) as session:
        print("\n--- Loading User Data ---")
        # Apne user data CSV file ka path yahaan dein
        user_parser.parse_and_load(file_path="Generator/realistic_users_24h_20250824_021654.csv", session=session)
        
        print("\n--- Loading IPDR Log Data ---")
        # Apne IPDR logs CSV file ka path yahaan dein
        ipdr_parser.parse_and_load(file_path="Generator/realistic_ipdr_24h_20250824_021654.csv", session=session)

    print("\n--- Script Finished ---")

if __name__ == "__main__":
    main()