"""
Routes package initialization
"""
from .auth import auth_bp
from .admin import admin_bp
from .user import user_bp
from .books import books_bp

__all__ = ['auth_bp', 'admin_bp', 'user_bp', 'books_bp']