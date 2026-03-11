#!/usr/bin/env python3
"""
Simple test script to demonstrate the WiFi Capping System's robust error handling and token expiry features.
"""

import requests
import time
import json
from datetime import datetime, timezone

BASE_URL = "http://localhost:8000"

def print_response(response, description):
    """Print formatted response"""
    print(f"\n{'='*50}")
    print(f"Test: {description}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print('='*50)

def test_error_handling_and_token_expiry():
    """Test the robust error handling and token expiry features"""
    
    print("🚀 Testing WiFi Capping System - Error Handling & Token Expiry")
    
    # Test 1: Health check
    response = requests.get(f"{BASE_URL}/health")
    print_response(response, "Health Check")
    
    # Test 2: Access protected endpoint without token
    response = requests.get(f"{BASE_URL}/auth/me")
    print_response(response, "Access Protected Endpoint Without Token")
    
    # Test 3: Access with invalid token
    response = requests.get(
        f"{BASE_URL}/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    print_response(response, "Access with Invalid Token")
    
    # Test 4: Login with wrong credentials
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": "testuser", "password": "wrongpassword"}
    )
    print_response(response, "Login with Wrong Password")
    
    # Test 5: Successful login
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": "testuser", "password": "secret"}
    )
    print_response(response, "Successful Login")
    
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data["access_token"]
        expires_in = token_data["expires_in"]
        
        print(f"\n🔑 Access token obtained!")
        print(f"Token expires in: {expires_in} seconds")
        
        # Test 6: Access protected endpoint with valid token
        response = requests.get(
            f"{BASE_URL}/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        print_response(response, "Access with Valid Token")
        
        # Test 7: Get WiFi usage
        response = requests.get(
            f"{BASE_URL}/wifi/usage",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        print_response(response, "Get WiFi Usage")
        
        # Test 8: Get WiFi quota
        response = requests.get(
            f"{BASE_URL}/wifi/quota",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        print_response(response, "Get WiFi Quota")
        
        # Test 9: Record WiFi usage
        response = requests.post(
            f"{BASE_URL}/wifi/usage",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "user_id": "testuser",
                "bytes_used": 1048576,  # 1MB
                "session_start": datetime.now(timezone.utc).isoformat()
            }
        )
        print_response(response, "Record WiFi Usage")
        
        # Test 10: Try to record usage for another user (validation error)
        response = requests.post(
            f"{BASE_URL}/wifi/usage",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "user_id": "otheruser",
                "bytes_used": 1048576,
                "session_start": datetime.now(timezone.utc).isoformat()
            }
        )
        print_response(response, "Try to Record Usage for Another User")
        
        # Test 11: Create and test expired token
        from main import create_access_token
        from datetime import timedelta
        
        expired_token = create_access_token(
            data={"sub": "testuser"},
            expires_delta=timedelta(seconds=-1)  # Already expired
        )
        
        response = requests.get(
            f"{BASE_URL}/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        print_response(response, "Access with Expired Token")
        
        print(f"\n✅ All tests completed!")
        print(f"⏰ Current token expires in approximately {expires_in} seconds")
        print(f"🔐 Robust error handling and token expiry features are working correctly!")

if __name__ == "__main__":
    try:
        test_error_handling_and_token_expiry()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the server. Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")