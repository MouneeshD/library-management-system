"""
Library Management System - Main Application Entry Point
"""
from flask import Flask, render_template, redirect, url_for, session
from flask_pymongo import PyMongo
from datetime import timedelta
import os
from config import Config

# Import blueprints
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.user import user_bp
from routes.books import books_bp

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize MongoDB
mongo = PyMongo(app)

# Make mongo accessible to blueprints
app.mongo = mongo

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(books_bp, url_prefix='/books')


@app.route('/')
def index():
    """Home page - redirect based on login status"""
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('user.dashboard'))
    return render_template('index.html')


@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return render_template('500.html'), 500


@app.context_processor
def inject_user():
    """Make user info available to all templates"""
    return dict(
        logged_in='user_id' in session,
        username=session.get('username', ''),
        role=session.get('role', '')
    )


if __name__ == '__main__':
    # Create indexes for better performance
    with app.app_context():
        # Users collection indexes
        mongo.db.users.create_index('email', unique=True)
        mongo.db.users.create_index('username', unique=True)
        
        # Books collection indexes
        mongo.db.books.create_index('isbn', unique=True)
        mongo.db.books.create_index('title')
        mongo.db.books.create_index('author')
        mongo.db.books.create_index('category')
        
        # Transactions collection indexes
        mongo.db.transactions.create_index('user_id')
        mongo.db.transactions.create_index('book_id')
        mongo.db.transactions.create_index('issue_date')
        mongo.db.transactions.create_index('status')

    
    app.run(debug=True, host='0.0.0.0', port=5000)