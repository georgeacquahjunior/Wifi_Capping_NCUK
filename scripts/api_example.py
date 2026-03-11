#!/usr/bin/env python3
"""
Example script demonstrating WiFi Capping NCUK API usage
"""

import requests
import json
import time
import sys


def main():
    """Demonstrate API usage"""
    
    base_url = "http://localhost:5000"
    
    print("WiFi Capping NCUK - API Example")
    print("=" * 40)
    
    # Check service status
    print("1. Checking service status...")
    try:
        response = requests.get(f"{base_url}/api/status")
        if response.status_code == 200:
            status = response.json()
            print(f"✓ Service running: {status['service_running']}")
            print(f"✓ RADIUS connected: {status['radius_connected']}")
            print(f"✓ Active sessions: {status['active_sessions']}")
        else:
            print("✗ Service not available")
            return
    except requests.ConnectionError:
        print("✗ Cannot connect to service. Make sure it's running with: python main.py start")
        return
    
    # Test RADIUS connection
    print("\n2. Testing RADIUS connection...")
    try:
        response = requests.get(f"{base_url}/api/test-radius")
        if response.status_code == 200:
            result = response.json()
            print(f"✓ RADIUS connection: {result['message']}")
        else:
            print("✗ RADIUS test failed")
    except Exception as e:
        print(f"✗ RADIUS test error: {e}")
    
    # Authenticate a test user
    print("\n3. Authenticating test user...")
    auth_data = {
        "username": "testuser",
        "password": "testpass",
        "user_ip": "192.168.1.100",
        "nas_ip": "192.168.1.1",
        "nas_port": 0,
        "bandwidth_limit_mb": 100
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/authenticate",
            headers={"Content-Type": "application/json"},
            data=json.dumps(auth_data)
        )
        
        result = response.json()
        if result.get("success"):
            session_id = result["session_id"]
            print(f"✓ Authentication successful")
            print(f"✓ Session ID: {session_id}")
            
            # Get session details
            print("\n4. Getting session details...")
            response = requests.get(f"{base_url}/api/sessions/{session_id}")
            if response.status_code == 200:
                session = response.json()
                print(f"✓ Username: {session['username']}")
                print(f"✓ User IP: {session['user_ip']}")
                print(f"✓ Bandwidth limit: {session['bandwidth_limit_mb']} MB")
                print(f"✓ Status: {'CAPPED' if session['is_capped'] else 'ACTIVE'}")
            
            # Wait a moment for monitoring
            print("\n5. Waiting for monitoring cycle...")
            time.sleep(3)
            
            # End the session
            print("\n6. Ending session...")
            response = requests.post(f"{base_url}/api/sessions/{session_id}/end")
            result = response.json()
            if result.get("success"):
                print("✓ Session ended successfully")
            else:
                print(f"✗ Failed to end session: {result.get('error')}")
                
        else:
            print(f"✗ Authentication failed: {result.get('error')}")
            
    except Exception as e:
        print(f"✗ Authentication error: {e}")
    
    # Get all sessions
    print("\n7. Getting all active sessions...")
    try:
        response = requests.get(f"{base_url}/api/sessions")
        if response.status_code == 200:
            sessions = response.json()
            print(f"✓ Active sessions: {len(sessions)}")
            for session_id, session in sessions.items():
                print(f"  - {session['username']} ({session_id[:8]}...): {session['total_mb']:.2f} MB")
        else:
            print("✗ Failed to get sessions")
    except Exception as e:
        print(f"✗ Sessions error: {e}")
    
    print("\n✅ API demonstration complete!")
    print("\nNote: Some operations may fail if no RADIUS server is configured.")
    print("This is expected behavior for demonstration purposes.")


if __name__ == "__main__":
    main()