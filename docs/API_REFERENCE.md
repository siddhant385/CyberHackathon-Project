# API Reference - IPDR Analysis System

## 📚 **Core Services API**

### **UserService**
*Business logic for user management and analysis*

#### **Methods**

##### `create_record(session: Session, data: Dict[str, Any]) -> UserModel`
**Purpose**: Create a new user with business validation
**Parameters**:
- `session`: Database session
- `data`: User data dictionary containing all required fields

**Returns**: Created UserModel instance
**Raises**: `ValueError` if user already exists or validation fails

**Example**:
```python
user_service = UserService()
user_data = {
    'AadhaarNo': '123456789012',
    'Name': 'John Doe',
    'Age': 30,
    'Phone': '9876543210',
    'City': 'Mumbai'
}
with Session(engine) as session:
    user = user_service.create_record(session, user_data)
```

---

##### `get_record(session: Session, aadhaar_no: str) -> Optional[UserModel]`
**Purpose**: Retrieve user by Aadhaar number
**Parameters**:
- `session`: Database session
- `aadhaar_no`: 12-digit Aadhaar number

**Returns**: UserModel instance or None if not found

---

##### `find_users_by_phone(session: Session, phone_no: str) -> List[UserModel]`
**Purpose**: Find all users with specified phone number
**Parameters**:
- `session`: Database session
- `phone_no`: 10-digit phone number

**Returns**: List of UserModel instances

---

##### `find_suspicious_users(session: Session) -> List[UserModel]`
**Purpose**: Find all users marked as suspicious
**Parameters**:
- `session`: Database session

**Returns**: List of suspicious UserModel instances

---

##### `mark_user_suspicious(session: Session, aadhaar_no: str, suspicious_type: str) -> Optional[UserModel]`
**Purpose**: Mark user as suspicious with specific reason
**Parameters**:
- `session`: Database session
- `aadhaar_no`: User's Aadhaar number
- `suspicious_type`: Reason for marking suspicious

**Returns**: Updated UserModel instance or None if user not found

---

### **IPDRService**
*Business logic for IPDR log analysis*

#### **Methods**

##### `create_record(session: Session, data: Dict[str, Any]) -> IPDRLogModel`
**Purpose**: Create new IPDR log with validation
**Parameters**:
- `session`: Database session
- `data`: IPDR log data dictionary

**Returns**: Created IPDRLogModel instance
**Raises**: `ValueError` if IP validation fails

---

##### `find_logs_by_user(session: Session, aadhaar_no: str) -> List[IPDRLogModel]`
**Purpose**: Find all logs for specific user
**Parameters**:
- `session`: Database session
- `aadhaar_no`: User's Aadhaar number

**Returns**: List of IPDRLogModel instances

---

##### `find_communication_partners(session: Session, aadhaar_no: str) -> List[Dict[str, Any]]`
**Purpose**: Find all B-party (recipients) for user communications
**Parameters**:
- `session`: Database session
- `aadhaar_no`: User's Aadhaar number

**Returns**: List of communication partner dictionaries with:
- `destination_ip`: Partner's IP address
- `total_sessions`: Number of communication sessions
- `total_upload/download`: Data transfer amounts
- `services_used`: List of services used
- `first_contact/last_contact`: Timeline of communication

---

##### `find_logs_by_time_range(session: Session, start_time: datetime, end_time: datetime) -> List[IPDRLogModel]`
**Purpose**: Find logs within specific time period
**Parameters**:
- `session`: Database session
- `start_time`: Start of time window
- `end_time`: End of time window

**Returns**: List of IPDRLogModel instances

---

##### `analyze_high_traffic_sessions(session: Session, threshold_mb: int = 100) -> List[IPDRLogModel]`
**Purpose**: Find sessions with high data usage
**Parameters**:
- `session`: Database session
- `threshold_mb`: Data usage threshold in megabytes

**Returns**: List of high-traffic IPDRLogModel instances

---

##### `get_user_activity_summary(session: Session, aadhaar_no: str) -> Dict[str, Any]`
**Purpose**: Generate comprehensive activity summary for user
**Parameters**:
- `session`: Database session
- `aadhaar_no`: User's Aadhaar number

**Returns**: Dictionary containing:
- `total_sessions`: Number of communication sessions
- `total_upload_mb/total_download_mb`: Data usage in MB
- `total_duration_hours`: Total communication time
- `unique_services`: List of services used
- `protocols_used`: List of protocols used
- `unique_destinations`: Number of unique communication partners
- `first_activity/last_activity`: Activity timeline
- `suspicious_sessions`: Count of suspicious sessions

---

### **InvestigationService**
*High-level investigation workflows*

#### **Methods**

##### `investigate_user_relationships(session: Session, aadhaar_no: str) -> Dict[str, Any]`
**Purpose**: Perform comprehensive user investigation
**Parameters**:
- `session`: Database session
- `aadhaar_no`: User's Aadhaar number

**Returns**: Complete investigation report dictionary containing:
- `user_details`: User profile information
- `communication_partners`: List of B-parties
- `activity_summary`: Activity statistics
- `patterns`: Communication patterns analysis
- `anomalies`: Detected anomalies
- `investigation_timestamp`: When investigation was performed

---

##### `find_connected_users(session: Session, aadhaar_no: str) -> List[Dict[str, Any]]`
**Purpose**: Find users who shared communication partners
**Parameters**:
- `session`: Database session
- `aadhaar_no`: Central user's Aadhaar number

**Returns**: List of connected user dictionaries with:
- `aadhaar_no`: Connected user's Aadhaar
- `name`: Connected user's name
- `phone`: Connected user's phone
- `common_destination`: Shared communication partner IP
- `connection_count`: Strength of connection

---

##### `analyze_network_cluster(session: Session, center_aadhaar: str, depth: int = 2) -> Dict[str, Any]`
**Purpose**: Analyze network cluster around central user
**Parameters**:
- `session`: Database session
- `center_aadhaar`: Central user's Aadhaar number
- `depth`: Network analysis depth (default: 2 levels)

**Returns**: Network analysis dictionary with:
- `nodes`: List of users in network
- `edges`: List of connections between users
- `cluster_analysis`: Network characteristics

---

##### `generate_investigation_report(session: Session, aadhaar_no: str) -> str`
**Purpose**: Generate formatted text investigation report
**Parameters**:
- `session`: Database session
- `aadhaar_no`: User's Aadhaar number

**Returns**: Formatted text report string

---

## 📊 **Data Models API**

### **UserModel**
*SQLModel for user data*

#### **Fields**
- `AadhaarNo: str` - Primary key, 12-digit Aadhaar number
- `Name: str` - User's full name
- `Age: int` - User's age
- `Address: str` - User's address
- `Email: str` - User's email address
- `PhoneNo: str` - 10-digit phone number
- `City: str` - User's city
- `State: str` - User's state
- `Devices: List[str]` - List of device identifiers
- `AssignedIPs: List[str]` - List of assigned IP addresses
- `ISP: str` - Internet Service Provider
- `IsSuspicious: bool` - Suspicious status flag
- `SuspiciousType: List[str]` - Reasons for being suspicious
- `HomeLocation: Dict[str, float]` - Geographic coordinates
- `UsualActiveHours: List[int]` - Typical activity hours

#### **Validators**
- `validate_aadhaar()`: Ensures 12-digit Aadhaar format
- `validate_phone()`: Validates Indian phone number format

---

### **IPDRLogModel**
*SQLModel for IPDR log records*

#### **Fields**
- `id: Optional[int]` - Primary key, auto-generated
- `AadhaarNo: str` - Foreign key to UserModel
- `IMEI: str` - Device IMEI number
- `MSISDN: str` - Mobile number
- `StartTime: datetime` - Session start time
- `EndTime: datetime` - Session end time
- `Duration: int` - Session duration in seconds
- `SourceIP: str` - Source IP address
- `SourcePort: int` - Source port number
- `DestinationIP: str` - Destination IP address (B-party)
- `DestinationPort: int` - Destination port number
- `Protocol: str` - Communication protocol
- `BytesUpload: int` - Uploaded data in bytes
- `BytesDownload: int` - Downloaded data in bytes
- `Service: str` - Service type (Gmail, WhatsApp, etc.)
- `AppName: Optional[str]` - Application name
- `ISP: str` - Internet Service Provider
- `CellTowerID: str` - Cell tower identifier
- `LAC: str` - Location Area Code
- `SessionType: str` - Type of session
- `DataType: str` - Type of data transferred
- `Location: Dict[str, float]` - Geographic coordinates
- `IsSuspicious: bool` - Suspicious activity flag
- `SuspiciousFlags: List[str]` - Suspicious activity indicators
- `ConnectionQuality: str` - Connection quality indicator

#### **Validators**
- `validate_ip()`: Validates IP address format

---

## 🔧 **CRUD Operations API**

### **BaseCRUD**
*Generic CRUD operations base class*

#### **Methods**
- `create(session, obj_in)` - Create new record
- `read(session, id)` - Read record by ID
- `read_multi(session, skip, limit)` - Read multiple records with pagination
- `update(session, db_obj, obj_in)` - Update existing record
- `delete(session, id)` - Delete record by ID
- `count(session)` - Count total records

### **UserCRUD**
*User-specific CRUD operations*
- Inherits from BaseCRUD
- Overrides `read()` to use AadhaarNo as primary key
- Adds user-specific query methods

### **IPDRLogCRUD**
*IPDR log-specific CRUD operations*
- Inherits from BaseCRUD
- Adds IPDR-specific query methods
- Optimized for large dataset operations

---

## 🚀 **Usage Examples**

### **Basic User Investigation**
```python
from sqlmodel import Session
from app.core.database import engine
from app.services.investigation_service import InvestigationService

# Create investigation service
investigation_service = InvestigationService()

# Perform investigation
with Session(engine) as session:
    report = investigation_service.investigate_user_relationships(
        session, 
        "922027456759"
    )
    print(f"Found {len(report['communication_partners'])} communication partners")
```

### **Network Analysis**
```python
# Analyze network cluster
network = investigation_service.analyze_network_cluster(
    session, 
    "922027456759", 
    depth=2
)
print(f"Network has {len(network['nodes'])} users and {len(network['edges'])} connections")
```

### **High Traffic Analysis**
```python
from app.services.ipdr_service import IPDRService

ipdr_service = IPDRService()

# Find high traffic sessions (>100MB)
with Session(engine) as session:
    high_traffic = ipdr_service.analyze_high_traffic_sessions(
        session, 
        threshold_mb=100
    )
    print(f"Found {len(high_traffic)} high traffic sessions")
```

### **Suspicious User Detection**
```python
from app.services.user_service import UserService

user_service = UserService()

# Find suspicious users
with Session(engine) as session:
    suspicious = user_service.find_suspicious_users(session)
    for user in suspicious:
        print(f"Suspicious user: {user.Name} - {user.SuspiciousType}")
```

---

## ⚠️ **Error Handling**

### **Common Exceptions**
- `ValueError`: Invalid input data or validation failures
- `sqlalchemy.exc.IntegrityError`: Database constraint violations
- `sqlalchemy.exc.PendingRollbackError`: Transaction rollback required
- `FileNotFoundError`: Missing input files
- `ConnectionError`: Database connection issues

### **Error Handling Pattern**
```python
try:
    # Perform operation
    result = service.some_operation(session, data)
    logger.info(f"Operation completed successfully")
    return result
except ValueError as e:
    logger.error(f"Validation error: {str(e)}")
    return {'error': 'Invalid input data'}
except Exception as e:
    logger.error(f"Unexpected error: {str(e)}")
    session.rollback()
    return {'error': 'Operation failed'}
```

---

## 📈 **Performance Guidelines**

### **Best Practices**
1. **Use Pagination**: For large datasets, always use `skip` and `limit`
2. **Batch Operations**: Process large datasets in batches
3. **Connection Management**: Use context managers for database sessions
4. **Index Usage**: Ensure queries use appropriate database indexes
5. **Memory Management**: Stream large files instead of loading entirely

### **Performance Metrics**
- Single user query: <100ms
- Communication partner analysis: <1s
- Network analysis (depth 2): <30s
- Report generation: <3s
