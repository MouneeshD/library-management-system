"""
Admin Routes - Admin dashboard and management functions
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
from routes.auth import admin_required
from models.user import User
from models.book import Book
from models.transaction import Transaction
from bson.objectid import ObjectId
from datetime import datetime

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard with statistics"""
    mongo = current_app.mongo
    
    # Get statistics
    total_books = Book.count_books(mongo, active_only=True)
    total_users = User.count_users(mongo, role='user')
    issued_books = Transaction.count_transactions(mongo, status='issued')
    available_books = mongo.db.books.aggregate([
        {'$match': {'is_active': True}},
        {'$group': {'_id': None, 'total': {'$sum': '$available_quantity'}}}
    ])
    available_books = list(available_books)
    available_count = available_books[0]['total'] if available_books else 0
    
    # Get recent transactions
    recent_transactions = Transaction.get_all_transactions(mongo, limit=10)
    
    # Get overdue books
    overdue_transactions = Transaction.get_overdue_transactions(mongo)
    
    # Calculate total fines
    total_fines = sum(trans.get('current_fine', 0) for trans in overdue_transactions)
    
    return render_template(
        'admin/dashboard.html',
        total_books=total_books,
        total_users=total_users,
        issued_books=issued_books,
        available_books=available_count,
        recent_transactions=recent_transactions,
        overdue_count=len(overdue_transactions),
        total_fines=total_fines
    )


@admin_bp.route('/books')
@admin_required
def books():
    """Manage books"""
    mongo = current_app.mongo
    page = request.args.get('page', 1, type=int)
    per_page = 12
    search_query = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()
    
    skip = (page - 1) * per_page
    
    if search_query or category:
        books_list = Book.search_books(mongo, search_query, category, skip, per_page)
        total_books = Book.count_books(mongo, search_query, category, active_only=False)
    else:
        books_list = Book.get_all_books(mongo, skip, per_page, active_only=False)
        total_books = Book.count_books(mongo, active_only=False)
    
    total_pages = (total_books + per_page - 1) // per_page
    categories = Book.get_categories(mongo)
    
    return render_template(
        'admin/books.html',
        books=books_list,
        page=page,
        total_pages=total_pages,
        total_books=total_books,
        categories=categories,
        search_query=search_query,
        selected_category=category
    )


@admin_bp.route('/books/add', methods=['GET', 'POST'])
@admin_required
def add_book():
    """Add new book"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        isbn = request.form.get('isbn', '').strip()
        category = request.form.get('category', '').strip()
        publisher = request.form.get('publisher', '').strip()
        publication_year = request.form.get('publication_year', '').strip()
        quantity = request.form.get('quantity', '').strip()
        description = request.form.get('description', '').strip()
        cover_image = request.form.get('cover_image', '').strip()
        
        # Validation
        errors = []
        if not title:
            errors.append('Title is required')
        if not author:
            errors.append('Author is required')
        if not isbn:
            errors.append('ISBN is required')
        if not category:
            errors.append('Category is required')
        if not publisher:
            errors.append('Publisher is required')
        if not publication_year or not publication_year.isdigit():
            errors.append('Valid publication year is required')
        if not quantity or not quantity.isdigit() or int(quantity) < 1:
            errors.append('Valid quantity is required')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('admin/add_book.html')
        
        # Create book
        book_id = Book.create_book(
            current_app.mongo,
            title=title,
            author=author,
            isbn=isbn,
            category=category,
            publisher=publisher,
            publication_year=publication_year,
            quantity=quantity,
            description=description,
            cover_image=cover_image
        )
        
        if book_id:
            flash(f'Book "{title}" added successfully', 'success')
            return redirect(url_for('admin.books'))
        else:
            flash('Book with this ISBN already exists', 'danger')
    
    return render_template('admin/add_book.html')


@admin_bp.route('/books/edit/<book_id>', methods=['GET', 'POST'])
@admin_required
def edit_book(book_id):
    """Edit book details"""
    book = Book.get_by_id(current_app.mongo, book_id)
    if not book:
        flash('Book not found', 'danger')
        return redirect(url_for('admin.books'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        category = request.form.get('category', '').strip()
        publisher = request.form.get('publisher', '').strip()
        publication_year = request.form.get('publication_year', '').strip()
        quantity = request.form.get('quantity', '').strip()
        description = request.form.get('description', '').strip()
        cover_image = request.form.get('cover_image', '').strip()
        
        # Validation
        if not title or not author or not category:
            flash('Title, author, and category are required', 'danger')
            return render_template('admin/edit_book.html', book=book)
        
        update_data = {
            'title': title,
            'author': author,
            'category': category,
            'publisher': publisher,
            'publication_year': int(publication_year) if publication_year.isdigit() else book['publication_year'],
            'description': description
        }
        
        if cover_image:
            update_data['cover_image'] = cover_image
        
        # Update quantity if changed
        if quantity and quantity.isdigit():
            new_quantity = int(quantity)
            quantity_diff = new_quantity - book['quantity']
            update_data['quantity'] = new_quantity
            update_data['available_quantity'] = book['available_quantity'] + quantity_diff
        
        if Book.update_book(current_app.mongo, book_id, update_data):
            flash(f'Book "{title}" updated successfully', 'success')
            return redirect(url_for('admin.books'))
        else:
            flash('Error updating book', 'danger')
    
    return render_template('admin/edit_book.html', book=book)


@admin_bp.route('/books/delete/<book_id>', methods=['POST'])
@admin_required
def delete_book(book_id):
    """Delete (soft delete) book"""
    book = Book.get_by_id(current_app.mongo, book_id)
    if not book:
        flash('Book not found', 'danger')
        return redirect(url_for('admin.books'))
    
    # Check if book is currently issued
    issued_count = Transaction.count_transactions(current_app.mongo, status='issued')
    issued_books = Transaction.get_all_transactions(current_app.mongo, status='issued')
    
    for trans in issued_books:
        if str(trans['book_id']) == book_id:
            flash('Cannot delete book that is currently issued', 'danger')
            return redirect(url_for('admin.books'))
    
    if Book.delete_book(current_app.mongo, book_id):
        flash(f'Book "{book["title"]}" deleted successfully', 'success')
    else:
        flash('Error deleting book', 'danger')
    
    return redirect(url_for('admin.books'))


@admin_bp.route('/users')
@admin_required
def users():
    """Manage users"""
    mongo = current_app.mongo
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    skip = (page - 1) * per_page
    users_list = User.get_all_users(mongo, role='user', skip=skip, limit=per_page)
    total_users = User.count_users(mongo, role='user')
    total_pages = (total_users + per_page - 1) // per_page
    
    return render_template(
        'admin/users.html',
        users=users_list,
        page=page,
        total_pages=total_pages,
        total_users=total_users
    )


@admin_bp.route('/users/toggle-status/<user_id>', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    """Toggle user active status"""
    if User.toggle_active_status(current_app.mongo, user_id):
        flash('User status updated successfully', 'success')
    else:
        flash('Error updating user status', 'danger')
    
    return redirect(url_for('admin.users'))


@admin_bp.route('/issue-book', methods=['GET', 'POST'])
@admin_required
def issue_book():
    """Issue book to user"""
    mongo = current_app.mongo
    
    if request.method == 'POST':
        user_id = request.form.get('user_id', '').strip()
        book_id = request.form.get('book_id', '').strip()
        
        if not user_id or not book_id:
            flash('Please select both user and book', 'danger')
            return redirect(url_for('admin.issue_book'))
        
        # Issue book
        transaction_id = Transaction.issue_book(
            mongo,
            user_id=user_id,
            book_id=book_id,
            issued_by_admin_id=session['user_id']
        )
        
        if transaction_id:
            flash('Book issued successfully', 'success')
            return redirect(url_for('admin.transactions'))
        else:
            flash('Error issuing book. Check if book is available or user has reached maximum limit', 'danger')
    
    # Get available books and active users for the form
    available_books = Book.get_available_books(mongo, limit=1000)
    active_users = User.get_all_users(mongo, role='user', limit=1000)
    
    return render_template(
        'admin/issue_book.html',
        books=available_books,
        users=active_users
    )


@admin_bp.route('/transactions')
@admin_required
def transactions():
    """View all transactions"""
    mongo = current_app.mongo
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '').strip()
    per_page = 20
    
    skip = (page - 1) * per_page
    
    transactions_list = Transaction.get_all_transactions(
        mongo,
        status=status_filter if status_filter else None,
        skip=skip,
        limit=per_page
    )
    
    total_transactions = Transaction.count_transactions(
        mongo,
        status=status_filter if status_filter else None
    )
    
    total_pages = (total_transactions + per_page - 1) // per_page
    
    return render_template(
        'admin/transactions.html',
        transactions=transactions_list,
        page=page,
        total_pages=total_pages,
        total_transactions=total_transactions,
        status_filter=status_filter
    )


@admin_bp.route('/return-book/<transaction_id>', methods=['POST'])
@admin_required
def return_book(transaction_id):
    """Accept book return"""
    result = Transaction.return_book(
        current_app.mongo,
        transaction_id=transaction_id,
        returned_to_admin_id=session['user_id']
    )
    
    if result:
        if result['fine'] > 0:
            flash(f'Book returned successfully. Fine: ₹{result["fine"]:.2f} ({result["days_overdue"]} days overdue)', 'warning')
        else:
            flash('Book returned successfully', 'success')
    else:
        flash('Error returning book', 'danger')
    
    return redirect(url_for('admin.transactions'))


@admin_bp.route('/overdue-books')
@admin_required
def overdue_books():
    """View overdue books"""
    overdue_transactions = Transaction.get_overdue_transactions(current_app.mongo)
    
    return render_template(
        'admin/overdue_books.html',
        transactions=overdue_transactions
    )