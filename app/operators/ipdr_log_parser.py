# app/parsers/ipdr_log_parser.py
import csv
from sqlmodel import Session
from datetime import datetime
from app.operators.base_parser import BaseParser
from app.models.ipdr_log_model import IPDRLogModel
from app.crud.ipdr_crud import IPDRLogCRUD

class IPDRLogCSVParser(BaseParser):
    """
    Parses a CSV file containing IPDR log data and loads it into the database.
    
    Assumes CSV format:
    AadhaarNo,IMEI,MSISDN,StartTime,EndTime,SourceIP,SourcePort,DestinationIP,DestinationPort,
    Protocol,BytesUpload,BytesDownload,Service,AppName,ISP,CellTowerID,LAC,SessionType,
    DataType,ConnectionQuality
    """
    
    def __init__(self, crud_instance: IPDRLogCRUD):
        self.ipdr_crud = crud_instance

    def parse_and_load(self, file_path: str, session: Session) -> None:
        """
        Parses the IPDR log CSV and inserts records into the database.
        """
        print(f"Starting to parse IPDR log file: {file_path}")
        try:
            with open(file_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                logs_to_create = []
                for row in reader:
                    # Convert string times to datetime objects
                    start_time = datetime.fromisoformat(row["StartTime"])
                    end_time = datetime.fromisoformat(row["EndTime"])
                    
                    # Calculate duration in seconds
                    duration = (end_time - start_time).total_seconds()

                    log_data = IPDRLogModel(
                        AadhaarNo=row["AadhaarNo"],
                        IMEI=row["IMEI"],
                        MSISDN=row["MSISDN"],
                        StartTime=start_time,
                        EndTime=end_time,
                        Duration=int(duration),
                        SourceIP=row["SourceIP"],
                        SourcePort=int(row["SourcePort"]),
                        DestinationIP=row["DestinationIP"],
                        DestinationPort=int(row["DestinationPort"]),
                        Protocol=row["Protocol"],
                        BytesUpload=int(row["BytesUpload"]),
                        BytesDownload=int(row["BytesDownload"]),
                        Service=row["Service"],
                        AppName=row.get("AppName", "Unknown"),
                        ISP=row["ISP"],
                        CellTowerID=row["CellTowerID"],
                        LAC=row["LAC"],
                        SessionType=row["SessionType"],
                        DataType=row["DataType"],
                        ConnectionQuality=row.get("ConnectionQuality", "Good")
                    )
                    logs_to_create.append(log_data)
                
                # Insert all logs in a single transaction for efficiency
                if logs_to_create:
                    session.add_all(logs_to_create)
                    session.commit()
                    print(f"Successfully loaded {len(logs_to_create)} IPDR logs into the database.")

        except FileNotFoundError:
            print(f"Error: File not found at {file_path}")
        except Exception as e:
            print(f"An error occurred while parsing IPDR logs: {e}")