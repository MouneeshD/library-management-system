"""
Configuration settings for the Library Management System
"""
import os
from datetime import timedelta


class Config:
    """Application configuration class"""
    
    # Secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # MongoDB configuration
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/library_db'
    
    # Session configuration
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # File upload configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Library business rules
    MAX_BOOKS_PER_USER = 5
    DEFAULT_ISSUE_DAYS = 14
    FINE_PER_DAY = 5  # Fine in currency units per day
    
    # Pagination
    BOOKS_PER_PAGE = 12
    USERS_PER_PAGE = 20
    TRANSACTIONS_PER_PAGE = 20