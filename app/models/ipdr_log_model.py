from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional, List, Dict
from datetime import datetime
import ipaddress


class IPDRLogModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    AadhaarNo: str
    IMEI: str
    MSISDN: str
    StartTime: datetime
    EndTime: datetime
    Duration: int

    SourceIP: str
    SourcePort: int
    DestinationIP: str
    DestinationPort: int

    Protocol: str
    BytesUpload: int
    BytesDownload: int
    Service: str
    AppName: Optional[str] = "Unknown"
    ISP: str
    CellTowerID: str
    LAC: str
    SessionType: str
    DataType: str

    # ✅ Store Dict and List as JSON
    Location: Dict[str, float] = Field(default={}, sa_column=Column(JSON))
    IsSuspicious: bool = False
    SuspiciousFlags: List[str] = Field(default=[], sa_column=Column(JSON))
    ConnectionQuality: str = "Good"

    # ✅ Validator for IPs
    @staticmethod
    def validate_ip(ip: str) -> str:
        try:
            ipaddress.ip_address(ip)
            return ip
        except ValueError:
            raise ValueError(f"Invalid IP address: {ip}")
