from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload
from app import db
from app.models import Product, Cart, CartItem, Wishlist, Order, OrderItem, Payment, PromoCode
from sqlalchemy.exc import IntegrityError
from config import Config
import razorpay

shop_bp = Blueprint('shop', __name__)

# Initialize Razorpay Client
razorpay_client = razorpay.Client(auth=(Config.RAZORPAY_KEY_ID, Config.RAZORPAY_KEY_SECRET))

def get_or_create_cart():
    cart = Cart.query.options(joinedload(Cart.items).joinedload(CartItem.product)).filter_by(user_id=current_user.id).first()
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.session.add(cart)
        db.session.commit()
    return cart

def get_cart_totals(cart_id):
    """Algorithmic Database Aggregation to prevent loading all items into Python memory."""
    result = db.session.query(
        db.func.sum(Product.price * CartItem.quantity),
        db.func.sum(CartItem.quantity)
    ).join(CartItem, CartItem.product_id == Product.id)\
     .filter(CartItem.cart_id == cart_id).first()
     
    subtotal = result[0] or 0
    total_items = result[1] or 0
    
    discount_percent = session.get('applied_promo_discount', 0)
    discount_amount = subtotal * (discount_percent / 100.0)
    
    total = subtotal - discount_amount
    return subtotal, discount_amount, total, total_items

@shop_bp.route('/cart')
@login_required
def view_cart():
    cart = get_or_create_cart()
    subtotal, discount, total, _ = get_cart_totals(cart.id)
    promo_code = session.get('applied_promo_code')
    return render_template('shop/cart.html', cart=cart, subtotal=subtotal, discount=discount, total=total, promo_code=promo_code)

@shop_bp.route('/api/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    if product.stock <= 0:
        return jsonify({'error': 'Product is out of stock'}), 400
        
    cart = get_or_create_cart()
    cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
    
    if cart_item:
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
        else:
            return jsonify({'error': 'Cannot add more than available stock'}), 400
    else:
        cart_item = CartItem(cart_id=cart.id, product_id=product_id, quantity=1)
        db.session.add(cart_item)
        
    db.session.commit()
    _, _, _, total_items = get_cart_totals(cart.id)
    return jsonify({'success': True, 'message': 'Added to cart', 'total_items': total_items})

@shop_bp.route('/api/cart/apply-promo', methods=['POST'])
@login_required
def apply_promo():
    data = request.get_json(silent=True) or {}
    code = data.get('code', '').strip().upper()
    
    if not code:
        session.pop('applied_promo_code', None)
        session.pop('applied_promo_discount', None)
        cart = get_or_create_cart()
        subtotal, discount, total, total_items = get_cart_totals(cart.id)
        return jsonify({'success': True, 'message': 'Promo code removed', 'subtotal': subtotal, 'discount': discount, 'total': total})
        
    import datetime
    promo = PromoCode.query.filter_by(code=code, is_active=True).first()
    
    if not promo:
        return jsonify({'error': 'Invalid promo code'}), 400
        
    if promo.valid_until and promo.valid_until < datetime.datetime.utcnow():
        return jsonify({'error': 'Promo code has expired'}), 400
        
    if promo.usage_limit and promo.times_used >= promo.usage_limit:
        return jsonify({'error': 'Promo code usage limit reached'}), 400
        
    session['applied_promo_code'] = promo.code
    session['applied_promo_discount'] = promo.discount_percent
    
    cart = get_or_create_cart()
    subtotal, discount, total, total_items = get_cart_totals(cart.id)
    
    return jsonify({
        'success': True, 
        'message': f'Promo code applied ({promo.discount_percent}% off)', 
        'subtotal': round(subtotal, 2), 
        'discount': round(discount, 2), 
        'total': round(total, 2)
    })

@shop_bp.route('/api/cart/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    cart_item = CartItem.query.options(joinedload(CartItem.product)).get_or_404(item_id)
    if cart_item.cart.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.get_json(silent=True) or {}
    action = data.get('action')
    
    item_quantity = 0
    item_total = 0

    if action == 'increase':
        if cart_item.quantity < cart_item.product.stock:
            cart_item.quantity += 1
        item_quantity = cart_item.quantity
        item_total = cart_item.quantity * cart_item.product.price
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            item_quantity = cart_item.quantity
            item_total = cart_item.quantity * cart_item.product.price
        else:
            db.session.delete(cart_item)
    elif action == 'remove':
        db.session.delete(cart_item)
    else:
        return jsonify({'error': 'Invalid cart action'}), 400
        
    db.session.commit()
    
    # Recalculate totals via Database Aggregation
    cart = get_or_create_cart()
    subtotal, discount, total, total_items = get_cart_totals(cart.id)
    
    return jsonify({
        'success': True, 
        'subtotal': round(subtotal, 2), 
        'discount': round(discount, 2), 
        'total': round(total, 2),
        'item_quantity': item_quantity,
        'item_total': round(item_total, 2),
        'total_items': total_items
    })

@shop_bp.route('/wishlist')
@login_required
def view_wishlist():
    wishlist_items = Wishlist.query.filter_by(user_id=current_user.id).all()
    return render_template('shop/wishlist.html', items=wishlist_items)

@shop_bp.route('/api/wishlist/toggle/<int:product_id>', methods=['POST'])
@login_required
def toggle_wishlist(product_id):
    item = Wishlist.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if item:
        db.session.delete(item)
        message = 'Removed from wishlist'
        added = False
    else:
        item = Wishlist(user_id=current_user.id, product_id=product_id)
        db.session.add(item)
        message = 'Added to wishlist'
        added = True
        
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        message = 'Already in wishlist'
        added = True
    return jsonify({'success': True, 'message': message, 'added': added})

def process_checkout_transaction(cart, total, shipping_address):
    """Helper method encapsulating atomic DB updates and checkout logic."""
    for item in cart.items:
        # ATOMIC DB UPDATE: Prevents race conditions / overselling
        updated = Product.query.filter(
            Product.id == item.product_id,
            Product.stock >= item.quantity
        ).update({Product.stock: Product.stock - item.quantity})
        
        if not updated:
            db.session.rollback()
            raise ValueError(f'{item.product.name} does not have enough stock available (Requested: {item.quantity}).')
            
    # Create Order
    order = Order(
        user_id=current_user.id,
        total_amount=total,
        shipping_address=shipping_address
    )
    db.session.add(order)
    db.session.flush() # Get order ID
    
    # Add items
    for item in cart.items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.product.price
        )
        db.session.add(order_item)
    
    return order

def create_payment_record(order, total, rzp_order_id=None, simulated=False):
    """Helper method to encapsulate payment creation."""
    payment = Payment(
        order_id=order.id,
        amount=total
    )
    if simulated:
        payment.status = 'success'
        payment.razorpay_payment_id = 'simulated_pay_' + str(order.id)
        order.status = 'paid'
        order.payment_status = 'success'
    else:
        payment.razorpay_order_id = rzp_order_id
        
    db.session.add(payment)
    return payment

@shop_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart = get_or_create_cart()
    if not cart.items:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('main.products'))
        
    subtotal, discount, total, _ = get_cart_totals(cart.id)
    
    if request.method == 'POST':
        shipping_address = (request.form.get('shipping_address') or '').strip()
        if len(shipping_address) < 12:
            flash('Please enter a complete shipping address.', 'danger')
            return redirect(url_for('shop.checkout'))
            
        try:
            order = process_checkout_transaction(cart, total, shipping_address)
            
            # Record discount if any (this is optional but good if Order model supported it)
            # order.discount_amount = discount
            
            # Clear promo code after successful order creation
            session.pop('applied_promo_code', None)
            session.pop('applied_promo_discount', None)
            
            # Check if Razorpay keys are configured
            if not Config.RAZORPAY_KEY_ID or Config.RAZORPAY_KEY_ID in ['your_test_key_here', 'rzp_test_your_key_id_here', 'rzp_test_placeholder_key']:
                # Bypass Razorpay - Simulate Payment
                create_payment_record(order, total, simulated=True)
                
                # Clear cart
                CartItem.query.filter_by(cart_id=cart.id).delete()
                db.session.commit()
                
                flash('Payment simulated successfully (Razorpay bypassed)! Your order has been placed.', 'success')
                return redirect(url_for('shop.order_confirmation', order_id=order.id))

            # Create Razorpay Order
            rzp_order = razorpay_client.order.create({
                'amount': int(total * 100), # amount in paise
                'currency': 'INR', # Assuming USD for luxury
                'receipt': str(order.id),
                'payment_capture': 1
            })
            
            payment = create_payment_record(order, total, rzp_order_id=rzp_order['id'], simulated=False)
            
            # Clear cart
            CartItem.query.filter_by(cart_id=cart.id).delete()
            db.session.commit()
            
            return render_template('shop/payment.html', order=order, payment=payment, key_id=Config.RAZORPAY_KEY_ID)
            
        except ValueError as e:
            flash(str(e), 'danger')
            return redirect(url_for('shop.view_cart'))
        except Exception as e:
            db.session.rollback()
            flash(f'Payment initialization failed: {str(e)}', 'danger')
            return redirect(url_for('shop.checkout'))
            
    return render_template('shop/checkout.html', cart=cart, subtotal=subtotal, discount=discount, total=total)

@shop_bp.route('/payment/verify', methods=['POST'])
def payment_verify():
    data = request.form
    razorpay_payment_id = data.get('razorpay_payment_id')
    razorpay_order_id = data.get('razorpay_order_id')
    razorpay_signature = data.get('razorpay_signature')
    
    payment = Payment.query.filter_by(razorpay_order_id=razorpay_order_id).first()
    if not payment:
        return "Payment record not found", 404
        
    try:
        # Verify signature
        razorpay_client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        })
        
        # Payment successful
        payment.razorpay_payment_id = razorpay_payment_id
        payment.razorpay_signature = razorpay_signature
        payment.status = 'success'
        
        payment.order.status = 'paid'
        payment.order.payment_status = 'success'
        db.session.commit()
        
        flash('Payment successful! Your order has been placed.', 'success')
        return redirect(url_for('shop.order_confirmation', order_id=payment.order_id))
        
    except razorpay.errors.SignatureVerificationError:
        payment.status = 'failed'
        payment.order.payment_status = 'failed'
        db.session.commit()
        flash('Payment verification failed.', 'danger')
        return redirect(url_for('main.index'))

@shop_bp.route('/order/<int:order_id>')
@login_required
def order_confirmation(order_id):
    order = Order.query.options(joinedload(Order.items).joinedload(OrderItem.product)).get_or_404(order_id)
    if order.user_id != current_user.id:
        return "Unauthorized", 403
    return render_template('shop/order_confirmation.html', order=order)

@shop_bp.route('/profile')
@login_required
def profile():
    orders = Order.query.options(joinedload(Order.items).joinedload(OrderItem.product)).filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('shop/profile.html', orders=orders)
