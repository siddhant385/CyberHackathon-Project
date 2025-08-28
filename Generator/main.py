# main.py
import sys
from datetime import datetime
from user_generator import RealisticUserGenerator
from ipdr_generator import RealisticIPDRGenerator

def generate_realistic_investigation_data(hours: int = 24, users_count: int = 100, records_per_hour: int = 100, suspicious_ratio: float = 0.1):
    """
    Generates a realistic IPDR dataset for investigation.
    """
    print("🚀 Generating Realistic Investigation Dataset")
    print(f"   Time Window: {hours} hours")
    print(f"   Users: {users_count} ({int(users_count * suspicious_ratio)} suspicious)")
    print(f"   Records/Hour: {records_per_hour}")
    print(f"   Total Records: {hours * records_per_hour}")
    print("-" * 50)
    
    # Step 1: Generate Users
    print("\n👥 Generating user profiles...")
    user_generator = RealisticUserGenerator(
        userCount=users_count,
        suspiciousRatio=suspicious_ratio
    )
    
    # Step 2: Generate IPDR Records
    print("\n📊 Generating IPDR records...")
    ipdr_generator = RealisticIPDRGenerator(
        users=user_generator.users,
        time_window_hours=hours,
        records_per_hour=records_per_hour
    )
    
    # Step 3: Save Data
    print("\n💾 Saving generated data...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    user_file = f"realistic_users_{hours}h_{timestamp}.csv"
    ipdr_file = f"realistic_ipdr_{hours}h_{timestamp}.csv"
    summary_file = f"data_summary_{hours}h_{timestamp}.txt"
    
    user_generator.save_to_csv(user_file)
    ipdr_generator.save_to_csv(ipdr_file)
    
    # Step 4: Generate Summary
    print("\n📋 Generating data summary...")
    generate_data_summary(user_generator, ipdr_generator, hours, summary_file)
    
    print("\n🎉 Realistic Dataset Generated Successfully!")
    print("Files created:")
    print(f"   📁 {user_file} - User profiles")
    print(f"   📁 {ipdr_file} - IPDR records")
    print(f"   📁 {summary_file} - Data summary")
    
    print("\n✅ Ready for your AI investigation tool!")
    return user_generator, ipdr_generator

def generate_data_summary(user_gen, ipdr_gen, hours, filename):
    """Generates a summary of the generated data."""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("REALISTIC IPDR DATASET SUMMARY\n")
        f.write("=" * 50 + "\n\n")
        
        f.write("📊 DATASET STATISTICS\n")
        f.write(f"Time Window: {hours} hours\n")
        f.write(f"Total Records: {len(ipdr_gen.records):,}\n")
        f.write(f"Total Users: {len(user_gen.users)}\n\n")
        
        # User breakdown
        suspicious_users = len([u for u in user_gen.users if u.IsSuspicious])
        f.write(f"Normal Users: {len(user_gen.users) - suspicious_users}\n")
        f.write(f"Suspicious Users: {suspicious_users}\n\n")

        # Record breakdown
        suspicious_records = len([r for r in ipdr_gen.records if r.IsSuspicious])
        f.write(f"Normal Records: {len(ipdr_gen.records) - suspicious_records:,}\n")
        f.write(f"Suspicious Records: {suspicious_records:,}\n\n")
        
        # Service breakdown
        f.write("📱 SERVICE USAGE BREAKDOWN\n")
        f.write("-" * 30 + "\n")
        services = {}
        for record in ipdr_gen.records:
            services[record.Service] = services.get(record.Service, 0) + 1
        
        for service, count in sorted(services.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(ipdr_gen.records)) * 100
            f.write(f"{service}: {count:,} records ({percentage:.1f}%)\n")
        f.write("\n")

def interactive_data_generation():
    """Simple interactive interface for data generation."""
    print("\n🎯 Realistic IPDR Data Generator")
    print("=" * 45)
    print("Generate realistic data for your investigation AI!")
    print("\nQuick Presets:")
    print("1. Demo Dataset (1 hour, 50 users, 20% suspicious)")
    print("2. Development Dataset (24 hours, 100 users, 10% suspicious)")
    print("3. Large Dataset (168 hours, 500 users, 8% suspicious)")
    print("4. Custom Configuration")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == "1":
        generate_realistic_investigation_data(hours=1, users_count=50, records_per_hour=50, suspicious_ratio=0.2)
    elif choice == "2":
        generate_realistic_investigation_data(hours=24, users_count=100, records_per_hour=100, suspicious_ratio=0.1)
    elif choice == "3":
        generate_realistic_investigation_data(hours=168, users_count=500, records_per_hour=200, suspicious_ratio=0.08)
    elif choice == "4":
        try:
            hours = int(input("Time window (hours): "))
            users = int(input("Number of users: "))
            records_per_hour = int(input("Records per hour: "))
            suspicious_ratio = float(input("Suspicious ratio (0.1 = 10%): "))
            generate_realistic_investigation_data(hours, users, records_per_hour, suspicious_ratio)
        except ValueError:
            print("❌ Invalid input! Using development preset.")
            generate_realistic_investigation_data()
    else:
        print("❌ Invalid choice! Using development preset.")
        generate_realistic_investigation_data()

if __name__ == "__main__":
    interactive_data_generation()
    print("\n✅ Data Generation Complete!")
    print("🔧 Ready for your AI investigation tool development!")