# models/ipdr_model.py
import re
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, validator, IPvAnyAddress

class IPDRModel(BaseModel):
    RecordID: str
    AadhaarNo: str
    IMEI: str
    MSISDN: str
    StartTime: datetime
    EndTime: datetime
    Duration: int
    SourceIP: IPvAnyAddress
    SourcePort: int
    DestinationIP: IPvAnyAddress
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
    Location: Dict[str, float] = {}
    IsSuspicious: bool = False
    SuspiciousFlags: List[str] = []
    ConnectionQuality: str = "Good"

    @validator('IMEI')
    def validate_imei(cls, v):
        if not re.match(r'^\d{15}$', v):
            raise ValueError('IMEI must be exactly 15 digits')
        return v