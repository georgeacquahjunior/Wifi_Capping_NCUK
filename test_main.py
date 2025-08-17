import pytest
import json
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from main import app, create_access_token, SECRET_KEY, ALGORITHM
import jwt

client = TestClient(app)

class TestErrorHandling:
    """Test suite for robust error handling"""
    
    def test_health_check(self):
        """Test basic health check endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "WiFi Capping System API"
        assert data["status"] == "healthy"
    
    def test_login_success(self):
        """Test successful login"""
        response = client.post(
            "/auth/login",
            json={"username": "testuser", "password": "secret"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 1800  # 30 minutes
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = client.post(
            "/auth/login",
            json={"username": "testuser", "password": "wrongpassword"}
        )
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Incorrect username or password"
    
    def test_login_missing_user(self):
        """Test login with non-existent user"""
        response = client.post(
            "/auth/login",
            json={"username": "nonexistent", "password": "password"}
        )
        assert response.status_code == 401

class TestTokenExpiry:
    """Test suite for token expiry functionality"""
    
    def get_valid_token(self):
        """Helper method to get a valid token"""
        response = client.post(
            "/auth/login",
            json={"username": "testuser", "password": "secret"}
        )
        return response.json()["access_token"]
    
    def test_access_with_valid_token(self):
        """Test accessing protected endpoint with valid token"""
        token = self.get_valid_token()
        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
    
    def test_access_without_token(self):
        """Test accessing protected endpoint without token"""
        response = client.get("/auth/me")
        assert response.status_code == 403
    
    def test_access_with_invalid_token(self):
        """Test accessing protected endpoint with invalid token"""
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
        data = response.json()
        assert data["error"] == "INVALID_TOKEN"
        assert "Invalid access token" in data["message"]
    
    def test_access_with_expired_token(self):
        """Test accessing protected endpoint with expired token"""
        # Create an expired token
        expired_token = create_access_token(
            data={"sub": "testuser"},
            expires_delta=timedelta(seconds=-1)  # Expired 1 second ago
        )
        
        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        assert response.status_code == 401
        data = response.json()
        assert data["error"] == "TOKEN_EXPIRED"
        assert "expired" in data["message"].lower()
    
    def test_token_expiry_time(self):
        """Test that token contains correct expiry time"""
        token = self.get_valid_token()
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check that expiry is set correctly (within 5 seconds tolerance)
        exp_time = datetime.fromtimestamp(payload["exp"])
        expected_exp = datetime.utcnow() + timedelta(minutes=30)
        time_diff = abs((exp_time - expected_exp).total_seconds())
        assert time_diff < 5  # Within 5 seconds tolerance

class TestWiFiEndpoints:
    """Test suite for WiFi management endpoints"""
    
    def get_valid_token(self):
        """Helper method to get a valid token"""
        response = client.post(
            "/auth/login",
            json={"username": "testuser", "password": "secret"}
        )
        return response.json()["access_token"]
    
    def test_get_wifi_usage_authenticated(self):
        """Test getting WiFi usage with valid authentication"""
        token = self.get_valid_token()
        response = client.get(
            "/wifi/usage",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert data["user_id"] == "testuser"
        assert "total_bytes_used" in data
    
    def test_get_wifi_usage_unauthenticated(self):
        """Test getting WiFi usage without authentication"""
        response = client.get("/wifi/usage")
        assert response.status_code == 403
    
    def test_get_wifi_quota_authenticated(self):
        """Test getting WiFi quota with valid authentication"""
        token = self.get_valid_token()
        response = client.get(
            "/wifi/quota",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "daily_limit_mb" in data
        assert "monthly_limit_mb" in data
    
    def test_record_wifi_usage_valid(self):
        """Test recording WiFi usage with valid data"""
        token = self.get_valid_token()
        usage_data = {
            "user_id": "testuser",
            "bytes_used": 1024000,  # 1MB
            "session_start": datetime.utcnow().isoformat()
        }
        
        response = client.post(
            "/wifi/usage",
            headers={"Authorization": f"Bearer {token}"},
            json=usage_data
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "successfully" in data["message"].lower()
    
    def test_record_wifi_usage_for_other_user(self):
        """Test recording WiFi usage for another user (should fail)"""
        token = self.get_valid_token()
        usage_data = {
            "user_id": "otheruser",  # Different user
            "bytes_used": 1024000,
            "session_start": datetime.utcnow().isoformat()
        }
        
        response = client.post(
            "/wifi/usage",
            headers={"Authorization": f"Bearer {token}"},
            json=usage_data
        )
        assert response.status_code == 422
        data = response.json()
        assert data["error"] == "VALIDATION_ERROR"
        assert "another user" in data["message"]

class TestErrorResponses:
    """Test suite for error response formats"""
    
    def test_error_response_format(self):
        """Test that error responses follow the correct format"""
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
        data = response.json()
        
        # Check required fields in error response
        assert "error" in data
        assert "message" in data
        assert "timestamp" in data
        
        # Validate timestamp format
        timestamp = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
        assert isinstance(timestamp, datetime)
    
    def test_health_check_endpoint(self):
        """Test comprehensive health check"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "services" in data
        assert "database" in data["services"]
        assert "authentication" in data["services"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])