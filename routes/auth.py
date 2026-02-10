"""
Authentication Routes - Login, Logout, Registration
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from models.user import User
from functools import wraps

auth_bp = Blueprint('auth', __name__)


def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('auth.login'))
        if session.get('role') != 'admin':
            flash('Admin access required', 'danger')
            return redirect(url_for('user.dashboard'))
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    # Redirect if already logged in
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('user.dashboard'))
    
    if request.method == 'POST':
        username_or_email = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        if not username_or_email or not password:
            flash('Please provide both username/email and password', 'danger')
            return render_template('auth/login.html')
        
        # Authenticate user
        user = User.authenticate(current_app.mongo, username_or_email, password)
        
        if user:
            # Set session
            session.permanent = True if remember else False
            session['user_id'] = str(user['_id'])
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            session['role'] = user['role']
            session['email'] = user['email']
            
            flash(f'Welcome back, {user["full_name"]}!', 'success')
            
            # Redirect based on role
            if user['role'] == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('user.dashboard'))
        else:
            flash('Invalid username/email or password', 'danger')
    
    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    # Redirect if already logged in
    if 'user_id' in session:
        return redirect(url_for('user.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        
        # Validation
        errors = []
        
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters long')
        
        if not email or '@' not in email:
            errors.append('Please provide a valid email address')
        
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters long')
        
        if password != confirm_password:
            errors.append('Passwords do not match')
        
        if not full_name:
            errors.append('Please provide your full name')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('auth/register.html')
        
        # Create user
        user_id = User.create_user(
            current_app.mongo,
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            role='user',
            phone=phone,
            address=address
        )
        
        if user_id:
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Username or email already exists', 'danger')
    
    return render_template('auth/register.html')


@auth_bp.route('/logout')
def logout():
    """User logout"""
    username = session.get('username', 'User')
    session.clear()
    flash(f'Goodbye, {username}!', 'info')
    return redirect(url_for('index'))


@auth_bp.route('/profile')
@login_required
def profile():
    """View user profile"""
    user = User.get_by_id(current_app.mongo, session['user_id'])
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('index'))
    
    return render_template('auth/profile.html', user=user)


@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile"""
    user = User.get_by_id(current_app.mongo, session['user_id'])
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        
        if not full_name:
            flash('Full name is required', 'danger')
            return render_template('auth/edit_profile.html', user=user)
        
        update_data = {
            'full_name': full_name,
            'phone': phone,
            'address': address
        }
        
        if User.update_user(current_app.mongo, session['user_id'], update_data):
            session['full_name'] = full_name
            flash('Profile updated successfully', 'success')
            return redirect(url_for('auth.profile'))
        else:
            flash('Error updating profile', 'danger')
    
    return render_template('auth/edit_profile.html', user=user)


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password"""
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validate current password
        user = User.get_by_id(current_app.mongo, session['user_id'])
        if not User.authenticate(current_app.mongo, user['username'], current_password):
            flash('Current password is incorrect', 'danger')
            return render_template('auth/change_password.html')
        
        # Validate new password
        if len(new_password) < 6:
            flash('New password must be at least 6 characters long', 'danger')
            return render_template('auth/change_password.html')
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'danger')
            return render_template('auth/change_password.html')
        
        # Change password
        if User.change_password(current_app.mongo, session['user_id'], new_password):
            flash('Password changed successfully', 'success')
            return redirect(url_for('auth.profile'))
        else:
            flash('Error changing password', 'danger')
    
    return render_template('auth/change_password.html')