"""
Authentication and security module for the AI Knowledge Assistant.
Handles JWT tokens, user authentication, and security middleware.
"""

import os
import jwt
import bcrypt
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import sqlite3
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-jwt-key-change-this-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

# Security
security = HTTPBearer()

# Pydantic models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class User(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool = True
    created_at: datetime

class AuthManager:
    """
    Manages user authentication, JWT tokens, and security operations.
    """
    
    def __init__(self, db_path: str = "./auth.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize the user database."""
        with self._get_db_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create default admin user if no users exist
            cursor = conn.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                self._create_default_admin(conn)
    
    def _create_default_admin(self, conn):
        """Create a default admin user for initial setup."""
        admin_password = "admin123"  # Change this in production
        password_hash = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt())
        
        conn.execute("""
            INSERT INTO users (username, email, password_hash, full_name)
            VALUES (?, ?, ?, ?)
        """, ("admin", "admin@example.com", password_hash, "System Administrator"))
        
        logger.info("Created default admin user (username: admin, password: admin123)")
    
    @contextmanager
    def _get_db_connection(self):
        """Get a database connection with proper cleanup."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        try:
            password_hash = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt())
            
            with self._get_db_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO users (username, email, password_hash, full_name)
                    VALUES (?, ?, ?, ?)
                """, (user_data.username, user_data.email, password_hash, user_data.full_name))
                
                user_id = cursor.lastrowid
                
                # Fetch the created user
                user_row = conn.execute("""
                    SELECT id, username, email, full_name, is_active, created_at
                    FROM users WHERE id = ?
                """, (user_id,)).fetchone()
                
                return User(
                    id=user_row['id'],
                    username=user_row['username'],
                    email=user_row['email'],
                    full_name=user_row['full_name'],
                    is_active=bool(user_row['is_active']),
                    created_at=datetime.fromisoformat(user_row['created_at'])
                )
        
        except sqlite3.IntegrityError as e:
            if "username" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already exists"
                )
            elif "email" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User creation failed"
                )
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password."""
        with self._get_db_connection() as conn:
            user_row = conn.execute("""
                SELECT id, username, email, password_hash, full_name, is_active, created_at
                FROM users WHERE username = ? AND is_active = TRUE
            """, (username,)).fetchone()
            
            if not user_row:
                return None
            
            # Verify password
            if not bcrypt.checkpw(password.encode('utf-8'), user_row['password_hash']):
                return None
            
            return User(
                id=user_row['id'],
                username=user_row['username'],
                email=user_row['email'],
                full_name=user_row['full_name'],
                is_active=bool(user_row['is_active']),
                created_at=datetime.fromisoformat(user_row['created_at'])
            )
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get a user by ID."""
        with self._get_db_connection() as conn:
            user_row = conn.execute("""
                SELECT id, username, email, full_name, is_active, created_at
                FROM users WHERE id = ? AND is_active = TRUE
            """, (user_id,)).fetchone()
            
            if not user_row:
                return None
            
            return User(
                id=user_row['id'],
                username=user_row['username'],
                email=user_row['email'],
                full_name=user_row['full_name'],
                is_active=bool(user_row['is_active']),
                created_at=datetime.fromisoformat(user_row['created_at'])
            )
    
    def create_access_token(self, user: User) -> str:
        """Create a JWT access token for a user."""
        expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
        
        payload = {
            "sub": str(user.id),
            "username": user.username,
            "email": user.email,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            
            # Check if token is expired
            if datetime.utcnow() > datetime.fromtimestamp(payload.get("exp", 0)):
                return None
            
            return payload
        
        except jwt.InvalidTokenError:
            return None
    
    def login(self, login_data: UserLogin) -> Token:
        """Login a user and return a JWT token."""
        user = self.authenticate_user(login_data.username, login_data.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token = self.create_access_token(user)
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=JWT_EXPIRATION_HOURS * 3600
        )

# Global auth manager instance
auth_manager = AuthManager()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """
    Dependency to get the current authenticated user from JWT token.
    """
    token = credentials.credentials
    
    # Verify token
    payload = auth_manager.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user_id = int(payload.get("sub"))
    user = auth_manager.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to get the current active user.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return current_user

# Optional dependency for endpoints that can work with or without authentication
async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[User]:
    """
    Optional dependency that returns user if authenticated, None otherwise.
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None

def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Dependency that requires admin privileges.
    For now, we'll consider the first user (admin) as admin.
    In production, you'd have a proper role system.
    """
    if current_user.username != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    return current_user

