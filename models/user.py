"""
User Model - Handles user data structure and operations
"""
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from bson.objectid import ObjectId


class User:
    """User model for managing user data"""
    
    @staticmethod
    def create_user(mongo, username, email, password, full_name, role='user', phone='', address=''):
        """Create a new user in the database"""
        try:
            # Check if user already exists
            if mongo.db.users.find_one({'$or': [{'email': email}, {'username': username}]}):
                return None
            
            user_data = {
                'username': username,
                'email': email,
                'password': generate_password_hash(password),
                'full_name': full_name,
                'role': role,
                'phone': phone,
                'address': address,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'is_active': True,
                'books_issued': 0,
                'total_fines': 0.0
            }
            
            result = mongo.db.users.insert_one(user_data)
            return result.inserted_id
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    @staticmethod
    def authenticate(mongo, username_or_email, password):
        """Authenticate user with username/email and password"""
        try:
            user = mongo.db.users.find_one({
                '$or': [
                    {'username': username_or_email},
                    {'email': username_or_email}
                ]
            })
            
            if user and check_password_hash(user['password'], password):
                if user.get('is_active', True):
                    return user
            return None
        except Exception as e:
            print(f"Error authenticating user: {e}")
            return None
    
    @staticmethod
    def get_by_id(mongo, user_id):
        """Get user by ID"""
        try:
            return mongo.db.users.find_one({'_id': ObjectId(user_id)})
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    @staticmethod
    def update_user(mongo, user_id, update_data):
        """Update user information"""
        try:
            update_data['updated_at'] = datetime.utcnow()
            result = mongo.db.users.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating user: {e}")
            return False
    
    @staticmethod
    def change_password(mongo, user_id, new_password):
        """Change user password"""
        try:
            hashed_password = generate_password_hash(new_password)
            result = mongo.db.users.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'password': hashed_password, 'updated_at': datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error changing password: {e}")
            return False
    
    @staticmethod
    def get_all_users(mongo, role=None, skip=0, limit=20):
        """Get all users with optional role filter"""
        try:
            query = {}
            if role:
                query['role'] = role
            
            users = mongo.db.users.find(query).skip(skip).limit(limit).sort('created_at', -1)
            return list(users)
        except Exception as e:
            print(f"Error getting users: {e}")
            return []
    
    @staticmethod
    def count_users(mongo, role=None):
        """Count total users"""
        try:
            query = {}
            if role:
                query['role'] = role
            return mongo.db.users.count_documents(query)
        except Exception as e:
            print(f"Error counting users: {e}")
            return 0
    
    @staticmethod
    def toggle_active_status(mongo, user_id):
        """Toggle user active status"""
        try:
            user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
            if user:
                new_status = not user.get('is_active', True)
                result = mongo.db.users.update_one(
                    {'_id': ObjectId(user_id)},
                    {'$set': {'is_active': new_status, 'updated_at': datetime.utcnow()}}
                )
                return result.modified_count > 0
            return False
        except Exception as e:
            print(f"Error toggling user status: {e}")
            return False