from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Product, Cart, CartItem, Wishlist, Order, OrderItem, Payment
from config import Config
import razorpay

shop_bp = Blueprint('shop', __name__)

# Initialize Razorpay Client
razorpay_client = razorpay.Client(auth=(Config.RAZORPAY_KEY_ID, Config.RAZORPAY_KEY_SECRET))

def get_or_create_cart():
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.session.add(cart)
        db.session.commit()
    return cart

@shop_bp.route('/cart')
@login_required
def view_cart():
    cart = get_or_create_cart()
    subtotal = sum(item.product.price * item.quantity for item in cart.items)
    gst = subtotal * 0.18
    total = subtotal + gst
    return render_template('shop/cart.html', cart=cart, subtotal=subtotal, gst=gst, total=total)

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
    
    total_items = sum(item.quantity for item in cart.items)
    return jsonify({'success': True, 'message': 'Added to cart', 'total_items': total_items})

@shop_bp.route('/api/cart/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    if cart_item.cart.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.get_json()
    action = data.get('action')
    
    if action == 'increase':
        if cart_item.quantity < cart_item.product.stock:
            cart_item.quantity += 1
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
        else:
            db.session.delete(cart_item)
    elif action == 'remove':
        db.session.delete(cart_item)
        
    db.session.commit()
    
    # Recalculate totals
    cart = get_or_create_cart()
    subtotal = sum(item.product.price * item.quantity for item in cart.items)
    gst = subtotal * 0.18
    total = subtotal + gst
    total_items = sum(item.quantity for item in cart.items)
    
    return jsonify({
        'success': True, 
        'subtotal': round(subtotal, 2), 
        'gst': round(gst, 2), 
        'total': round(total, 2),
        'item_quantity': cart_item.quantity if cart_item in cart.items else 0,
        'item_total': round(cart_item.quantity * cart_item.product.price, 2) if cart_item in cart.items else 0,
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
        
    db.session.commit()
    return jsonify({'success': True, 'message': message, 'added': added})

@shop_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart = get_or_create_cart()
    if not cart.items:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('main.products'))
        
    subtotal = sum(item.product.price * item.quantity for item in cart.items)
    gst = subtotal * 0.18
    total = subtotal + gst
    
    if request.method == 'POST':
        shipping_address = request.form.get('shipping_address')
        
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
            
            # Reduce stock
            item.product.stock -= item.quantity
        
        # Check if Razorpay keys are configured
        if not Config.RAZORPAY_KEY_ID or Config.RAZORPAY_KEY_ID in ['your_test_key_here', 'rzp_test_your_key_id_here', 'rzp_test_placeholder_key']:
            # Bypass Razorpay - Simulate Payment
            payment = Payment(
                order_id=order.id,
                amount=total,
                status='success',
                razorpay_payment_id='simulated_pay_' + str(order.id)
            )
            order.status = 'paid'
            order.payment_status = 'success'
            db.session.add(payment)
            
            # Clear cart
            for item in cart.items:
                db.session.delete(item)
                
            db.session.commit()
            flash('Payment simulated successfully (Razorpay bypassed)! Your order has been placed.', 'success')
            return redirect(url_for('shop.order_confirmation', order_id=order.id))

        # Create Razorpay Order
        try:
            rzp_order = razorpay_client.order.create({
                'amount': int(total * 100), # amount in paise
                'currency': 'INR', # Assuming USD for luxury
                'receipt': str(order.id),
                'payment_capture': 1
            })
            
            payment = Payment(
                order_id=order.id,
                razorpay_order_id=rzp_order['id'],
                amount=total
            )
            db.session.add(payment)
            
            # Clear cart
            for item in cart.items:
                db.session.delete(item)
                
            db.session.commit()
            
            return render_template('shop/payment.html', order=order, payment=payment, key_id=Config.RAZORPAY_KEY_ID)
            
        except Exception as e:
            db.session.rollback()
            flash(f'Payment initialization failed: {str(e)}', 'danger')
            return redirect(url_for('shop.checkout'))
            
    return render_template('shop/checkout.html', cart=cart, subtotal=subtotal, gst=gst, total=total)

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
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        return "Unauthorized", 403
    return render_template('shop/order_confirmation.html', order=order)

@shop_bp.route('/profile')
@login_required
def profile():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('shop/profile.html', orders=orders)
