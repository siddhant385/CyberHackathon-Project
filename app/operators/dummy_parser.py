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
                
                # Bulk insert can be done here if needed
                for user in users_to_create:
                    self.user_crud.create(session, user)

            print(f"Successfully parsed and loaded data from {file_path}")

        except FileNotFoundError:
            print(f"Error: File not found at {file_path}")
        except Exception as e:
            print(f"An error occurred: {e}")