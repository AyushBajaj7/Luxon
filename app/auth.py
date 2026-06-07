from urllib.parse import urlsplit
from flask import Blueprint, render_template, redirect, url_for, flash, request
from app import db, bcrypt
from app.models import User
from flask_login import login_user, current_user, logout_user, login_required

auth_bp = Blueprint('auth', __name__)

def is_safe_next_url(target):
    if not target:
        return False
    ref_url = urlsplit(request.host_url)
    test_url = urlsplit(target)
    return (not test_url.netloc or test_url.netloc == ref_url.netloc) and test_url.scheme in ('', ref_url.scheme)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords must match.', 'danger')
            return redirect(url_for('auth.register'))

        user_exists = User.query.filter((User.email == email) | (User.username == username)).first()
        if user_exists:
            flash('Email or Username already exists.', 'danger')
            return redirect(url_for('auth.register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(full_name=full_name, username=username, email=email, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        
        flash('Your account has been created! You are now able to log in.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        email_or_username = request.form.get('email_or_username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter((User.email == email_or_username) | (User.username == email_or_username)).first()
        
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            return redirect(next_page) if is_safe_next_url(next_page) else redirect(url_for('main.index'))
        else:
            flash('Login Unsuccessful. Please check email/username and password.', 'danger')
            
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
