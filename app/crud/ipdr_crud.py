# app/crud/ipdr_crud.py
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlmodel import Session, select, and_, or_, func
from app.models.ipdr_log_model import IPDRLogModel
from app.crud.base import BaseCRUD
from sqlalchemy.orm.attributes import flag_modified


class IPDRLogCRUD(BaseCRUD[IPDRLogModel]):
    """
    CRUD operations for IPDRLogModel.
    
    This class handles database operations for IPDR (Internet Protocol
    Detail Records) logs, including specialized queries for network analysis.
    """
    
    def __init__(self):
        super().__init__(IPDRLogModel)
    
    def get_logs_by_aadhaar(
        self, 
        session: Session, 
        aadhaar_no: str,
        limit: int = 100
    ) -> List[IPDRLogModel]:
        """Get all network logs for a specific user, identified by Aadhaar."""
        statement = select(IPDRLogModel).where(
            IPDRLogModel.AadhaarNo == aadhaar_no
        ).limit(limit)
        return session.exec(statement).all()
    
    def get_logs_by_ip(
        self, 
        session: Session, 
        ip_address: str,
        is_source: bool = True,
        limit: int = 100
    ) -> List[IPDRLogModel]:
        """Get logs filtered by a specific IP address (either source or destination)."""
        if is_source:
            statement = select(IPDRLogModel).where(
                IPDRLogModel.SourceIP == ip_address
            ).limit(limit)
        else:
            statement = select(IPDRLogModel).where(
                IPDRLogModel.DestinationIP == ip_address
            ).limit(limit)
        return session.exec(statement).all()
    
    def get_logs_by_time_range(
        self,
        session: Session,
        start_time: datetime,
        end_time: datetime,
        aadhaar_no: Optional[str] = None
    ) -> List[IPDRLogModel]:
        """
        Get logs where the session started within a specific time period.
        Optionally filters for a specific user.
        """
        conditions = [
            IPDRLogModel.StartTime >= start_time,
            IPDRLogModel.StartTime <= end_time
        ]
        
        if aadhaar_no:
            conditions.append(IPDRLogModel.AadhaarNo == aadhaar_no)
        
        statement = select(IPDRLogModel).where(and_(*conditions))
        return session.exec(statement).all()

    def get_suspicious_logs(self, session: Session) -> List[IPDRLogModel]:
        """Get all logs that have been flagged as suspicious."""
        statement = select(IPDRLogModel).where(IPDRLogModel.IsSuspicious == True)
        return session.exec(statement).all()

    def get_connection_pairs(
        self,
        session: Session,
        source_ip: Optional[str] = None,
        dest_ip: Optional[str] = None,
        limit: int = 100
    ) -> List[IPDRLogModel]:
        """
        Get A-party to B-party connection logs for network analysis.
        - A-party = Source (initiator)
        - B-party = Destination (receiver)
        """
        conditions = []
        if source_ip:
            conditions.append(IPDRLogModel.SourceIP == source_ip)
        if dest_ip:
            conditions.append(IPDRLogModel.DestinationIP == dest_ip)
        
        statement = select(IPDRLogModel)
        if conditions:
            statement = statement.where(and_(*conditions))
        
        return session.exec(statement.limit(limit)).all()

    def update_log_suspicion_status(
        self,
        session: Session,
        log_id: int,
        is_suspicious: bool,
        suspicious_flags: Optional[List[str]] = None
    ) -> Optional[IPDRLogModel]:
        """Update the suspicion status and flags for a specific log entry."""
        log = self.read(session, log_id)
        if log:
            log.IsSuspicious = is_suspicious
            if suspicious_flags is not None:
                log.SuspiciousFlags = suspicious_flags
                # Mark the JSON field as modified to ensure the change is saved
                flag_modified(log, "SuspiciousFlags")
            session.add(log)
            session.commit()
            session.refresh(log)
        return log
    
    def get_logs_with_high_data_usage(
        self,
        session: Session,
        threshold_mb: int = 100
    ) -> List[IPDRLogModel]:
        """Get logs with combined data usage (upload + download) exceeding a threshold."""
        threshold_bytes = threshold_mb * 1024 * 1024
        statement = select(IPDRLogModel).where(
            (IPDRLogModel.BytesUpload + IPDRLogModel.BytesDownload) >= threshold_bytes
        )
        return session.exec(statement).all()

    # ... (baaki saare methods aapke waise hi rahenge kyonki woh sahi the)
    # get_logs_by_imei, get_logs_by_msisdn, etc.