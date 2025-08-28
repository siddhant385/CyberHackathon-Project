# Investigation Workflows - IPDR Analysis System

## 🔍 **Core Investigation Workflows**

### **Workflow 1: Basic User Investigation**
```
Start → User Lookup → Activity Analysis → Communication Partners → Report Generation → End
```

**Steps:**
1. **Input**: Aadhaar number or phone number
2. **User Validation**: Verify user exists in database
3. **Activity Summary**: Generate comprehensive activity statistics
4. **Partner Analysis**: Identify all communication partners (B-parties)
5. **Pattern Analysis**: Analyze temporal and behavioral patterns
6. **Report Generation**: Create professional investigation report

**Output**: 
- User profile summary
- Communication partner list
- Activity patterns
- Risk assessment
- Professional PDF/Text report

---

### **Workflow 2: Network Analysis Investigation**
```
Start → Central User → Connected Users → Network Mapping → Cluster Analysis → Report → End
```

**Steps:**
1. **Input**: Central user identifier
2. **Direct Connections**: Find users who shared communication partners
3. **Network Expansion**: Map connections up to specified depth (default: 2 levels)
4. **Cluster Analysis**: Analyze network characteristics
5. **Risk Propagation**: Assess risk across network
6. **Visualization**: Generate network diagrams

**Output**:
- Network topology map
- Connection strength analysis
- Cluster risk assessment
- Suspicious user identification

---

### **Workflow 3: Anomaly Detection Investigation**
```
Start → Data Collection → Pattern Baseline → Anomaly Detection → Risk Scoring → Alert Generation → End
```

**Steps:**
1. **Baseline Establishment**: Analyze normal behavior patterns
2. **Anomaly Detection**: Identify deviations from normal patterns
3. **Risk Scoring**: Calculate risk scores for anomalies
4. **Alert Classification**: Categorize alerts by severity
5. **Investigation Prioritization**: Rank cases by importance

**Anomaly Types Detected**:
- High data usage sessions (>100MB)
- Unusual timing patterns (late night activity)
- High connectivity (>50 unique destinations)
- Suspicious service usage patterns
- Geographic anomalies

---

### **Workflow 4: Temporal Analysis Investigation**
```
Start → Time Range Selection → Activity Extraction → Pattern Analysis → Timeline Generation → Report → End
```

**Steps:**
1. **Time Window**: Define investigation time period
2. **Activity Extraction**: Extract all activities in time window
3. **Pattern Recognition**: Identify temporal patterns
4. **Timeline Creation**: Build chronological activity timeline
5. **Correlation Analysis**: Find correlated activities

**Analysis Types**:
- Hourly activity patterns
- Daily/weekly patterns
- Seasonal variations
- Event correlation
- Peak activity identification

---

### **Workflow 5: Communication Flow Investigation**
```
Start → A-party Selection → B-party Mapping → Flow Analysis → Relationship Graph → Report → End
```

**Steps:**
1. **Source Identification**: Identify A-party (initiator)
2. **Destination Mapping**: Map all B-parties (recipients)
3. **Flow Analysis**: Analyze data flow patterns
4. **Relationship Strength**: Calculate connection strengths
5. **Graph Generation**: Create communication flow diagrams

**Metrics Calculated**:
- Session frequency
- Data volume (upload/download)
- Duration patterns
- Service types used
- Protocol analysis

---

## 🎯 **Investigation Decision Tree**

```
Investigation Request
        │
        ├── Single User Focus?
        │   ├── Yes → Basic User Investigation (Workflow 1)
        │   └── No → Continue
        │
        ├── Network Analysis Needed?
        │   ├── Yes → Network Analysis Investigation (Workflow 2)
        │   └── No → Continue
        │
        ├── Suspicious Activity Search?
        │   ├── Yes → Anomaly Detection Investigation (Workflow 3)
        │   └── No → Continue
        │
        ├── Time-based Investigation?
        │   ├── Yes → Temporal Analysis Investigation (Workflow 4)
        │   └── No → Continue
        │
        └── Communication Flow Analysis?
            ├── Yes → Communication Flow Investigation (Workflow 5)
            └── Custom Investigation Required
```

## 📊 **Standard Investigation Process**

### **Phase 1: Data Collection & Validation**
1. **Input Validation**: Verify all input parameters
2. **Data Availability**: Check data exists for investigation period
3. **Quality Assessment**: Assess data completeness and quality
4. **Baseline Establishment**: Create normal behavior baseline

### **Phase 2: Primary Analysis**
1. **User Profiling**: Build comprehensive user profiles
2. **Activity Mapping**: Map all communication activities
3. **Pattern Recognition**: Identify communication patterns
4. **Relationship Mapping**: Map user relationships

### **Phase 3: Advanced Analysis**
1. **Anomaly Detection**: Flag suspicious activities
2. **Risk Assessment**: Calculate risk scores
3. **Network Analysis**: Analyze network topology
4. **Temporal Analysis**: Study time-based patterns

### **Phase 4: Investigation & Reporting**
1. **Evidence Compilation**: Gather investigation evidence
2. **Timeline Construction**: Build chronological timeline
3. **Report Generation**: Create professional reports
4. **Recommendation Development**: Provide investigation recommendations

## 🚨 **Alert Generation Workflow**

```
Data Processing → Pattern Analysis → Threshold Checking → Alert Generation → Prioritization → Investigation
```

### **Alert Categories**
1. **High Priority (RED)**
   - Multiple anomalies detected
   - Very high risk score (>70)
   - Known suspicious user activity
   - Unusual communication patterns

2. **Medium Priority (YELLOW)**
   - Single anomaly detected
   - Medium risk score (40-70)
   - Unusual but explainable patterns
   - First-time occurrence

3. **Low Priority (GREEN)**
   - Minor deviations from normal
   - Low risk score (20-40)
   - Borderline suspicious activity
   - Monitoring recommended

## 🔧 **Investigation Tools & Commands**

### **Command Line Tools**

```bash
# Basic user investigation
python smart_investigation.py <aadhaar_number>

# Demo investigation with sample data
python demo_investigation.py

# Load fresh data
python main.py

# Generate test data (if needed)
cd Generator && python main.py
```

### **Investigation Parameters**

```python
# Risk assessment thresholds
HIGH_RISK_THRESHOLD = 70
MEDIUM_RISK_THRESHOLD = 40
LOW_RISK_THRESHOLD = 20

# Data usage thresholds
HIGH_DATA_THRESHOLD_MB = 100
SUSPICIOUS_DESTINATIONS_COUNT = 50

# Time-based thresholds
OFF_HOURS_START = 23  # 11 PM
OFF_HOURS_END = 6     # 6 AM
```

## 📈 **Performance Metrics**

### **Investigation Speed Benchmarks**
- Single user investigation: <5 seconds
- Network analysis (depth 2): <30 seconds
- Anomaly detection: <10 seconds
- Report generation: <3 seconds

### **Data Processing Capacity**
- Users: 10,000+ profiles
- IPDR Logs: 1,000,000+ records
- Real-time processing: 1,000 records/second
- Batch processing: 10,000 records/minute

## 🔒 **Investigation Security Protocols**

1. **Data Access Control**: Role-based access to investigation data
2. **Audit Logging**: All investigation activities logged
3. **Data Encryption**: Sensitive data encrypted at rest
4. **Secure Transfer**: All data transfers use encryption
5. **Privacy Compliance**: GDPR and local privacy law compliance

## 📝 **Investigation Report Standards**

### **Report Structure**
1. **Executive Summary**: Key findings and recommendations
2. **User Profile**: Comprehensive user information
3. **Activity Analysis**: Detailed activity breakdown
4. **Risk Assessment**: Risk score and factors
5. **Network Analysis**: Connection and relationship mapping
6. **Evidence**: Supporting data and logs
7. **Timeline**: Chronological sequence of events
8. **Recommendations**: Investigation recommendations

### **Report Formats**
- **Text Report**: Detailed text-based report
- **JSON Export**: Machine-readable data export
- **PDF Report**: Professional formatted report (future)
- **Excel Export**: Spreadsheet analysis (future)

## 🎯 **Best Practices for Investigators**

1. **Start with Basic Investigation**: Always begin with single user analysis
2. **Use Multiple Workflows**: Combine different investigation approaches
3. **Verify Findings**: Cross-reference results with multiple data sources
4. **Document Everything**: Maintain detailed investigation logs
5. **Follow Legal Guidelines**: Ensure all investigations comply with legal requirements
6. **Protect Privacy**: Only access data necessary for investigation
7. **Regular Updates**: Keep investigation status updated
8. **Collaborate**: Share findings with team members when appropriate
