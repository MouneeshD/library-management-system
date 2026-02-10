"""
Books API Routes - RESTful API endpoints for book operations
"""
from flask import Blueprint, jsonify, request, current_app
from models.book import Book
from models.transaction import Transaction
from bson.objectid import ObjectId
import json

books_bp = Blueprint('books', __name__)


class JSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for MongoDB ObjectId"""
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super(JSONEncoder, self).default(obj)


@books_bp.route('/api/books', methods=['GET'])
def get_books():
    """GET /books/api/books - Get all books with optional filters"""
    try:
        mongo = current_app.mongo
        search = request.args.get('search', '').strip()
        category = request.args.get('category', '').strip()
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 12, type=int)
        
        skip = (page - 1) * limit
        
        if search or category:
            books = Book.search_books(mongo, search, category, skip, limit)
            total = Book.count_books(mongo, search, category)
        else:
            books = Book.get_all_books(mongo, skip, limit)
            total = Book.count_books(mongo)
        
        # Convert ObjectId to string
        books_list = json.loads(JSONEncoder().encode(books))
        
        return jsonify({
            'status': 'success',
            'data': {
                'books': books_list,
                'total': total,
                'page': page,
                'limit': limit,
                'total_pages': (total + limit - 1) // limit
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@books_bp.route('/api/books/<book_id>', methods=['GET'])
def get_book(book_id):
    """GET /books/api/books/<book_id> - Get single book by ID"""
    try:
        book = Book.get_by_id(current_app.mongo, book_id)
        
        if not book:
            return jsonify({
                'status': 'error',
                'message': 'Book not found'
            }), 404
        
        book_data = json.loads(JSONEncoder().encode(book))
        
        return jsonify({
            'status': 'success',
            'data': book_data
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@books_bp.route('/api/books/search', methods=['GET'])
def search_books():
    """GET /books/api/books/search - Search books by query"""
    try:
        mongo = current_app.mongo
        query = request.args.get('q', '').strip()
        category = request.args.get('category', '').strip()
        
        if not query:
            return jsonify({
                'status': 'error',
                'message': 'Search query is required'
            }), 400
        
        books = Book.search_books(mongo, query, category, limit=50)
        books_list = json.loads(JSONEncoder().encode(books))
        
        return jsonify({
            'status': 'success',
            'data': {
                'books': books_list,
                'count': len(books_list)
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@books_bp.route('/api/categories', methods=['GET'])
def get_categories():
    """GET /books/api/categories - Get all book categories"""
    try:
        categories = Book.get_categories(current_app.mongo)
        
        return jsonify({
            'status': 'success',
            'data': {
                'categories': categories,
                'count': len(categories)
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@books_bp.route('/api/books/available', methods=['GET'])
def get_available_books():
    """GET /books/api/books/available - Get all available books"""
    try:
        mongo = current_app.mongo
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 12, type=int)
        
        skip = (page - 1) * limit
        books = Book.get_available_books(mongo, skip, limit)
        
        total = mongo.db.books.count_documents({
            'is_active': True,
            'available_quantity': {'$gt': 0}
        })
        
        books_list = json.loads(JSONEncoder().encode(books))
        
        return jsonify({
            'status': 'success',
            'data': {
                'books': books_list,
                'total': total,
                'page': page,
                'limit': limit
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@books_bp.route('/api/statistics', methods=['GET'])
def get_statistics():
    """GET /books/api/statistics - Get library statistics"""
    try:
        mongo = current_app.mongo
        
        stats = {
            'total_books': Book.count_books(mongo),
            'total_categories': len(Book.get_categories(mongo)),
            'issued_books': Transaction.count_transactions(mongo, status='issued'),
            'available_books': mongo.db.books.aggregate([
                {'$match': {'is_active': True}},
                {'$group': {'_id': None, 'total': {'$sum': '$available_quantity'}}}
            ]),
            'total_users': mongo.db.users.count_documents({'role': 'user'}),
            'overdue_books': len(Transaction.get_overdue_transactions(mongo))
        }
        
        available = list(stats['available_books'])
        stats['available_books'] = available[0]['total'] if available else 0
        
        return jsonify({
            'status': 'success',
            'data': stats
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500