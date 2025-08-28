# models/user_model.py
import re
from typing import List, Dict
from pydantic import BaseModel, validator

class UserModel(BaseModel):
    AadhaarNo: str
    Name: str
    Age: int
    Address: str
    Email: str
    PhoneNo: str
    City: str
    State: str
    Devices: List[str] = []
    AssignedIPs: List[str] = []
    ISP: str = "Unknown"
    IsSuspicious: bool = False
    SuspiciousType: List[str] = []
    HomeLocation: Dict[str, float] = {}
    UsualActiveHours: List[int] = []

    @validator('AadhaarNo')
    def validate_aadhaar(cls, v):
        if not re.match(r'^\d{12}$', v):
            raise ValueError('Aadhaar must be exactly 12 digits')
        return v

    @validator('PhoneNo')
    def validate_phone(cls, v):
        if not re.match(r'^[6-9]\d{9}$', v):
            raise ValueError('Invalid Indian phone number')
        return v