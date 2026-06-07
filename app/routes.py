from flask import Blueprint, render_template, request, send_from_directory, current_app
from sqlalchemy import or_
from sqlalchemy.orm import joinedload
from app.models import Product, Category, Subcategory
import os

main_bp = Blueprint('main', __name__)

@main_bp.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(current_app.root_path, 'static', 'img'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@main_bp.route('/')
def index():
    featured_products = Product.query.options(joinedload(Product.category)).filter_by(is_featured=True).limit(5).all()
    return render_template('home.html', featured_products=featured_products)

@main_bp.route('/products')
def products():
    category_id = request.args.get('category')
    category_name = request.args.get('category_name')
    subcategory_name = request.args.get('subcategory_name')
    filter_type = request.args.get('filter_type')
    max_price = request.args.get('max_price')
    gender = request.args.get('gender')
    search = (request.args.get('q') or '').strip()
    page = request.args.get('page', 1, type=int)
    
    if filter_type:
        if filter_type.startswith('cat_'):
            category_name = filter_type[4:]
            subcategory_name = None
        elif filter_type.startswith('sub_'):
            subcategory_name = filter_type[4:]
            category_name = None

    active_filter = ""
    if subcategory_name:
        active_filter = f"sub_{subcategory_name}"
    elif category_name:
        active_filter = f"cat_{category_name}"
    elif category_id:
        # Fallback for old integer IDs if still used anywhere
        cat = Category.query.get(category_id)
        if cat:
            active_filter = f"cat_{cat.name}"
    
    query = Product.query.options(joinedload(Product.category))
    if category_id and not category_name and not subcategory_name:
        try:
            query = query.filter(Product.category_id == int(category_id))
        except ValueError:
            pass
    if category_name:
        category = Category.query.filter(Category.name.ilike(category_name)).first()
        if category:
            query = query.filter(Product.category_id == category.id)
    if subcategory_name:
        subcategory = Subcategory.query.filter(Subcategory.name.ilike(subcategory_name)).first()
        if subcategory:
            query = query.filter(Product.subcategory_id == subcategory.id)
    if max_price:
        try:
            query = query.filter(Product.price <= float(max_price))
        except ValueError:
            pass
    if gender:
        if gender == 'Men':
            query = query.filter(Product.gender.in_(['Men', 'Unisex']))
        elif gender == 'Women':
            query = query.filter(Product.gender.in_(['Women', 'Unisex']))
        else:
            query = query.filter(Product.gender == gender)
    if search:
        terms = search.split()
        for term in terms:
            like = f"%{term}%"
            query = query.filter(or_(
                Product.name.ilike(like),
                Product.brand.ilike(like),
                Product.description.ilike(like),
            ))
        
    sort_by = request.args.get('sort', 'newest')
    if sort_by == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(Product.price.desc())
    else:
        query = query.order_by(Product.created_at.desc(), Product.id.desc())
        
    pagination = query.paginate(page=page, per_page=21, error_out=False)
    
    return render_template('products.html', pagination=pagination, search=search, active_filter=active_filter, sort_by=sort_by, gender=gender)

@main_bp.route('/product/<int:id>')
def product_detail(id):
    product = Product.query.get_or_404(id)
    return render_template('product_detail.html', product=product)
