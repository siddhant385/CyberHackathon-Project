# utils/config.py

# User Profile Data
CITIES = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad", "Pune", "Kolkata", "Ahmedabad"]
STATES = ["Maharashtra", "Delhi", "Karnataka", "Tamil Nadu", "Telangana", "Maharashtra", "West Bengal", "Gujarat"]
ISPS = ["Jio", "Airtel", "Vi", "BSNL"]

# Geographical Data
CITY_COORDS = {
    "Mumbai": {"lat": 19.0760, "lng": 72.8777, "radius": 0.5},
    "Delhi": {"lat": 28.7041, "lng": 77.1025, "radius": 0.6},
    "Bangalore": {"lat": 12.9716, "lng": 77.5946, "radius": 0.4},
    "Chennai": {"lat": 13.0827, "lng": 80.2707, "radius": 0.4},
}
IP_RANGES = {
    "Mumbai": ["103.21", "117.18", "125.99"],
    "Delhi": ["117.97", "106.51", "203.122"],
    "Bangalore": ["117.196", "49.207", "103.248"],
    "Chennai": ["117.192", "203.192", "49.205"],
}

# Suspicious Patterns Data
SUSPICIOUS_BEHAVIORS = [
    "location_hopping", "ip_hopping", "unusual_timing", "large_transfers",
    "micro_sessions", "long_sessions", "suspicious_destinations",
    "device_cloning", "data_exfiltration"
]
SUSPICIOUS_IPS = [
    "185.220.101.15", "198.98.51.189", "45.77.230.37",
    "194.61.24.102", "103.224.182.251", "45.32.105.15"
]
SUSPICIOUS_LOCATIONS = [
    {"lat": 28.7041, "lng": 77.1025, "name": "Border Area"},
    {"lat": 15.2993, "lng": 74.1240, "name": "Remote Area"},
]

# Service and B-Party Data
SERVICES = {
    "WhatsApp": {"name": "WhatsApp", "ports": [443, 5222], "protocol": "HTTPS", "data_type": "IM", "data_usage": (50_000, 500_000)},
    "Facebook": {"name": "Facebook", "ports": [443, 80], "protocol": "HTTPS", "data_type": "Social", "data_usage": (200_000, 2_000_000)},
    "Instagram": {"name": "Instagram", "ports": [443], "protocol": "HTTPS", "data_type": "Social", "data_usage": (500_000, 5_000_000)},
    "YouTube": {"name": "YouTube", "ports": [443, 80], "protocol": "HTTPS", "data_type": "Video", "data_usage": (1_000_000, 50_000_000)},
    "Netflix": {"name": "Netflix", "ports": [443], "protocol": "HTTPS", "data_type": "Video", "data_usage": (5_000_000, 100_000_000)},
    "Telegram": {"name": "Telegram", "ports": [443, 80], "protocol": "HTTPS", "data_type": "IM", "data_usage": (50_000, 500_000)},
    "Gmail": {"name": "Gmail", "ports": [993, 587], "protocol": "IMAP", "data_type": "Email", "data_usage": (5_000, 50_000)},
    "Banking": {"name": "Banking", "ports": [443], "protocol": "HTTPS", "data_type": "Finance", "data_usage": (10_000, 100_000)},
    "Gaming": {"name": "Gaming", "ports": [443, 7777], "protocol": "TCP", "data_type": "Gaming", "data_usage": (100_000, 10_000_000)},
    "Unknown": {"name": "Unknown", "ports": [80, 8080], "protocol": "TCP", "data_type": "Unknown", "data_usage": (10_000, 100_000)}
}
SERVICE_SERVERS = {
    "WhatsApp": ["157.240.12.35", "91.108.4.41"],
    "Telegram": ["91.108.56.181", "149.154.175.50"],
    "YouTube": ["142.250.183.14", "172.217.160.78"],
    "Facebook": ["157.240.12.35", "31.13.64.35"],
    "Netflix": ["54.230.216.47", "52.85.83.228"],
    "Gmail": ["172.217.160.109", "142.250.183.109"]
}