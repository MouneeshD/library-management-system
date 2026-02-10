"""
Book Model - Handles book data structure and operations
"""
from datetime import datetime
from bson.objectid import ObjectId


class Book:
    """Book model for managing book data"""
    
    @staticmethod
    def create_book(mongo, title, author, isbn, category, publisher, publication_year, 
                   quantity, description='', cover_image=''):
        """Create a new book in the database"""
        try:
            # Check if ISBN already exists
            if mongo.db.books.find_one({'isbn': isbn}):
                return None
            
            book_data = {
                'title': title,
                'author': author,
                'isbn': isbn,
                'category': category,
                'publisher': publisher,
                'publication_year': int(publication_year),
                'quantity': int(quantity),
                'available_quantity': int(quantity),
                'description': description,
                'cover_image': cover_image or '/static/img/default-book.png',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'is_active': True,
                'total_issued': 0,
                'rating': 0.0,
                'reviews_count': 0
            }
            
            result = mongo.db.books.insert_one(book_data)
            return result.inserted_id
        except Exception as e:
            print(f"Error creating book: {e}")
            return None
    
    @staticmethod
    def get_by_id(mongo, book_id):
        """Get book by ID"""
        try:
            return mongo.db.books.find_one({'_id': ObjectId(book_id)})
        except Exception as e:
            print(f"Error getting book: {e}")
            return None
    
    @staticmethod
    def get_by_isbn(mongo, isbn):
        """Get book by ISBN"""
        try:
            return mongo.db.books.find_one({'isbn': isbn})
        except Exception as e:
            print(f"Error getting book: {e}")
            return None
    
    @staticmethod
    def update_book(mongo, book_id, update_data):
        """Update book information"""
        try:
            update_data['updated_at'] = datetime.utcnow()
            result = mongo.db.books.update_one(
                {'_id': ObjectId(book_id)},
                {'$set': update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating book: {e}")
            return False
    
    @staticmethod
    def delete_book(mongo, book_id):
        """Soft delete book (set is_active to False)"""
        try:
            result = mongo.db.books.update_one(
                {'_id': ObjectId(book_id)},
                {'$set': {'is_active': False, 'updated_at': datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error deleting book: {e}")
            return False
    
    @staticmethod
    def search_books(mongo, query='', category='', skip=0, limit=12):
        """Search books by title, author, or ISBN with optional category filter"""
        try:
            filter_query = {'is_active': True}
            
            if query:
                filter_query['$or'] = [
                    {'title': {'$regex': query, '$options': 'i'}},
                    {'author': {'$regex': query, '$options': 'i'}},
                    {'isbn': {'$regex': query, '$options': 'i'}},
                    {'description': {'$regex': query, '$options': 'i'}}
                ]
            
            if category:
                filter_query['category'] = category
            
            books = mongo.db.books.find(filter_query).skip(skip).limit(limit).sort('title', 1)
            return list(books)
        except Exception as e:
            print(f"Error searching books: {e}")
            return []
    
    @staticmethod
    def get_all_books(mongo, skip=0, limit=12, active_only=True):
        """Get all books with pagination"""
        try:
            query = {}
            if active_only:
                query['is_active'] = True
            
            books = mongo.db.books.find(query).skip(skip).limit(limit).sort('created_at', -1)
            return list(books)
        except Exception as e:
            print(f"Error getting books: {e}")
            return []
    
    @staticmethod
    def count_books(mongo, query='', category='', active_only=True):
        """Count total books matching criteria"""
        try:
            filter_query = {}
            if active_only:
                filter_query['is_active'] = True
            
            if query:
                filter_query['$or'] = [
                    {'title': {'$regex': query, '$options': 'i'}},
                    {'author': {'$regex': query, '$options': 'i'}},
                    {'isbn': {'$regex': query, '$options': 'i'}}
                ]
            
            if category:
                filter_query['category'] = category
            
            return mongo.db.books.count_documents(filter_query)
        except Exception as e:
            print(f"Error counting books: {e}")
            return 0
    
    @staticmethod
    def update_quantity(mongo, book_id, change):
        """Update available quantity of a book"""
        try:
            result = mongo.db.books.update_one(
                {'_id': ObjectId(book_id)},
                {
                    '$inc': {'available_quantity': change},
                    '$set': {'updated_at': datetime.utcnow()}
                }
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating quantity: {e}")
            return False
    
    @staticmethod
    def get_categories(mongo):
        """Get all unique categories"""
        try:
            categories = mongo.db.books.distinct('category', {'is_active': True})
            return sorted(categories)
        except Exception as e:
            print(f"Error getting categories: {e}")
            return []
    
    @staticmethod
    def get_available_books(mongo, skip=0, limit=12):
        """Get books that are available for issuing"""
        try:
            books = mongo.db.books.find({
                'is_active': True,
                'available_quantity': {'$gt': 0}
            }).skip(skip).limit(limit).sort('title', 1)
            return list(books)
        except Exception as e:
            print(f"Error getting available books: {e}")
            return []