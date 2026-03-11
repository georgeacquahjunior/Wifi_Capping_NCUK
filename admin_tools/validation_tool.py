#!/usr/bin/env python3
"""
Network Administrator Validation Interface
Provides tools for validating FreeRADIUS-NAS-Backend flow
"""

import os
import sys
import json
import requests
import argparse
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import subprocess

# Load environment variables
load_dotenv()

class ValidationTool:
    def __init__(self):
        # Database configuration
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'user': os.getenv('DB_USER', 'radius_user'),
            'password': os.getenv('DB_PASSWORD', 'radius_password'),
            'database': os.getenv('DB_NAME', 'wifi_capping')
        }
        
        # Backend API configuration
        self.backend_url = f"http://localhost:{os.getenv('ADMIN_PORT', 5000)}/api"
        
        # RADIUS configuration
        self.radius_config = {
            'host': os.getenv('RADIUS_HOST', 'localhost'),
            'secret': os.getenv('RADIUS_SECRET', 'testing123'),
            'auth_port': int(os.getenv('RADIUS_AUTH_PORT', 1812)),
            'acct_port': int(os.getenv('RADIUS_ACCT_PORT', 1813))
        }
        
        # Setup database connection
        db_url = f"mysql+pymysql://{self.db_config['user']}:{self.db_config['password']}@{self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}"
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)

    def test_database_connection(self):
        """Test database connectivity"""
        print("Testing database connection...")
        try:
            with self.Session() as session:
                result = session.execute(text("SELECT COUNT(*) as count FROM users")).fetchone()
                print(f"✓ Database connection successful. Found {result.count} users.")
                return True
        except Exception as e:
            print(f"✗ Database connection failed: {str(e)}")
            return False

    def test_backend_api(self):
        """Test backend API connectivity"""
        print("Testing backend API connection...")
        try:
            response = requests.get(f"{self.backend_url}/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Backend API is healthy. Total users: {data.get('total_users', 'N/A')}")
                return True
            else:
                print(f"✗ Backend API returned status code: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Backend API connection failed: {str(e)}")
            return False

    def test_radius_auth(self, username="testuser1", password="password123"):
        """Test RADIUS authentication"""
        print(f"Testing RADIUS authentication for user: {username}")
        try:
            # Prepare authentication request
            auth_data = {
                "username": username,
                "password": password,
                "nas_ip": "192.168.1.1"
            }
            
            response = requests.post(f"{self.backend_url}/auth", json=auth_data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'accept':
                    print(f"✓ Authentication successful for {username}")
                    print(f"  Data remaining: {result.get('user_data', {}).get('data_remaining_mb', 'N/A')} MB")
                    return True
                else:
                    print(f"✗ Authentication rejected: {result.get('reason', 'Unknown')}")
                    return False
            else:
                print(f"✗ Authentication request failed with status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ RADIUS authentication test failed: {str(e)}")
            return False

    def test_accounting_flow(self, username="testuser1"):
        """Test complete accounting flow"""
        print(f"Testing accounting flow for user: {username}")
        session_id = f"test-session-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        try:
            # Start session
            start_data = {
                "session_id": session_id,
                "username": username,
                "nas_ip": "192.168.1.1",
                "nas_port": 1
            }
            
            response = requests.post(f"{self.backend_url}/accounting/start", json=start_data, timeout=10)
            if response.status_code != 200:
                print(f"✗ Failed to start accounting session: {response.status_code}")
                return False
            
            print(f"✓ Accounting session started: {session_id}")
            
            # Update session with data usage
            update_data = {
                "session_id": session_id,
                "bytes_in": 1024 * 1024,  # 1MB
                "bytes_out": 512 * 1024   # 512KB
            }
            
            response = requests.post(f"{self.backend_url}/accounting/update", json=update_data, timeout=10)
            if response.status_code != 200:
                print(f"✗ Failed to update accounting session: {response.status_code}")
                return False
            
            print("✓ Accounting session updated with data usage")
            
            # Stop session
            stop_data = {"session_id": session_id}
            response = requests.post(f"{self.backend_url}/accounting/stop", json=stop_data, timeout=10)
            if response.status_code != 200:
                print(f"✗ Failed to stop accounting session: {response.status_code}")
                return False
            
            print("✓ Accounting session stopped successfully")
            return True
            
        except Exception as e:
            print(f"✗ Accounting flow test failed: {str(e)}")
            return False

    def validate_nas_devices(self):
        """Validate NAS device configuration"""
        print("Validating NAS device configuration...")
        try:
            with self.Session() as session:
                result = session.execute(text("SELECT nas_ip, nas_name, is_active FROM nas_devices")).fetchall()
                
                if not result:
                    print("✗ No NAS devices found in database")
                    return False
                
                print(f"✓ Found {len(result)} NAS devices:")
                for row in result:
                    status = "Active" if row.is_active else "Inactive"
                    print(f"  - {row.nas_name} ({row.nas_ip}) - {status}")
                
                return True
                
        except Exception as e:
            print(f"✗ NAS device validation failed: {str(e)}")
            return False

    def generate_test_report(self):
        """Generate comprehensive validation report"""
        print("=" * 60)
        print("FREERADIUS-NAS-BACKEND VALIDATION REPORT")
        print("=" * 60)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print()
        
        tests = [
            ("Database Connection", self.test_database_connection),
            ("Backend API", self.test_backend_api),
            ("NAS Device Configuration", self.validate_nas_devices),
            ("RADIUS Authentication", self.test_radius_auth),
            ("Accounting Flow", self.test_accounting_flow)
        ]
        
        results = {}
        for test_name, test_func in tests:
            print(f"\n--- {test_name} ---")
            results[test_name] = test_func()
        
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        
        passed = sum(results.values())
        total = len(results)
        
        for test_name, result in results.items():
            status = "PASS" if result else "FAIL"
            print(f"{test_name}: {status}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("✓ All tests passed! FreeRADIUS-NAS-Backend flow is properly configured.")
            return True
        else:
            print("✗ Some tests failed. Please check the configuration and logs.")
            return False

    def show_active_sessions(self):
        """Show currently active RADIUS sessions"""
        print("Active RADIUS Sessions:")
        print("-" * 80)
        try:
            with self.Session() as session:
                result = session.execute(
                    text("""SELECT session_id, username, nas_ip_address, session_start,
                         (bytes_in + bytes_out) / (1024*1024) as total_mb
                         FROM radius_sessions 
                         WHERE is_active = TRUE 
                         ORDER BY session_start DESC""")
                ).fetchall()
                
                if not result:
                    print("No active sessions found.")
                    return
                
                for row in result:
                    duration = datetime.now() - row.session_start
                    print(f"Session: {row.session_id}")
                    print(f"  User: {row.username}")
                    print(f"  NAS: {row.nas_ip_address}")
                    print(f"  Duration: {duration}")
                    print(f"  Data: {row.total_mb:.2f} MB")
                    print()
                    
        except Exception as e:
            print(f"Error retrieving sessions: {str(e)}")

    def reset_user_data(self, username):
        """Reset user data usage (admin function)"""
        print(f"Resetting data usage for user: {username}")
        try:
            with self.Session() as session:
                session.execute(
                    text("UPDATE users SET data_used_mb = 0 WHERE username = :username"),
                    {"username": username}
                )
                session.commit()
                print(f"✓ Data usage reset for {username}")
                
                # Log admin action
                session.execute(
                    text("""INSERT INTO admin_log (admin_user, action, target_user, details)
                         VALUES ('admin', 'reset_data', :username, 'Data usage reset to 0')"""),
                    {"username": username}
                )
                session.commit()
                
        except Exception as e:
            print(f"✗ Failed to reset data for {username}: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Network Administrator Validation Tool for FreeRADIUS-NAS-Backend")
    parser.add_argument('--test', choices=['all', 'db', 'api', 'auth', 'accounting', 'nas'], 
                       help='Run specific tests')
    parser.add_argument('--sessions', action='store_true', help='Show active sessions')
    parser.add_argument('--reset-user', metavar='USERNAME', help='Reset data usage for a user')
    parser.add_argument('--report', action='store_true', help='Generate full validation report')
    
    args = parser.parse_args()
    
    validator = ValidationTool()
    
    if args.report or args.test == 'all':
        validator.generate_test_report()
    elif args.test == 'db':
        validator.test_database_connection()
    elif args.test == 'api':
        validator.test_backend_api()
    elif args.test == 'auth':
        validator.test_radius_auth()
    elif args.test == 'accounting':
        validator.test_accounting_flow()
    elif args.test == 'nas':
        validator.validate_nas_devices()
    elif args.sessions:
        validator.show_active_sessions()
    elif args.reset_user:
        validator.reset_user_data(args.reset_user)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()