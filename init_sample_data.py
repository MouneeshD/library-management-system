"""
Sample Data Initialization Script
Populates the database with sample books, users, and categories
"""
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['library_db']

# Clear existing data
print("Clearing existing data...")
db.users.delete_many({})
db.books.delete_many({})
db.transactions.delete_many({})

# Create indexes
print("Creating indexes...")
db.users.create_index('email', unique=True)
db.users.create_index('username', unique=True)
db.books.create_index('isbn', unique=True)

# Create admin user
print("Creating admin user...")
admin = {
    'username': 'admin',
    'email': 'admin@library.com',
    'password': generate_password_hash('admin123'),
    'full_name': 'System Administrator',
    'role': 'admin',
    'phone': '+91-9876543210',
    'address': '123 Admin Street, City',
    'created_at': datetime.utcnow(),
    'updated_at': datetime.utcnow(),
    'is_active': True,
    'books_issued': 0,
    'total_fines': 0.0
}
db.users.insert_one(admin)

# Create sample users
print("Creating sample users...")
sample_users = [
    {
        'username': 'mouneesh',
        'email': 'mouneesh@example.com',
        'password': generate_password_hash('123456'),
        'full_name': 'Mouneesh',
        'role': 'user',
        'phone': '+91-9876543211',
        'address': '456 User Lane, City',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
        'is_active': True,
        'books_issued': 0,
        'total_fines': 0.0
    },
    {
        'username': 'jane_smith',
        'email': 'jane@example.com',
        'password': generate_password_hash('password123'),
        'full_name': 'Jane Smith',
        'role': 'user',
        'phone': '+91-9876543212',
        'address': '789 Reader Road, City',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
        'is_active': True,
        'books_issued': 0,
        'total_fines': 0.0
    },
    {
        'username': 'bob_wilson',
        'email': 'bob@example.com',
        'password': generate_password_hash('password123'),
        'full_name': 'Bob Wilson',
        'role': 'user',
        'phone': '+91-9876543213',
        'address': '321 Book Boulevard, City',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
        'is_active': True,
        'books_issued': 0,
        'total_fines': 0.0
    }
]
db.users.insert_many(sample_users)

# Create sample books
print("Creating sample books...")
sample_books = [
    {
        'title': 'To Kill a Mockingbird',
        'author': 'Harper Lee',
        'isbn': '978-0-06-112008-4',
        'category': 'Fiction',
        'publisher': 'J. B. Lippincott & Co.',
        'publication_year': 1960,
        'quantity': 5,
        'available_quantity': 5,
        'description': 'A classic novel about racial injustice and childhood innocence in the American South.',
        'cover_image': '/static/img/default-book.png',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
        'is_active': True,
        'total_issued': 0
    },
    {
        'title': '1984',
        'author': 'George Orwell',
        'isbn': '978-0-452-28423-4',
        'category': 'Science Fiction',
        'publisher': 'Secker & Warburg',
        'publication_year': 1949,
        'quantity': 4,
        'available_quantity': 4,
        'description': 'A dystopian novel about totalitarianism and surveillance.',
        'cover_image': '/static/img/default-book.png',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
        'is_active': True,
        'total_issued': 0
    },
    {
        'title': 'Pride and Prejudice',
        'author': 'Jane Austen',
        'isbn': '978-0-14-143951-8',
        'category': 'Romance',
        'publisher': 'T. Egerton',
        'publication_year': 1813,
        'quantity': 6,
        'available_quantity': 6,
        'description': 'A romantic novel of manners set in Georgian England.',
        'cover_image': '/static/img/default-book.png',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
        'is_active': True,
        'total_issued': 0
    },
    {
        'title': 'The Great Gatsby',
        'author': 'F. Scott Fitzgerald',
        'isbn': '978-0-7432-7356-5',
        'category': 'Fiction',
        'publisher': "Charles Scribner's Sons",
        'publication_year': 1925,
        'quantity': 5,
        'available_quantity': 5,
        'description': 'A critique of the American Dream during the Jazz Age.',
        'cover_image': '/static/img/default-book.png',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
        'is_active': True,
        'total_issued': 0
    },
    {
        'title': 'Harry Potter and the Philosopher\'s Stone',
        'author': 'J.K. Rowling',
        'isbn': '978-0-7475-3269-9',
        'category': 'Fantasy',
        'publisher': 'Bloomsbury',
        'publication_year': 1997,
        'quantity': 10,
        'available_quantity': 10,
        'description': 'The first book in the Harry Potter series.',
        'cover_image': '/static/img/default-book.png',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
        'is_active': True,
        'total_issued': 0
    },
    {
        'title': 'Introduction to Algorithms',
        'author': 'Thomas H. Cormen',
        'isbn': '978-0-262-03384-8',
        'category': 'Computer Science',
        'publisher': 'MIT Press',
        'publication_year': 2009,
        'quantity': 8,
        'available_quantity': 8,
        'description': 'A comprehensive textbook on algorithms.',
        'cover_image': '/static/img/default-book.png',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
        'is_active': True,
        'total_issued': 0
    },
    {
        'title': 'Clean Code',
        'author': 'Robert C. Martin',
        'isbn': '978-0-13-235088-4',
        'category': 'Computer Science',
        'publisher': 'Prentice Hall',
        'publication_year': 2008,
        'quantity': 6,
        'available_quantity': 6,
        'description': 'A handbook of agile software craftsmanship.',
        'cover_image': '/static/img/default-book.png',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
        'is_active': True,
        'total_issued': 0
    },
    {
        'title': 'Sapiens: A Brief History of Humankind',
        'author': 'Yuval Noah Harari',
        'isbn': '978-0-06-231609-7',
        'category': 'History',
        'publisher': 'Harper',
        'publication_year': 2011,
        'quantity': 5,
        'available_quantity': 5,
        'description': 'A narrative history of humanity.',
        'cover_image': '/static/img/default-book.png',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
        'is_active': True,
        'total_issued': 0
    }
]
db.books.insert_many(sample_books)

print("\n" + "="*60)
print("Sample data created successfully!")
print("="*60)
print("\nLogin Credentials:")
print("\nAdmin Account:")
print("  Username: admin")
print("  Password: admin123")
print("\nSample User Accounts:")
print("  Username: john_doe / jane_smith / bob_wilson")
print("  Password: password123")
print("\nDatabase Statistics:")
print(f"  Total Users: {db.users.count_documents({})}")
print(f"  Total Books: {db.books.count_documents({})}")
print(f"  Total Categories: {len(db.books.distinct('category'))}")
print("\nCategories:")
for category in sorted(db.books.distinct('category')):
    count = db.books.count_documents({'category': category})
    print(f"  - {category}: {count} books")
print("\n" + "="*60)
print("\nYou can now start the application with: python app.py")
print("="*60 + "\n")