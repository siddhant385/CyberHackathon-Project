#!/usr/bin/env python3
"""
IPDR Analysis System - Main Entry Point

This is the main entry point for the IPDR (Internet Protocol Detail Record) Analysis System.
It provides a command-line interface for investigators to perform various analysis operations
on telecommunications data.

The system is designed for law enforcement and telecommunications investigators to:
- Analyze communication patterns
- Identify suspicious activities  
- Generate investigation reports
- Map user relationships and networks

Usage Examples:
    # Load sample data
    python main.py load-data
    
    # Run investigation demo
    python main.py demo
    
    # Investigate specific user
    python main.py investigate 922027456759
    
    # Show system status
    python main.py status
    
    # Get help
    python main.py --help

Author: IPDR Analysis Team
Version: 1.0.0
License: Proprietary - For Investigation Use Only
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

# Add the app directory to the Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from app.core.logger import get_logger
from app.core.database import init_db, check_db_connection
from app.core.config import settings, validate_configuration

# Import handlers
from app.handlers.load_data_handler import LoadDataHandler
from app.handlers.suspicious_analysis_handler import SuspiciousAnalysisHandler
from app.handlers.demo_handler import DemoHandler
from app.handlers.investigation_handler import InvestigationHandler

# Initialize logger
logger = get_logger(__name__)

def show_banner():
    """Display the application banner with system information."""
    banner = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        IPDR ANALYSIS SYSTEM v{settings.APP_VERSION}                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  🔍 Internet Protocol Detail Record Analysis & Investigation Platform        ║
║                                                                              ║
║  📊 Features:                                                                ║
║    • B-party identification and relationship mapping                         ║
║    • Network topology analysis and visualization                             ║
║    • Suspicious activity detection and risk assessment                       ║
║    • Professional investigation report generation                            ║
║    • Temporal pattern analysis and anomaly detection                         ║
║                                                                              ║
║  ⚖️  FOR AUTHORIZED INVESTIGATION USE ONLY                                   ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

📋 System Status:
   Database: {settings.DATABASE_URL}
   Log Level: {settings.LOG_LEVEL}
   Debug Mode: {'🟢 Enabled' if settings.DEBUG else '🔴 Disabled'}
   Version: {settings.APP_VERSION}

"""
    print(banner)

def show_system_status():
    """Display comprehensive system status information."""
    print("\n🔧 SYSTEM STATUS REPORT")
    print("=" * 50)
    
    # Configuration validation
    print("\n📋 Configuration:")
    if validate_configuration():
        print("   ✅ Configuration valid")
    else:
        print("   ❌ Configuration issues detected")
    
    # Database connectivity
    print("\n💾 Database:")
    if check_db_connection():
        print("   ✅ Database connection successful")
        print(f"   📍 Location: {settings.DATABASE_URL}")
    else:
        print("   ❌ Database connection failed")
    
    # File system checks
    print("\n📁 File System:")
    
    # Check data directory
    data_dir = Path("data")
    if data_dir.exists():
        print(f"   ✅ Data directory: {data_dir.absolute()}")
    else:
        print(f"   ⚠️  Data directory missing: {data_dir.absolute()}")
    
    # Check logs directory
    logs_dir = Path("logs")
    if logs_dir.exists():
        print(f"   ✅ Logs directory: {logs_dir.absolute()}")
        # Count log files
        log_files = list(logs_dir.glob("*.log"))
        print(f"   📝 Log files: {len(log_files)}")
    else:
        print(f"   ⚠️  Logs directory missing: {logs_dir.absolute()}")
    
    # Check reports directory
    reports_dir = Path("reports")
    if reports_dir.exists():
        print(f"   ✅ Reports directory: {reports_dir.absolute()}")
        # Count report files
        report_files = list(reports_dir.glob("*.txt"))
        print(f"   📄 Report files: {len(report_files)}")
    else:
        print(f"   ⚠️  Reports directory missing: {reports_dir.absolute()}")
    
    # Memory and performance info
    print("\n⚡ Performance:")
    print(f"   📊 Max batch size: {settings.MAX_BATCH_SIZE}")
    print(f"   📈 Max query results: {settings.MAX_QUERY_RESULTS}")
    print(f"   🌐 Network analysis depth: {settings.NETWORK_ANALYSIS_MAX_DEPTH}")
    
    print("\n" + "=" * 50)

def main():
    """
    Main entry point for the IPDR Analysis System.
    
    Parses command line arguments and executes the appropriate functionality.
    """
    parser = argparse.ArgumentParser(
        description="IPDR Analysis System - Telecommunications Investigation Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s load-data              Load sample data for analysis
  %(prog)s demo                   Run investigation demonstration
  %(prog)s investigate 922027456759  Investigate specific user
  %(prog)s status                 Show system status
  
For detailed documentation, see the docs/ directory.
        """
    )
    
    # Add subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands', required=True)
    
    # Load data command
    load_parser = subparsers.add_parser('load-data', help='Load sample data into the system')
    
    # Clear and reload command
    clear_parser = subparsers.add_parser('clear-reload', help='Clear existing data and reload fresh sample data')
    
    # Suspicious analysis command
    suspicious_parser = subparsers.add_parser('suspicious', help='Analyze suspicious users and activities')
    
    # Demo command
    demo_parser = subparsers.add_parser('demo', help='Run investigation demonstration')
    
    # Investigate command
    investigate_parser = subparsers.add_parser('investigate', help='Investigate specific user')
    investigate_parser.add_argument('aadhaar', help='12-digit Aadhaar number to investigate')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show system status')
    
    # Version flag
    parser.add_argument('--version', action='version', 
                       version=f'IPDR Analysis System {settings.APP_VERSION}')
    
    # Debug flag
    parser.add_argument('--debug', action='store_true', 
                       help='Enable debug mode')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Set debug mode if requested
    if args.debug:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
        logger.info("🐛 Debug mode enabled")
    
    # Show banner
    show_banner()
    
    # Initialize database
    try:
        init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {str(e)}")
        return 1
    
    # Execute command using handlers
    try:
        if args.command == 'load-data':
            handler = LoadDataHandler()
            handler.handle()
        
        elif args.command == 'clear-reload':
            handler = LoadDataHandler(clear_data=True)
            handler.handle()
        
        elif args.command == 'suspicious':
            handler = SuspiciousAnalysisHandler()
            handler.handle()
        
        elif args.command == 'demo':
            handler = DemoHandler()
            handler.handle()
        
        elif args.command == 'investigate':
            handler = InvestigationHandler(args.aadhaar)
            handler.handle()
        
        elif args.command == 'status':
            show_system_status()
        
        return 0
    except Exception as e:
        logger.error(f"A critical error occurred: {e}")
        if settings.DEBUG:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\n🛑 Operation cancelled by user")
        sys.exit(130)  # Standard exit code for Ctrl+C
    except Exception as e:
        logger.error(f"💥 Unexpected error: {str(e)}")
        if settings.DEBUG:
            import traceback
            traceback.print_exc()
        sys.exit(1)