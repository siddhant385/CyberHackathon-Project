# app/parsers/dummy_parser.py
import csv
from sqlmodel import Session
from app.operators.base_parser import BaseParser
from app.models.user_model import UserModel
from app.crud.user_crud import UserCRUD

class UserCSVParser(BaseParser):
    """
    A dummy parser to read user data from a CSV file and load it into the database.
    Assumes CSV format: AadhaarNo,Name,Age,Address,Email,PhoneNo,City,State,ISP
    """
    
    def __init__(self, crud_instance: UserCRUD):
        self.user_crud = crud_instance

    def parse_and_load(self, file_path: str, session: Session) -> None:
        """
        Parses a CSV file with user data and inserts it into the database.
        """
        print(f"Starting to parse file: {file_path}")
        try:
            with open(file_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                users_to_create = []
                for row in reader:
                    user_data = UserModel(
                        AadhaarNo=row["AadhaarNo"],
                        Name=row["Name"],
                        Age=int(row["Age"]),
                        Address=row["Address"],
                        Email=row["Email"],
                        PhoneNo=row["PhoneNo"],
                        City=row["City"],
                        State=row["State"],
                        ISP=row.get("ISP", "Unknown") # .get for optional fields
                    )
                    users_to_create.append(user_data)
                
                # Insert users with duplicate handling
                created_count = 0
                duplicate_count = 0
                error_count = 0
                
                for user in users_to_create:
                    try:
                        # Check if user already exists
                        existing_user = self.user_crud.read(session, user.AadhaarNo)
                        if existing_user:
                            duplicate_count += 1
                            print(f"Duplicate user skipped: {user.AadhaarNo} - {user.Name}")
                            continue
                        
                        self.user_crud.create(session, user)
                        created_count += 1
                        
                    except Exception as user_error:
                        error_count += 1
                        print(f"Error creating user {user.AadhaarNo}: {str(user_error)}")
                        continue

            print(f"Successfully processed {file_path}")
            print(f"Created: {created_count}, Duplicates: {duplicate_count}, Errors: {error_count}")

        except FileNotFoundError:
            print(f"Error: File not found at {file_path}")
        except Exception as e:
            print(f"An error occurred: {e}")
            raise