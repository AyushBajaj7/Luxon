from flask import Blueprint, render_template, request
from app.models import Product, Category

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    featured_products = Product.query.filter_by(is_featured=True).limit(5).all()
    categories = Category.query.all()
    return render_template('home.html', featured_products=featured_products, categories=categories)

@main_bp.route('/products')
def products():
    category_id = request.args.get('category')
    category_name = request.args.get('category_name')
    subcategory_name = request.args.get('subcategory_name')
    max_price = request.args.get('max_price')
    page = request.args.get('page', 1, type=int)
    
    query = Product.query
    if category_id:
        try:
            query = query.filter(Product.category_id == int(category_id))
        except ValueError:
            pass
    if category_name:
        query = query.join(Category).filter(Category.name.ilike(category_name))
    if subcategory_name:
        query = query.join(Subcategory).filter(Subcategory.name.ilike(subcategory_name))
    if max_price:
        try:
            query = query.filter(Product.price <= float(max_price))
        except ValueError:
            pass
        
    pagination = query.paginate(page=page, per_page=12, error_out=False)
    categories = Category.query.all()
    
    return render_template('products.html', pagination=pagination, categories=categories, request=request)

@main_bp.route('/product/<int:id>')
def product_detail(id):
    product = Product.query.get_or_404(id)
    return render_template('product_detail.html', product=product)
