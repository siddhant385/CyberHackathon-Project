# generators/user_generator.py
import csv
import random
import math
from faker import Faker
from typing import List, Dict

from models.user_model import UserModel
from utils.config import CITIES, STATES, ISPS, SUSPICIOUS_BEHAVIORS, CITY_COORDS, IP_RANGES

fake = Faker("en_IN")

class RealisticUserGenerator:
    def __init__(self, userCount: int = 50, suspiciousRatio: float = 0.1):
        self.userCount = userCount
        self.suspiciousCount = max(1, int(userCount * suspiciousRatio))
        self.users: List[UserModel] = []
        self._generate_users()

    def _generate_location(self, city: str) -> Dict[str, float]:
        base = CITY_COORDS.get(city, {"lat": 20.0, "lng": 77.0, "radius": 0.5})
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0, base["radius"])
        lat_offset = distance * math.cos(angle)
        lng_offset = distance * math.sin(angle)
        return {"lat": round(base["lat"] + lat_offset, 6), "lng": round(base["lng"] + lng_offset, 6)}

    def _generate_imei(self) -> str:
        tacs = [35328108, 35694410, 86585603, 35875507, 35849509, 35226711]
        tac = random.choice(tacs)
        serial = str(random.randint(100000, 999999))
        return f"{tac}{serial}{random.randint(0, 9)}"

    def _generate_ip_pool(self, city: str) -> List[str]:
        base_ranges = IP_RANGES.get(city, ["192.168.1"])
        ip_pool = []
        for _ in range(random.randint(2, 5)):
            base = random.choice(base_ranges)
            parts = base.split('.')
            if len(parts) == 2:
                ip = f"{base}.{random.randint(1, 254)}.{random.randint(1, 254)}"
            elif len(parts) == 3:
                ip = f"{base}.{random.randint(1, 254)}"
            else:
                ip = fake.ipv4_private()
            ip_pool.append(ip)
        return ip_pool

    def _generate_normal_user(self) -> UserModel:
        city = random.choice(CITIES)
        state = STATES[CITIES.index(city)]
        aadhaar = ''.join([str(random.randint(0, 9)) for _ in range(12)])
        name = fake.name()
        email_name = name.lower().replace(' ', '.')
        email = f"{email_name}{random.randint(1, 999)}@{random.choice(['gmail.com', 'yahoo.in'])}"
        phone = f"{random.choice(['9', '8', '7', '6'])}{''.join([str(random.randint(0, 9)) for _ in range(9)])}"
        
        return UserModel(
            AadhaarNo=aadhaar, Name=name, Age=random.randint(18, 75),
            Address=f"{fake.building_number()}, {fake.street_name()}, {city}, {state} - {fake.postcode()}",
            Email=email, PhoneNo=phone, City=city, State=state,
            Devices=[self._generate_imei() for _ in range(random.choices([1, 2, 3], weights=[70, 25, 5])[0])],
            AssignedIPs=self._generate_ip_pool(city), ISP=random.choice(ISPS),
            IsSuspicious=False, HomeLocation=self._generate_location(city),
            UsualActiveHours=list(range(6, 23))
        )

    def _generate_suspicious_user(self) -> UserModel:
        user = self._generate_normal_user()
        user.IsSuspicious = True
        user.SuspiciousType = random.sample(SUSPICIOUS_BEHAVIORS, random.randint(1, 3))

        if "location_hopping" in user.SuspiciousType:
            cities = ["Mumbai", "Delhi", "Bangalore"]
            for city in random.sample(cities, 2):
                user.AssignedIPs.extend(self._generate_ip_pool(city))
        if "unusual_timing" in user.SuspiciousType:
            user.UsualActiveHours = list(range(0, 6)) + list(range(22, 24))
        if "device_cloning" in user.SuspiciousType:
            user.Devices.extend([self._generate_imei() for _ in range(2, 5)])
            
        return user

    def _generate_users(self):
        print(f"Generating {self.userCount} users ({self.suspiciousCount} suspicious)...")
        self.users.extend(self._generate_suspicious_user() for _ in range(self.suspiciousCount))
        self.users.extend(self._generate_normal_user() for _ in range(self.userCount - self.suspiciousCount))
        random.shuffle(self.users)
        print(f"✅ Generated {len(self.users)} users")

    def save_to_csv(self, filename: str = "users.csv"):
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            fieldnames = UserModel.__fields__.keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for user in self.users:
                row = user.dict()
                row['Devices'] = '|'.join(row['Devices'])
                row['AssignedIPs'] = '|'.join(row['AssignedIPs'])
                row['SuspiciousType'] = '|'.join(row['SuspiciousType'])
                row['HomeLocation'] = f"{row['HomeLocation'].get('lat')},{row['HomeLocation'].get('lng')}"
                row['UsualActiveHours'] = '|'.join(map(str, row['UsualActiveHours']))
                writer.writerow(row)
        print(f"✅ Users saved to {filename}")
        