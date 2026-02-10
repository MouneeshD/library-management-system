"""
User Routes - User dashboard and book browsing
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
from routes.auth import login_required
from models.book import Book
from models.transaction import Transaction
from models.user import User

user_bp = Blueprint('user', __name__)


@user_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    mongo = current_app.mongo
    
    # Get user's issued books
    issued_books = Transaction.get_user_transactions(
        mongo,
        user_id=session['user_id'],
        status='issued',
        limit=10
    )
    
    # Get user details
    user = User.get_by_id(mongo, session['user_id'])
    
    # Calculate total current fines
    total_fines = sum(book.get('current_fine', 0) for book in issued_books)
    
    # Get recently added books
    recent_books = Book.get_all_books(mongo, limit=6)
    
    return render_template(
        'user/dashboard.html',
        issued_books=issued_books,
        user=user,
        total_fines=total_fines,
        recent_books=recent_books
    )


@user_bp.route('/browse')
@login_required
def browse_books():
    """Browse available books"""
    mongo = current_app.mongo
    page = request.args.get('page', 1, type=int)
    per_page = 12
    search_query = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()
    
    skip = (page - 1) * per_page
    
    if search_query or category:
        books_list = Book.search_books(mongo, search_query, category, skip, per_page)
        total_books = Book.count_books(mongo, search_query, category)
    else:
        books_list = Book.get_all_books(mongo, skip, per_page)
        total_books = Book.count_books(mongo)
    
    total_pages = (total_books + per_page - 1) // per_page
    categories = Book.get_categories(mongo)
    
    return render_template(
        'user/browse_books.html',
        books=books_list,
        page=page,
        total_pages=total_pages,
        total_books=total_books,
        categories=categories,
        search_query=search_query,
        selected_category=category
    )


@user_bp.route('/book/<book_id>')
@login_required
def book_details(book_id):
    """View book details"""
    book = Book.get_by_id(current_app.mongo, book_id)
    
    if not book:
        flash('Book not found', 'danger')
        return redirect(url_for('user.browse_books'))
    
    # Check if user has already issued this book
    user_issued_books = Transaction.get_user_transactions(
        current_app.mongo,
        user_id=session['user_id'],
        status='issued'
    )
    
    already_issued = any(str(b['book_id']) == book_id for b in user_issued_books)
    
    return render_template(
        'user/book_details.html',
        book=book,
        already_issued=already_issued
    )


@user_bp.route('/my-books')
@login_required
def my_books():
    """View user's issued books"""
    mongo = current_app.mongo
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    skip = (page - 1) * per_page
    
    issued_books = Transaction.get_user_transactions(
        mongo,
        user_id=session['user_id'],
        status='issued',
        skip=skip,
        limit=per_page
    )
    
    total_transactions = Transaction.count_transactions(
        mongo,
        user_id=session['user_id'],
        status='issued'
    )
    
    total_pages = (total_transactions + per_page - 1) // per_page
    
    # Calculate total fines
    total_fines = sum(book.get('current_fine', 0) for book in issued_books)
    
    return render_template(
        'user/my_books.html',
        issued_books=issued_books,
        page=page,
        total_pages=total_pages,
        total_fines=total_fines
    )


@user_bp.route('/history')
@login_required
def history():
    """View user's borrowing history"""
    mongo = current_app.mongo
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    skip = (page - 1) * per_page
    
    transactions = Transaction.get_user_transactions(
        mongo,
        user_id=session['user_id'],
        skip=skip,
        limit=per_page
    )
    
    total_transactions = Transaction.count_transactions(
        mongo,
        user_id=session['user_id']
    )
    
    total_pages = (total_transactions + per_page - 1) // per_page
    
    return render_template(
        'user/history.html',
        transactions=transactions,
        page=page,
        total_pages=total_pages,
        total_transactions=total_transactions
    )