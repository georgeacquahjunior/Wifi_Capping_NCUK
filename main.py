from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt
import logging
import traceback
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme
security = HTTPBearer()

# Initialize FastAPI app
app = FastAPI(
    title="WiFi Capping System",
    description="A robust WiFi usage management system with token authentication",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class WiFiUsage(BaseModel):
    user_id: str
    bytes_used: int
    session_start: datetime
    session_end: Optional[datetime] = None

class WiFiQuota(BaseModel):
    user_id: str
    daily_limit_mb: int
    monthly_limit_mb: int

class ErrorResponse(BaseModel):
    error: str
    message: str
    timestamp: datetime
    request_id: Optional[str] = None
    
    model_config = {"json_encoders": {datetime: lambda v: v.isoformat()}}

# Custom Exception Classes
class TokenExpiredError(Exception):
    pass

class InvalidTokenError(Exception):
    pass

class UserNotFoundError(Exception):
    pass

class QuotaExceededError(Exception):
    pass

class CustomValidationError(Exception):
    def __init__(self, message: str, details: Dict[str, Any] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

# Mock database (replace with real database in production)
fake_users_db = {
    "testuser": {
        "username": "testuser",
        "full_name": "Test User",
        "email": "test@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
        "disabled": False,
    }
}

fake_wifi_usage_db = []
fake_quota_db = {
    "testuser": {
        "user_id": "testuser",
        "daily_limit_mb": 1024,
        "monthly_limit_mb": 10240
    }
}

# Utility functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(username: str):
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return UserInDB(**user_dict)
    return None

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Error handlers
@app.exception_handler(TokenExpiredError)
async def token_expired_handler(request, exc):
    logger.warning(f"Token expired for request: {request.url}")
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "error": "TOKEN_EXPIRED",
            "message": "Access token has expired. Please login again.",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

@app.exception_handler(InvalidTokenError)
async def invalid_token_handler(request, exc):
    logger.warning(f"Invalid token for request: {request.url}")
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "error": "INVALID_TOKEN",
            "message": "Invalid access token provided.",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

@app.exception_handler(UserNotFoundError)
async def user_not_found_handler(request, exc):
    logger.warning(f"User not found for request: {request.url}")
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": "USER_NOT_FOUND",
            "message": "User not found in the system.",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

@app.exception_handler(QuotaExceededError)
async def quota_exceeded_handler(request, exc):
    logger.warning(f"Quota exceeded for request: {request.url}")
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": "QUOTA_EXCEEDED",
            "message": "WiFi usage quota has been exceeded.",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

@app.exception_handler(CustomValidationError)
async def validation_error_handler(request, exc):
    logger.warning(f"Validation error for request: {request.url} - {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "VALIDATION_ERROR",
            "message": exc.message,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unexpected error for request: {request.url} - {str(exc)}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred. Please try again later.",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

# Token validation dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise InvalidTokenError()
        token_data = TokenData(username=username)
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError()
    except (jwt.DecodeError, jwt.InvalidTokenError):
        raise InvalidTokenError()
    
    user = get_user(username=token_data.username)
    if user is None:
        raise UserNotFoundError()
    return user

# Routes
@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "message": "WiFi Capping System API",
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc)
    }

@app.post("/auth/login", response_model=Token, tags=["Authentication"])
async def login_for_access_token(user_credentials: UserLogin):
    """
    Authenticate user and return access token with expiry
    """
    try:
        user = authenticate_user(user_credentials.username, user_credentials.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        logger.info(f"User {user.username} successfully authenticated")
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error for user {user_credentials.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service temporarily unavailable"
        )

@app.get("/auth/me", response_model=User, tags=["Authentication"])
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get current user information
    """
    return current_user

@app.get("/wifi/usage", tags=["WiFi Management"])
async def get_wifi_usage(current_user: User = Depends(get_current_user)):
    """
    Get current user's WiFi usage statistics
    """
    try:
        user_usage = [usage for usage in fake_wifi_usage_db if usage.get("user_id") == current_user.username]
        total_bytes = sum(usage.get("bytes_used", 0) for usage in user_usage)
        
        return {
            "user_id": current_user.username,
            "total_bytes_used": total_bytes,
            "total_mb_used": round(total_bytes / 1024 / 1024, 2),
            "sessions": len(user_usage),
            "last_updated": datetime.now(timezone.utc)
        }
    except Exception as e:
        logger.error(f"Error getting WiFi usage for user {current_user.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve usage data"
        )

@app.get("/wifi/quota", tags=["WiFi Management"])
async def get_wifi_quota(current_user: User = Depends(get_current_user)):
    """
    Get current user's WiFi quota information
    """
    try:
        quota = fake_quota_db.get(current_user.username)
        if not quota:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No quota found for user"
            )
        
        return quota
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting WiFi quota for user {current_user.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve quota information"
        )

@app.post("/wifi/usage", tags=["WiFi Management"])
async def record_wifi_usage(usage: WiFiUsage, current_user: User = Depends(get_current_user)):
    """
    Record WiFi usage for the current user
    """
    try:
        # Validate user can only record their own usage
        if usage.user_id != current_user.username:
            raise CustomValidationError(
                "Cannot record usage for another user",
                {"provided_user": usage.user_id, "authenticated_user": current_user.username}
            )
        
        # Check quota before recording
        quota = fake_quota_db.get(current_user.username)
        if quota:
            current_usage = sum(u.get("bytes_used", 0) for u in fake_wifi_usage_db if u.get("user_id") == current_user.username)
            daily_limit_bytes = quota["daily_limit_mb"] * 1024 * 1024
            
            if current_usage + usage.bytes_used > daily_limit_bytes:
                raise QuotaExceededError()
        
        # Record usage
        usage_record = {
            "user_id": usage.user_id,
            "bytes_used": usage.bytes_used,
            "session_start": usage.session_start,
            "session_end": usage.session_end,
            "recorded_at": datetime.now(timezone.utc)
        }
        
        fake_wifi_usage_db.append(usage_record)
        logger.info(f"Recorded {usage.bytes_used} bytes usage for user {current_user.username}")
        
        return {
            "message": "Usage recorded successfully",
            "usage_id": len(fake_wifi_usage_db),
            "timestamp": datetime.now(timezone.utc)
        }
        
    except (QuotaExceededError, CustomValidationError):
        raise
    except Exception as e:
        logger.error(f"Error recording WiFi usage for user {current_user.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to record usage data"
        )

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Comprehensive health check endpoint
    """
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc),
            "version": "1.0.0",
            "services": {
                "database": "connected",  # Mock status
                "authentication": "operational",
                "wifi_monitoring": "active"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service health check failed"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)