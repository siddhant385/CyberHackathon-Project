# app/models/user_model.py
from typing import Dict, List
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, JSON

from pydantic import validator
import re

class UserModel(SQLModel, table=True):
    """
    Represents a user in the database.
    The primary key is AadhaarNo.
    """
    # Fields
    AadhaarNo: str = Field(primary_key=True)
    Name: str
    Age: int
    Address: str
    Email: str
    PhoneNo: str = Field(unique=False)
    City: str
    State: str
    Devices: List[str] = Field(default=[], sa_column=Column(JSON))
    AssignedIPs: List[str] = Field(default=[], sa_column=Column(JSON))
    ISP: str = "Unknown"
    IsSuspicious: bool = False
    SuspiciousType: List[str] = Field(default=[], sa_column=Column(JSON))
    HomeLocation: Dict[str, float] = Field(default={}, sa_column=Column(JSON))
    UsualActiveHours: List[int] = Field(default=[], sa_column=Column(JSON))
    # Devices: List[str] = Field(default=[])
    # AssignedIPs: List[str] = Field(default=[])
    # ISP: str = "Unknown"
    # IsSuspicious: bool = False
    # SuspiciousType: List[str] = Field(default=[])
    # HomeLocation: Dict[str, float] = Field(default={})
    # UsualActiveHours: List[int] = Field(default=[])

    # Validators
    @validator('AadhaarNo')
    def validate_aadhaar(cls, v):
        if not re.match(r'^\d{12}$', v):
            raise ValueError('Aadhaar must be exactly 12 digits')
        return v

    @validator('PhoneNo')
    def validate_phone(cls, v):
        if not re.match(r'^[6-9]\d{9}$', v):
            raise ValueError('Invalid 10-digit Indian phone number')
        return v