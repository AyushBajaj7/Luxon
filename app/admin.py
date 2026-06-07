from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Product, Category, Subcategory, Order, User, OrderItem, PromoCode
from sqlalchemy.orm import joinedload
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
    product_page = request.args.get('product_page', 1, type=int)
    order_page = request.args.get('order_page', 1, type=int)
    search = (request.args.get('q') or '').strip()
    sort = request.args.get('sort', 'created_at')
    order = request.args.get('order', 'desc')
    
    query = Product.query.options(joinedload(Product.category))
    if search:
        like = f"%{search}%"
        from sqlalchemy import or_
        query = query.filter(or_(Product.name.ilike(like), Product.brand.ilike(like)))
        
    if sort == 'price':
        order_col = Product.price.desc() if order == 'desc' else Product.price.asc()
    elif sort == 'stock':
        order_col = Product.stock.desc() if order == 'desc' else Product.stock.asc()
    elif sort == 'name':
        order_col = Product.name.desc() if order == 'desc' else Product.name.asc()
    else:
        order_col = Product.created_at.desc()
        
    products_pagination = query.order_by(order_col).paginate(page=product_page, per_page=25, error_out=False)
    
    categories = Category.query.all()
    
    orders_pagination = Order.query.options(joinedload(Order.user)).order_by(Order.created_at.desc()).paginate(page=order_page, per_page=15, error_out=False)
    
    total_revenue = db.session.query(db.func.sum(Order.total_amount)).filter_by(payment_status='success').scalar() or 0
    total_orders = Order.query.count()
    total_customers = User.query.filter_by(role='customer').count()
    
    category_order_counts_query = db.session.query(
        Category.name, db.func.sum(OrderItem.quantity)
    ).select_from(Category)\
     .outerjoin(Product, Category.id == Product.category_id)\
     .outerjoin(OrderItem, Product.id == OrderItem.product_id)\
     .group_by(Category.name).all()
     
    category_order_counts = {name: count or 0 for name, count in category_order_counts_query}
    
    promo_codes = PromoCode.query.order_by(PromoCode.created_at.desc()).all()
    
    return render_template('admin/dashboard.html', 
                           products_pagination=products_pagination, 
                           categories=categories,
                           orders_pagination=orders_pagination,
                           total_revenue=total_revenue,
                           total_orders=total_orders,
                           total_customers=total_customers,
                           category_order_counts=category_order_counts,
                           promo_codes=promo_codes,
                           search=search,
                           sort=sort,
                           order=order,
                           active_tab=request.args.get('tab', 'overview'))

@admin_bp.route('/product/add', methods=['POST'])
@login_required
@admin_required
def add_product():
    name = (request.form.get('name') or '').strip()
    description = (request.form.get('description') or '').strip()
    brand = (request.form.get('brand') or '').strip()
    try:
        price = float(request.form.get('price') or 0)
        original_price_str = request.form.get('original_price')
        original_price = float(original_price_str) if original_price_str else None
        stock = int(request.form.get('stock') or 0)
        category_id = int(request.form.get('category_id') or 0)
    except ValueError:
        flash('Price, stock, and category must be valid numbers.', 'danger')
        return redirect(url_for('admin.dashboard', tab='products'))

    if not name or price <= 0 or stock < 0 or not Category.query.get(category_id):
        flash('Please enter a product name, positive price, valid stock, and category.', 'danger')
        return redirect(url_for('admin.dashboard', tab='products'))
    
    image_file = request.files.get('image')
    image_url = None
    
    if image_file and image_file.filename:
        upload_result = cloudinary.uploader.upload(image_file)
        image_url = upload_result.get('secure_url')
        
    product = Product(
        name=name, description=description, price=price, original_price=original_price, stock=stock,
        brand=brand, category_id=category_id, image_url=image_url
    )
    db.session.add(product)
    db.session.commit()
    flash('Product added successfully!', 'success')
    return redirect(url_for('admin.dashboard', tab='products'))

@admin_bp.route('/product/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    if request.method == 'POST':
        product.name = (request.form.get('name') or '').strip()
        product.description = (request.form.get('description') or '').strip()
        product.brand = (request.form.get('brand') or '').strip()
        try:
            product.price = float(request.form.get('price') or 0)
            original_price_str = request.form.get('original_price')
            product.original_price = float(original_price_str) if original_price_str else None
            product.stock = int(request.form.get('stock') or 0)
            product.category_id = int(request.form.get('category_id') or 0)
        except ValueError:
            flash('Price, stock, and category must be valid numbers.', 'danger')
            return redirect(url_for('admin.edit_product', id=id))

        if not product.name or product.price <= 0 or product.stock < 0 or not Category.query.get(product.category_id):
            flash('Please enter a product name, positive price, valid stock, and category.', 'danger')
            return redirect(url_for('admin.edit_product', id=id))
        
        image_file = request.files.get('image')
        if image_file and image_file.filename:
            upload_result = cloudinary.uploader.upload(image_file)
            product.image_url = upload_result.get('secure_url')
            
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('admin.dashboard', tab='products'))
        
    categories = Category.query.all()
    return render_template('admin/edit_product.html', product=product, categories=categories)

@admin_bp.route('/product/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('admin.dashboard', tab='products'))

@admin_bp.route('/promo/add', methods=['POST'])
@login_required
@admin_required
def add_promo():
    code = (request.form.get('code') or '').strip().upper()
    try:
        discount_percent = float(request.form.get('discount_percent') or 0)
        usage_limit_str = request.form.get('usage_limit')
        usage_limit = int(usage_limit_str) if usage_limit_str else None
    except ValueError:
        flash('Discount and usage limit must be valid numbers.', 'danger')
        return redirect(url_for('admin.dashboard', tab='promos'))
        
    if not code or discount_percent <= 0 or discount_percent > 100:
        flash('Please enter a valid code and discount percentage (1-100).', 'danger')
        return redirect(url_for('admin.dashboard', tab='promos'))
        
    existing = PromoCode.query.filter_by(code=code).first()
    if existing:
        flash('Promo code already exists.', 'danger')
        return redirect(url_for('admin.dashboard', tab='promos'))
        
    promo = PromoCode(code=code, discount_percent=discount_percent, usage_limit=usage_limit)
    db.session.add(promo)
    db.session.commit()
    flash('Promo code created successfully!', 'success')
    return redirect(url_for('admin.dashboard', tab='promos'))

@admin_bp.route('/promo/<int:id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_promo(id):
    promo = PromoCode.query.get_or_404(id)
    promo.is_active = not promo.is_active
    db.session.commit()
    flash(f'Promo code {promo.code} {"activated" if promo.is_active else "deactivated"}.', 'success')
    return redirect(url_for('admin.dashboard', tab='promos'))

@admin_bp.route('/promo/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_promo(id):
    promo = PromoCode.query.get_or_404(id)
    db.session.delete(promo)
    db.session.commit()
    flash('Promo code deleted.', 'success')
    return redirect(url_for('admin.dashboard', tab='promos'))

@admin_bp.route('/change_password', methods=['POST'])
@login_required
@admin_required
def change_password():
    from app import bcrypt
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not current_password or not new_password or not confirm_password:
        flash('All fields are required.', 'danger')
        return redirect(url_for('admin.dashboard', tab='settings'))
        
    if new_password != confirm_password:
        flash('New passwords do not match.', 'danger')
        return redirect(url_for('admin.dashboard', tab='settings'))
        
    if not bcrypt.check_password_hash(current_user.password_hash, current_password):
        flash('Incorrect current password.', 'danger')
        return redirect(url_for('admin.dashboard', tab='settings'))
        
    current_user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
    db.session.commit()
    flash('Admin password changed successfully!', 'success')
    return redirect(url_for('admin.dashboard', tab='settings'))
