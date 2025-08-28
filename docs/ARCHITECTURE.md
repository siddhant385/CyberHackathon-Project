# System Architecture - IPDR Analysis System

## 🏗️ **High-Level Architecture**

```
┌─────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                       │
├─────────────────────────────────────────────────────────────────┤
│  CLI Tools  │  Demo Scripts  │  Investigation Tools  │  Reports │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                      BUSINESS LOGIC LAYER                       │
├─────────────────────────────────────────────────────────────────┤
│ Investigation │  User Service  │  IPDR Service  │  Risk Engine  │
│   Service     │               │               │               │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                        DATA ACCESS LAYER                        │
├─────────────────────────────────────────────────────────────────┤
│   User CRUD   │  IPDR CRUD   │  Base CRUD   │  Query Builder   │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                         DATA MODEL LAYER                        │
├─────────────────────────────────────────────────────────────────┤
│  User Model   │ IPDR Model   │  Validators  │  Relationships   │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE LAYER                         │
├─────────────────────────────────────────────────────────────────┤
│  Database     │   Logging    │    Config    │   File I/O      │
│  Engine       │   System     │   Manager    │   Handlers      │
└─────────────────────────────────────────────────────────────────┘
```

## 🧩 **Component Architecture**

### **1. Infrastructure Layer** (`app/core/`)

#### **Database Engine** (`database.py`)
```python
"""
Centralized database management with:
- Connection pooling and lifecycle management
- Transaction handling and rollback support
- Health checks and monitoring
- SQLModel integration
"""
```

**Key Components**:
- **Engine Creation**: Optimized SQLAlchemy engine configuration
- **Session Management**: Context-managed database sessions
- **Connection Pooling**: Efficient connection reuse
- **Health Monitoring**: Database connectivity checks

#### **Configuration Manager** (`config.py`)
```python
"""
Environment-based configuration with:
- Type-safe settings using Pydantic
- Environment variable support
- Validation and defaults
- Security settings
"""
```

**Configuration Categories**:
- Database settings
- Logging configuration
- Application parameters
- Security settings
- Processing thresholds

#### **Logging System** (`logger.py`)
```python
"""
Structured logging infrastructure with:
- Multiple output destinations (console, file)
- Log level management
- Colored console output
- Performance tracking
- Error context preservation
"""
```

**Logging Features**:
- Hierarchical loggers
- Contextual information
- Performance metrics
- Error tracking
- Audit trails

---

### **2. Data Model Layer** (`app/models/`)

#### **User Model** (`user_model.py`)
```python
"""
Comprehensive user data model with:
- Identity validation (Aadhaar, phone)
- Profile information management
- Suspicious activity tracking
- Device and IP associations
- Geographic and temporal data
"""
```

**Data Structure**:
```
UserModel
├── Identity: AadhaarNo (PK), Name, Age
├── Contact: Email, PhoneNo, Address, City, State
├── Technical: Devices[], AssignedIPs[], ISP
├── Security: IsSuspicious, SuspiciousType[]
├── Location: HomeLocation{}, UsualActiveHours[]
└── Metadata: Created, Updated timestamps
```

#### **IPDR Log Model** (`ipdr_log_model.py`)
```python
"""
Detailed communication record model with:
- Session information (timing, duration)
- Network details (IPs, ports, protocols)
- Data transfer metrics
- Service identification
- Location and quality metrics
"""
```

**Data Structure**:
```
IPDRLogModel
├── Session: id (PK), StartTime, EndTime, Duration
├── Identity: AadhaarNo (FK), IMEI, MSISDN
├── Network: SourceIP, SourcePort, DestinationIP, DestinationPort
├── Protocol: Protocol, Service, AppName
├── Data: BytesUpload, BytesDownload, DataType
├── Location: CellTowerID, LAC, Location{}
├── Quality: ConnectionQuality, SessionType
└── Security: IsSuspicious, SuspiciousFlags[]
```

---

### **3. Data Access Layer** (`app/crud/`)

#### **Base CRUD** (`base.py`)
```python
"""
Generic CRUD operations with:
- Type-safe operations using generics
- Standardized error handling
- Pagination support
- Query optimization
- Transaction management
"""
```

**CRUD Operations**:
- **Create**: Insert new records with validation
- **Read**: Single and multi-record retrieval
- **Update**: Partial and full record updates
- **Delete**: Safe record deletion
- **Count**: Efficient record counting

#### **Specialized CRUD Classes**
- **UserCRUD**: User-specific operations with Aadhaar-based lookups
- **IPDRLogCRUD**: IPDR-specific operations with time-based queries

---

### **4. Business Logic Layer** (`app/services/`)

#### **Base Service** (`base_service.py`)
```python
"""
Abstract service foundation providing:
- Common service patterns
- Session management
- Error handling templates
- Logging integration
- Transaction coordination
"""
```

#### **User Service** (`user_service.py`)
```python
"""
User management and analysis with:
- User lifecycle management
- Suspicious activity tracking
- Phone and location-based searches
- Risk assessment
- Profile enrichment
"""
```

**Core Capabilities**:
- User creation and validation
- Suspicious user identification
- Phone number association
- Geographic analysis
- Activity pattern recognition

#### **IPDR Service** (`ipdr_service.py`)
```python
"""
IPDR log analysis and processing with:
- Communication partner identification
- Traffic pattern analysis
- Time-based filtering
- Data usage analytics
- Anomaly detection
"""
```

**Analysis Functions**:
- B-party identification
- Traffic volume analysis
- Temporal pattern recognition
- Service usage analytics
- Quality assessment

#### **Investigation Service** (`investigation_service.py`)
```python
"""
High-level investigation workflows with:
- Multi-data source correlation
- Network topology analysis
- Risk assessment algorithms
- Report generation
- Evidence compilation
"""
```

**Investigation Types**:
- Individual user analysis
- Network cluster analysis
- Temporal correlation analysis
- Risk propagation analysis
- Evidence trail construction

---

## 🔄 **Data Flow Architecture**

### **Data Ingestion Flow**
```
CSV Files → Parsers → Validation → CRUD Layer → Database
     │         │          │           │            │
     │         │          │           │            └─→ Logs
     │         │          │           └─→ Error Handling
     │         │          └─→ Business Rules
     │         └─→ Format Conversion
     └─→ File Validation
```

### **Investigation Flow**
```
User Request → Service Layer → CRUD Operations → Database Query
     │              │               │                   │
     │              │               │                   └─→ Results
     │              │               └─→ Data Aggregation
     │              └─→ Business Logic
     └─→ Input Validation
```

### **Report Generation Flow**
```
Investigation Results → Analysis Engine → Report Templates → Output Files
            │                │                │              │
            │                │                │              └─→ File System
            │                │                └─→ Formatting
            │                └─→ Data Processing
            └─→ Data Validation
```

---

## 🔐 **Security Architecture**

### **Data Security Layers**
1. **Input Validation**: All inputs validated before processing
2. **SQL Injection Protection**: SQLModel ORM prevents injection attacks
3. **Access Control**: Role-based access to sensitive data
4. **Audit Logging**: Complete audit trail of all operations
5. **Data Encryption**: Sensitive data encrypted at rest (future)

### **Error Handling Strategy**
```
Error Occurrence → Logging → Classification → Recovery Action → User Notification
        │            │           │              │               │
        │            │           │              │               └─→ User-friendly message
        │            │           │              └─→ Rollback/Retry
        │            │           └─→ Severity Assessment
        │            └─→ Context Preservation
        └─→ Stack Trace Capture
```

---

## 📊 **Performance Architecture**

### **Database Optimization**
- **Connection Pooling**: Reuse database connections
- **Query Optimization**: Efficient query patterns
- **Indexing Strategy**: Strategic index placement
- **Batch Processing**: Bulk operations for large datasets

### **Memory Management**
- **Streaming**: Large file processing without full load
- **Pagination**: Limited result sets for UI responsiveness
- **Caching**: Strategic data caching (future enhancement)
- **Resource Cleanup**: Proper resource disposal

### **Scalability Considerations**
- **Horizontal Scaling**: Database sharding support (future)
- **Vertical Scaling**: Optimized for single-machine performance
- **Asynchronous Processing**: Background task processing (future)
- **Load Distribution**: Service layer separation enables load balancing

---

## 🔧 **Deployment Architecture**

### **Development Environment**
```
Developer Machine
├── SQLite Database (local)
├── File-based Logging
├── Debug Configuration
└── Test Data Generation
```

### **Production Environment** (Future)
```
Application Server
├── PostgreSQL Database (clustered)
├── Centralized Logging (ELK Stack)
├── Production Configuration
├── Monitoring and Alerting
└── Backup and Recovery
```

---

## 🧪 **Testing Architecture**

### **Test Layers**
1. **Unit Tests**: Individual component testing
2. **Integration Tests**: Service layer testing
3. **End-to-End Tests**: Complete workflow testing
4. **Performance Tests**: Load and stress testing

### **Test Data Management**
- **Synthetic Data**: Generated test datasets
- **Anonymized Data**: Real data with PII removed
- **Edge Cases**: Boundary condition testing
- **Error Scenarios**: Failure condition testing

---

## 📈 **Monitoring and Observability**

### **Logging Strategy**
- **Structured Logging**: Consistent log format
- **Log Levels**: Appropriate severity classification
- **Context Preservation**: Request tracing through system
- **Performance Metrics**: Operation timing and resource usage

### **Health Monitoring**
- **Database Health**: Connection and query performance
- **Application Health**: Service availability and responsiveness
- **Resource Monitoring**: Memory and CPU usage tracking
- **Error Rate Tracking**: Exception frequency and types

---

## 🔮 **Future Architecture Enhancements**

### **Planned Improvements**
1. **Web Dashboard**: React-based investigation interface
2. **REST API**: External system integration
3. **Real-time Processing**: Stream processing capabilities
4. **Machine Learning**: Automated pattern detection
5. **Distributed Architecture**: Microservices deployment
6. **Advanced Caching**: Redis-based caching layer
7. **Message Queuing**: Asynchronous processing with RabbitMQ
8. **Container Deployment**: Docker and Kubernetes support
