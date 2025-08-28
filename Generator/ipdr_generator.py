# generators/ipdr_generator.py
import csv
import random
import uuid
import math
from datetime import datetime, timedelta
from typing import List, Tuple
from faker import Faker

from models.user_model import UserModel
from models.ipdr_model import IPDRModel
from app.core.config import settings

fake = Faker("en_IN")

class RealisticIPDRGenerator:
    def __init__(self, users: List[UserModel], time_window_hours: int = 24, records_per_hour: int = 100):
        self.users = users
        self.time_window_hours = time_window_hours
        self.records_per_hour = records_per_hour
        self.total_records = time_window_hours * records_per_hour
        self.records: List[IPDRModel] = []
        self._generate_time_based_records()

    def _get_realistic_b_party(self, a_user: UserModel, service: str, timestamp: datetime) -> Tuple[str, int]:
        if service in ["WhatsApp", "Telegram"] and random.random() < 0.3 and len(self.users) > 1:
            active_contacts = [u for u in self.users if u.AadhaarNo != a_user.AadhaarNo and timestamp.hour in u.UsualActiveHours]
            if active_contacts:
                b_user = random.choice(active_contacts)
                return random.choice(b_user.AssignedIPs), 443
        
        servers = settings.GENERATOR_SERVICE_SERVERS.get(service, [fake.ipv4_public()])
        port = random.choice(settings.GENERATOR_SERVICES.get(service, {}).get("ports", [443]))
        return random.choice(servers), port
    
    def _generate_current_location(self, user: UserModel):
        home = user.HomeLocation
        max_distance = 0.05
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0, max_distance)
        lat_offset = distance * math.cos(angle)
        lng_offset = distance * math.sin(angle)
        return {"lat": round(home["lat"] + lat_offset, 6), "lng": round(home["lng"] + lng_offset, 6)}

    def _generate_record(self, user: UserModel, timestamp: datetime) -> IPDRModel:
        service_details = settings.GENERATOR_SERVICES.get(self._select_realistic_service(user, timestamp), settings.GENERATOR_SERVICES["Unknown"])
        service_name = service_details["name"]
        
        duration = random.choices([random.randint(30, 300), random.randint(300, 1800)], weights=[70, 30])[0]
        dest_ip, dest_port = self._get_realistic_b_party(user, service_name, timestamp)

        base_up, base_down = service_details["data_usage"]
        upload = random.randint(int(base_up * 0.1), base_up)
        download = random.randint(int(base_down * 0.1), base_down)
        
        record = IPDRModel(
            RecordID=str(uuid.uuid4()), AadhaarNo=user.AadhaarNo, IMEI=random.choice(user.Devices),
            MSISDN=user.PhoneNo, StartTime=timestamp, EndTime=timestamp + timedelta(seconds=duration),
            Duration=duration, SourceIP=random.choice(user.AssignedIPs),
            SourcePort=random.randint(1024, 65535), DestinationIP=dest_ip, DestinationPort=dest_port,
            Protocol=service_details["protocol"], BytesUpload=upload, BytesDownload=download,
            Service=service_name, AppName=service_name, ISP=user.ISP,
            CellTowerID=f"CT{user.City[:3].upper()}{random.randint(1000, 9999)}", LAC=f"LAC{random.randint(1000, 9999)}",
            SessionType="Data", DataType=service_details["data_type"], Location=self._generate_current_location(user)
        )
        
        if user.IsSuspicious and "large_transfers" in user.SuspiciousType:
            record.IsSuspicious = True
            record.BytesUpload = random.randint(100_000_000, 1_000_000_000)
            record.SuspiciousFlags.append("Large data transfer")
        if user.IsSuspicious and "suspicious_destinations" in user.SuspiciousType:
            record.IsSuspicious = True
            record.DestinationIP = random.choice(settings.GENERATOR_SUSPICIOUS_IPS)
            record.SuspiciousFlags.append("Suspicious destination")

        return record

    def _select_realistic_service(self, user: UserModel, timestamp: datetime) -> str:
        hour = timestamp.hour
        if hour >= 22 or hour <= 6:
            return random.choice(["WhatsApp", "Instagram", "YouTube"])
        return random.choice(["WhatsApp", "Facebook", "YouTube", "Gmail", "Banking"])

    def _generate_time_based_records(self):
        print(f"Generating {self.total_records} IPDR records for a {self.time_window_hours}h window...")
        start_time = datetime.now() - timedelta(hours=self.time_window_hours)
        
        for hour in range(self.time_window_hours):
            hour_start = start_time + timedelta(hours=hour)
            for _ in range(self.records_per_hour):
                record_time = hour_start + timedelta(minutes=random.randint(0, 59), seconds=random.randint(0, 59))
                active_users = [u for u in self.users if record_time.hour in u.UsualActiveHours] or self.users
                user = random.choice(active_users)
                self.records.append(self._generate_record(user, record_time))

        self.records.sort(key=lambda r: r.StartTime)
        suspicious_count = sum(1 for r in self.records if r.IsSuspicious)
        print(f"✅ Generated {len(self.records)} records ({suspicious_count} suspicious)")

    def save_to_csv(self, filename: str = "ipdr_records.csv"):
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            fieldnames = IPDRModel.__fields__.keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for record in self.records:
                row = record.dict()
                row['StartTime'] = record.StartTime.isoformat()
                row['EndTime'] = record.EndTime.isoformat()
                row['Location'] = f"{row['Location'].get('lat', 0)},{row['Location'].get('lng', 0)}"
                row['SuspiciousFlags'] = '|'.join(record.SuspiciousFlags)
                writer.writerow(row)
        print(f"✅ IPDR records saved to {filename}")