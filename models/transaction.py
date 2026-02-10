"""
Transaction Model - Handles book issue and return transactions
"""
from datetime import datetime, timedelta
from bson.objectid import ObjectId
from config import Config


class Transaction:
    """Transaction model for managing book issues and returns"""
    
    @staticmethod
    def issue_book(mongo, user_id, book_id, issued_by_admin_id):
        """Issue a book to a user"""
        try:
            # Check if book is available
            book = mongo.db.books.find_one({'_id': ObjectId(book_id)})
            if not book or book.get('available_quantity', 0) <= 0:
                return None
            
            # Check user's current issued books count
            user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
            if not user:
                return None
            
            current_issued = mongo.db.transactions.count_documents({
                'user_id': ObjectId(user_id),
                'status': 'issued'
            })
            
            if current_issued >= Config.MAX_BOOKS_PER_USER:
                return None
            
            # Create transaction
            issue_date = datetime.utcnow()
            due_date = issue_date + timedelta(days=Config.DEFAULT_ISSUE_DAYS)
            
            transaction_data = {
                'user_id': ObjectId(user_id),
                'book_id': ObjectId(book_id),
                'issued_by': ObjectId(issued_by_admin_id),
                'issue_date': issue_date,
                'due_date': due_date,
                'return_date': None,
                'status': 'issued',
                'fine': 0.0,
                'fine_paid': False,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            result = mongo.db.transactions.insert_one(transaction_data)
            
            if result.inserted_id:
                # Update book available quantity
                mongo.db.books.update_one(
                    {'_id': ObjectId(book_id)},
                    {
                        '$inc': {
                            'available_quantity': -1,
                            'total_issued': 1
                        },
                        '$set': {'updated_at': datetime.utcnow()}
                    }
                )
                
                # Update user's books issued count
                mongo.db.users.update_one(
                    {'_id': ObjectId(user_id)},
                    {
                        '$inc': {'books_issued': 1},
                        '$set': {'updated_at': datetime.utcnow()}
                    }
                )
                
                return result.inserted_id
            
            return None
        except Exception as e:
            print(f"Error issuing book: {e}")
            return None
    
    @staticmethod
    def return_book(mongo, transaction_id, returned_to_admin_id):
        """Return a book and calculate fine if overdue"""
        try:
            transaction = mongo.db.transactions.find_one({'_id': ObjectId(transaction_id)})
            if not transaction or transaction.get('status') != 'issued':
                return None
            
            return_date = datetime.utcnow()
            due_date = transaction['due_date']
            
            # Calculate fine if overdue
            fine = 0.0
            if return_date > due_date:
                days_overdue = (return_date - due_date).days
                fine = days_overdue * Config.FINE_PER_DAY
            
            # Update transaction
            result = mongo.db.transactions.update_one(
                {'_id': ObjectId(transaction_id)},
                {
                    '$set': {
                        'return_date': return_date,
                        'status': 'returned',
                        'fine': fine,
                        'returned_to': ObjectId(returned_to_admin_id),
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                # Update book available quantity
                mongo.db.books.update_one(
                    {'_id': transaction['book_id']},
                    {
                        '$inc': {'available_quantity': 1},
                        '$set': {'updated_at': datetime.utcnow()}
                    }
                )
                
                # Update user's books issued count and total fines
                mongo.db.users.update_one(
                    {'_id': transaction['user_id']},
                    {
                        '$inc': {
                            'books_issued': -1,
                            'total_fines': fine
                        },
                        '$set': {'updated_at': datetime.utcnow()}
                    }
                )
                
                return {
                    'status': 'success',
                    'fine': fine,
                    'days_overdue': (return_date - due_date).days if return_date > due_date else 0
                }
            
            return None
        except Exception as e:
            print(f"Error returning book: {e}")
            return None
    
    @staticmethod
    def get_by_id(mongo, transaction_id):
        """Get transaction by ID with book and user details"""
        try:
            transaction = mongo.db.transactions.find_one({'_id': ObjectId(transaction_id)})
            if transaction:
                # Populate book and user details
                transaction['book'] = mongo.db.books.find_one({'_id': transaction['book_id']})
                transaction['user'] = mongo.db.users.find_one({'_id': transaction['user_id']})
            return transaction
        except Exception as e:
            print(f"Error getting transaction: {e}")
            return None
    
    @staticmethod
    def get_user_transactions(mongo, user_id, status=None, skip=0, limit=20):
        """Get all transactions for a specific user"""
        try:
            query = {'user_id': ObjectId(user_id)}
            if status:
                query['status'] = status
            
            transactions = mongo.db.transactions.find(query).skip(skip).limit(limit).sort('issue_date', -1)
            result = []
            
            for trans in transactions:
                trans['book'] = mongo.db.books.find_one({'_id': trans['book_id']})
                
                # Calculate current fine for issued books
                if trans['status'] == 'issued' and datetime.utcnow() > trans['due_date']:
                    days_overdue = (datetime.utcnow() - trans['due_date']).days
                    trans['current_fine'] = days_overdue * Config.FINE_PER_DAY
                else:
                    trans['current_fine'] = 0.0
                
                result.append(trans)
            
            return result
        except Exception as e:
            print(f"Error getting user transactions: {e}")
            return []
    
    @staticmethod
    def get_all_transactions(mongo, status=None, skip=0, limit=20):
        """Get all transactions with optional status filter"""
        try:
            query = {}
            if status:
                query['status'] = status
            
            transactions = mongo.db.transactions.find(query).skip(skip).limit(limit).sort('issue_date', -1)
            result = []
            
            for trans in transactions:
                trans['book'] = mongo.db.books.find_one({'_id': trans['book_id']})
                trans['user'] = mongo.db.users.find_one({'_id': trans['user_id']})
                
                # Calculate current fine for issued books
                if trans['status'] == 'issued' and datetime.utcnow() > trans['due_date']:
                    days_overdue = (datetime.utcnow() - trans['due_date']).days
                    trans['current_fine'] = days_overdue * Config.FINE_PER_DAY
                else:
                    trans['current_fine'] = 0.0
                
                result.append(trans)
            
            return result
        except Exception as e:
            print(f"Error getting transactions: {e}")
            return []
    
    @staticmethod
    def count_transactions(mongo, user_id=None, status=None):
        """Count transactions with optional filters"""
        try:
            query = {}
            if user_id:
                query['user_id'] = ObjectId(user_id)
            if status:
                query['status'] = status
            
            return mongo.db.transactions.count_documents(query)
        except Exception as e:
            print(f"Error counting transactions: {e}")
            return 0
    
    @staticmethod
    def get_overdue_transactions(mongo):
        """Get all overdue transactions"""
        try:
            transactions = mongo.db.transactions.find({
                'status': 'issued',
                'due_date': {'$lt': datetime.utcnow()}
            }).sort('due_date', 1)
            
            result = []
            for trans in transactions:
                trans['book'] = mongo.db.books.find_one({'_id': trans['book_id']})
                trans['user'] = mongo.db.users.find_one({'_id': trans['user_id']})
                
                days_overdue = (datetime.utcnow() - trans['due_date']).days
                trans['current_fine'] = days_overdue * Config.FINE_PER_DAY
                trans['days_overdue'] = days_overdue
                
                result.append(trans)
            
            return result
        except Exception as e:
            print(f"Error getting overdue transactions: {e}")
            return []