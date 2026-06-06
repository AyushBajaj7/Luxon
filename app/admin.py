from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Product, Category, Subcategory, Order, User
import cloudinary.uploader

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    products = Product.query.all()
    categories = Category.query.all()
    orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    total_revenue = db.session.query(db.func.sum(Order.total_amount)).filter_by(payment_status='success').scalar() or 0
    total_orders = Order.query.count()
    total_customers = User.query.filter_by(role='customer').count()
    
    return render_template('admin/dashboard.html', 
                           products=products, 
                           categories=categories,
                           orders=orders,
                           total_revenue=total_revenue,
                           total_orders=total_orders,
                           total_customers=total_customers)

@admin_bp.route('/product/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = float(request.form.get('price'))
        stock = int(request.form.get('stock'))
        brand = request.form.get('brand')
        category_id = int(request.form.get('category_id'))
        
        image_file = request.files.get('image')
        image_url = None
        
        if image_file:
            upload_result = cloudinary.uploader.upload(image_file)
            image_url = upload_result.get('secure_url')
            
        product = Product(
            name=name, description=description, price=price, stock=stock,
            brand=brand, category_id=category_id, image_url=image_url
        )
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('admin.dashboard'))
        
    categories = Category.query.all()
    return render_template('admin/add_product.html', categories=categories)
