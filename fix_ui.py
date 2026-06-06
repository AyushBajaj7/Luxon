import os
from app import create_app, db
from app.models import Order, Payment, OrderItem

app = create_app()

def cleanup_ghost_orders():
    with app.app_context():
        # Find orders with no items
        ghost_orders = Order.query.filter(~Order.items.any()).all()
        for order in ghost_orders:
            # Delete payments for this order
            Payment.query.filter_by(order_id=order.id).delete()
            db.session.delete(order)
        db.session.commit()
        print(f"Cleaned up {len(ghost_orders)} ghost orders.")

def update_templates():
    login_html = """{% extends 'base.html' %}
{% block title %}Sign In | Luxon{% endblock %}
{% block content %}
<div class="container py-5 motion-container">
    <div class="row justify-content-center">
        <div class="col-md-6 col-lg-5">
            <div class="card border-0 shadow-lg rounded-4 p-5 auth-card">
                <div class="text-center mb-4">
                    <h2 class="fw-bold text-navy" style="font-family: 'Playfair Display', serif;">Welcome Back</h2>
                    <p class="text-muted small">Sign in to access your luxury shopping experience</p>
                </div>
                <form method="POST" action="{{ url_for('auth.login') }}">
                    <div class="mb-4 input-group-custom">
                        <label class="form-label small fw-bold text-muted text-uppercase letter-spacing-1">Email or Username</label>
                        <input type="text" class="form-control p-3 bg-light border-0 rounded-3" name="email_or_username" placeholder="Enter your email" required>
                    </div>
                    <div class="mb-4 input-group-custom">
                        <label class="form-label small fw-bold text-muted text-uppercase letter-spacing-1">Password</label>
                        <input type="password" class="form-control p-3 bg-light border-0 rounded-3" name="password" placeholder="••••••••" required>
                    </div>
                    <div class="mb-4 d-flex justify-content-between align-items-center">
                        <div class="form-check">
                            <input type="checkbox" class="form-check-input border-secondary" id="remember" name="remember">
                            <label class="form-check-label small text-muted" for="remember">Remember me</label>
                        </div>
                        <a href="#" class="small text-gold text-decoration-none fw-semibold">Forgot password?</a>
                    </div>
                    <button type="submit" class="btn btn-navy w-100 py-3 rounded-pill fw-bold shadow-sm mb-4">SIGN IN</button>
                </form>
                <div class="text-center">
                    <p class="small text-muted mb-0">New to Luxon? <a href="{{ url_for('auth.register') }}" class="text-navy fw-bold text-decoration-none border-bottom border-navy pb-1">Create an Account</a></p>
                </div>
            </div>
        </div>
    </div>
</div>
<script type="module">
    import { animate } from "https://cdn.jsdelivr.net/npm/motion@11.11.13/+esm";
    animate(".auth-card", { opacity: [0, 1], y: [30, 0] }, { duration: 0.6, easing: "ease-out" });
    animate(".input-group-custom", { opacity: [0, 1], x: [-20, 0] }, { duration: 0.5, delay: 0.2, easing: "ease-out" });
</script>
<style>.auth-card, .input-group-custom { opacity: 0; } .letter-spacing-1 { letter-spacing: 1px; }</style>
{% endblock %}"""

    register_html = """{% extends 'base.html' %}
{% block title %}Create Account | Luxon{% endblock %}
{% block content %}
<div class="container py-5 motion-container">
    <div class="row justify-content-center">
        <div class="col-md-6 col-lg-5">
            <div class="card border-0 shadow-lg rounded-4 p-5 auth-card">
                <div class="text-center mb-4">
                    <h2 class="fw-bold text-navy" style="font-family: 'Playfair Display', serif;">Join Luxon</h2>
                    <p class="text-muted small">Unlock exclusive access to the world's finest products</p>
                </div>
                <form method="POST" action="{{ url_for('auth.register') }}">
                    <div class="mb-3 input-group-custom">
                        <label class="form-label small fw-bold text-muted text-uppercase letter-spacing-1">Full Name</label>
                        <input type="text" class="form-control p-3 bg-light border-0 rounded-3" name="full_name" placeholder="John Doe" required>
                    </div>
                    <div class="mb-3 input-group-custom">
                        <label class="form-label small fw-bold text-muted text-uppercase letter-spacing-1">Username</label>
                        <input type="text" class="form-control p-3 bg-light border-0 rounded-3" name="username" placeholder="johndoe" required>
                    </div>
                    <div class="mb-3 input-group-custom">
                        <label class="form-label small fw-bold text-muted text-uppercase letter-spacing-1">Email Address</label>
                        <input type="email" class="form-control p-3 bg-light border-0 rounded-3" name="email" placeholder="john@example.com" required>
                    </div>
                    <div class="mb-3 input-group-custom">
                        <label class="form-label small fw-bold text-muted text-uppercase letter-spacing-1">Password</label>
                        <input type="password" class="form-control p-3 bg-light border-0 rounded-3" name="password" placeholder="••••••••" required>
                    </div>
                    <div class="mb-4 input-group-custom">
                        <label class="form-label small fw-bold text-muted text-uppercase letter-spacing-1">Confirm Password</label>
                        <input type="password" class="form-control p-3 bg-light border-0 rounded-3" name="confirm_password" placeholder="••••••••" required>
                    </div>
                    <button type="submit" class="btn btn-navy w-100 py-3 rounded-pill fw-bold shadow-sm mb-4">CREATE ACCOUNT</button>
                </form>
                <div class="text-center">
                    <p class="small text-muted mb-0">Already a member? <a href="{{ url_for('auth.login') }}" class="text-navy fw-bold text-decoration-none border-bottom border-navy pb-1">Sign In</a></p>
                </div>
            </div>
        </div>
    </div>
</div>
<script type="module">
    import { animate, stagger } from "https://cdn.jsdelivr.net/npm/motion@11.11.13/+esm";
    animate(".auth-card", { opacity: [0, 1], y: [30, 0] }, { duration: 0.6, easing: "ease-out" });
    animate(".input-group-custom", { opacity: [0, 1], x: [-20, 0] }, { duration: 0.4, delay: stagger(0.1), easing: "ease-out" });
</script>
<style>.auth-card, .input-group-custom { opacity: 0; } .letter-spacing-1 { letter-spacing: 1px; }</style>
{% endblock %}"""

    order_confirmation_html = """{% extends 'base.html' %}
{% block title %}Order Confirmed | Luxon{% endblock %}
{% block content %}
<div class="container py-5 text-center my-5">
    <div class="row justify-content-center">
        <div class="col-md-8 col-lg-6">
            <div class="card border-0 shadow-lg rounded-4 p-5 confirm-card">
                <div class="mb-4 confirm-icon">
                    <div class="bg-success bg-opacity-10 text-success rounded-circle d-inline-flex align-items-center justify-content-center" style="width: 100px; height: 100px;">
                        <i class="bi bi-check2 fs-1"></i>
                    </div>
                </div>
                <h1 class="fw-bold mb-3 text-navy confirm-text" style="font-family: 'Playfair Display', serif;">Thank You!</h1>
                <p class="text-muted mb-5 confirm-text">Your luxury order has been placed successfully. A confirmation email will be sent shortly.</p>
                
                <div class="bg-light p-4 rounded-4 text-start mb-5 confirm-details">
                    <div class="d-flex justify-content-between mb-3 border-bottom pb-3">
                        <span class="text-muted fw-semibold">Order Number</span>
                        <span class="fw-bold text-navy">#{{ order.id }}</span>
                    </div>
                    <div class="d-flex justify-content-between mb-3 border-bottom pb-3">
                        <span class="text-muted fw-semibold">Date</span>
                        <span class="fw-bold text-navy">{{ order.created_at.strftime('%B %d, %Y') }}</span>
                    </div>
                    <div class="d-flex justify-content-between mb-3 border-bottom pb-3">
                        <span class="text-muted fw-semibold">Total Paid</span>
                        <span class="fw-bold text-gold fs-5">₹{{ "{:,.0f}".format(order.total_amount) }}</span>
                    </div>
                    <div class="d-flex justify-content-between">
                        <span class="text-muted fw-semibold">Payment ID</span>
                        <span class="fw-bold text-navy small font-monospace">{{ order.payment.razorpay_payment_id if order.payment else 'Pending' }}</span>
                    </div>
                </div>
                
                <div class="d-flex justify-content-center gap-3 confirm-actions">
                    <a href="{{ url_for('shop.profile') }}" class="btn btn-outline-navy rounded-pill px-4 py-2 fw-semibold">View Order Status</a>
                    <a href="{{ url_for('main.products') }}" class="btn btn-gold rounded-pill px-4 py-2 fw-semibold">Continue Shopping</a>
                </div>
            </div>
        </div>
    </div>
</div>
<script type="module">
    import { animate, stagger } from "https://cdn.jsdelivr.net/npm/motion@11.11.13/+esm";
    animate(".confirm-card", { opacity: [0, 1], scale: [0.95, 1] }, { duration: 0.6, easing: "ease-out" });
    animate(".confirm-icon", { opacity: [0, 1], y: [20, 0] }, { duration: 0.5, delay: 0.2, easing: "ease-out" });
    animate(".confirm-text", { opacity: [0, 1], y: [20, 0] }, { duration: 0.5, delay: stagger(0.1, { start: 0.3 }), easing: "ease-out" });
    animate(".confirm-details", { opacity: [0, 1], y: [20, 0] }, { duration: 0.5, delay: 0.6, easing: "ease-out" });
    animate(".confirm-actions", { opacity: [0, 1], y: [20, 0] }, { duration: 0.5, delay: 0.8, easing: "ease-out" });
</script>
<style>
.confirm-card, .confirm-icon, .confirm-text, .confirm-details, .confirm-actions { opacity: 0; }
</style>
{% endblock %}"""

    admin_dashboard_html = """{% extends 'base.html' %}
{% block title %}Admin Dashboard | Luxon{% endblock %}
{% block content %}
<div class="container-fluid py-4 bg-light min-vh-100">
    <div class="row g-4 px-lg-4">
        <!-- Sidebar -->
        <div class="col-lg-2">
            <div class="card border-0 shadow-sm rounded-4 h-100 admin-sidebar">
                <div class="card-body p-4">
                    <h5 class="text-gold mb-4 pb-2 border-bottom fw-bold" style="font-family: 'Playfair Display', serif;">Admin Panel</h5>
                    <ul class="nav flex-column gap-2">
                        <li class="nav-item"><a href="{{ url_for('admin.dashboard') }}" class="nav-link text-navy fw-semibold bg-light rounded-3 px-3 py-2"><i class="bi bi-speedometer2 me-2"></i> Dashboard</a></li>
                        <li class="nav-item"><a href="#orders" class="nav-link text-muted fw-semibold hover-navy rounded-3 px-3 py-2"><i class="bi bi-cart-check me-2"></i> Orders</a></li>
                        <li class="nav-item"><a href="#products" class="nav-link text-muted fw-semibold hover-navy rounded-3 px-3 py-2"><i class="bi bi-box-seam me-2"></i> Products</a></li>
                        <li class="nav-item"><a href="{{ url_for('admin.add_product') }}" class="nav-link text-muted fw-semibold hover-navy rounded-3 px-3 py-2"><i class="bi bi-plus-circle me-2"></i> Add Product</a></li>
                        <li class="nav-item mt-4"><a href="{{ url_for('main.index') }}" class="nav-link text-danger fw-semibold rounded-3 px-3 py-2"><i class="bi bi-box-arrow-left me-2"></i> Exit Admin</a></li>
                    </ul>
                </div>
            </div>
        </div>
        
        <!-- Main Content -->
        <div class="col-lg-10">
            <div class="row g-4 mb-5">
                <div class="col-md-4">
                    <div class="card border-0 shadow-sm rounded-4 bg-white h-100 stat-card">
                        <div class="card-body p-4 d-flex align-items-center">
                            <div class="bg-gold bg-opacity-10 rounded-circle d-flex align-items-center justify-content-center text-gold" style="width: 64px; height: 64px;">
                                <i class="bi bi-graph-up-arrow fs-3"></i>
                            </div>
                            <div class="ms-4">
                                <p class="text-muted small text-uppercase fw-bold mb-1 tracking-wide">Total Revenue</p>
                                <h3 class="fw-bold m-0 text-navy">₹{{ "{:,.0f}".format(total_revenue) }}</h3>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card border-0 shadow-sm rounded-4 bg-white h-100 stat-card">
                        <div class="card-body p-4 d-flex align-items-center">
                            <div class="bg-navy bg-opacity-10 rounded-circle d-flex align-items-center justify-content-center text-navy" style="width: 64px; height: 64px;">
                                <i class="bi bi-bag-check fs-3"></i>
                            </div>
                            <div class="ms-4">
                                <p class="text-muted small text-uppercase fw-bold mb-1 tracking-wide">Total Orders</p>
                                <h3 class="fw-bold m-0 text-navy">{{ total_orders }}</h3>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card border-0 shadow-sm rounded-4 bg-white h-100 stat-card">
                        <div class="card-body p-4 d-flex align-items-center">
                            <div class="bg-secondary bg-opacity-10 rounded-circle d-flex align-items-center justify-content-center text-secondary" style="width: 64px; height: 64px;">
                                <i class="bi bi-people fs-3"></i>
                            </div>
                            <div class="ms-4">
                                <p class="text-muted small text-uppercase fw-bold mb-1 tracking-wide">Customers</p>
                                <h3 class="fw-bold m-0 text-navy">{{ total_customers }}</h3>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="d-flex justify-content-between align-items-end mb-4" id="orders">
                <h4 class="fw-bold m-0" style="font-family: 'Playfair Display', serif;">Recent Orders</h4>
                <a href="#" class="text-gold text-decoration-none fw-semibold small">View All <i class="bi bi-arrow-right"></i></a>
            </div>
            
            <div class="card shadow-sm border-0 rounded-4 mb-5 overflow-hidden data-table">
                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="table-light">
                            <tr>
                                <th class="py-3 px-4 text-muted small text-uppercase fw-semibold">Order ID</th>
                                <th class="py-3 text-muted small text-uppercase fw-semibold">Date</th>
                                <th class="py-3 text-muted small text-uppercase fw-semibold">Customer</th>
                                <th class="py-3 text-muted small text-uppercase fw-semibold">Total</th>
                                <th class="py-3 px-4 text-muted small text-uppercase fw-semibold text-end">Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for order in orders %}
                            <tr>
                                <td class="py-3 px-4 fw-bold text-navy">#{{ order.id }}</td>
                                <td class="py-3 text-muted small">{{ order.created_at.strftime('%B %d, %Y') }}</td>
                                <td class="py-3 fw-semibold">{{ order.user.full_name }}</td>
                                <td class="py-3 text-gold fw-bold">₹{{ "{:,.0f}".format(order.total_amount) }}</td>
                                <td class="py-3 px-4 text-end">
                                    {% if order.payment_status == 'success' %}
                                        <span class="badge bg-success bg-opacity-10 text-success rounded-pill px-3 py-2 border border-success border-opacity-25">Paid</span>
                                    {% else %}
                                        <span class="badge bg-warning bg-opacity-10 text-warning rounded-pill px-3 py-2 border border-warning border-opacity-25">Pending</span>
                                    {% endif %}
                                </td>
                            </tr>
                            {% else %}
                            <tr><td colspan="5" class="text-center py-5 text-muted">No recent orders.</td></tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="d-flex justify-content-between align-items-end mb-4" id="products">
                <h4 class="fw-bold m-0" style="font-family: 'Playfair Display', serif;">Products Management</h4>
                <a href="{{ url_for('admin.add_product') }}" class="btn btn-navy rounded-pill px-4 py-2 fw-semibold shadow-sm"><i class="bi bi-plus-lg me-2"></i> Add Product</a>
            </div>
            
            <div class="card shadow-sm border-0 rounded-4 overflow-hidden data-table mb-4">
                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="table-light">
                            <tr>
                                <th class="py-3 px-4 text-muted small text-uppercase fw-semibold">Item</th>
                                <th class="py-3 text-muted small text-uppercase fw-semibold">Price</th>
                                <th class="py-3 text-muted small text-uppercase fw-semibold">Stock</th>
                                <th class="py-3 text-muted small text-uppercase fw-semibold">Category</th>
                                <th class="py-3 px-4 text-muted small text-uppercase fw-semibold text-end">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for p in products %}
                            <tr>
                                <td class="py-3 px-4">
                                    <div class="d-flex align-items-center">
                                        <img src="{{ p.image_url or 'https://via.placeholder.com/50' }}" width="48" height="48" class="rounded-3 object-fit-cover shadow-sm me-3">
                                        <div>
                                            <h6 class="fw-bold text-navy mb-0 small">{{ p.name }}</h6>
                                            <small class="text-muted">{{ p.brand }}</small>
                                        </div>
                                    </div>
                                </td>
                                <td class="py-3 text-gold fw-bold">₹{{ "{:,.0f}".format(p.price) }}</td>
                                <td class="py-3">
                                    {% if p.stock > 0 %}
                                        <span class="badge bg-success bg-opacity-10 text-success rounded-pill px-2 py-1">{{ p.stock }} in stock</span>
                                    {% else %}
                                        <span class="badge bg-danger bg-opacity-10 text-danger rounded-pill px-2 py-1">Out of stock</span>
                                    {% endif %}
                                </td>
                                <td class="py-3"><span class="badge bg-light text-dark border px-2 py-1">{{ p.category.name if p.category else 'None' }}</span></td>
                                <td class="py-3 px-4 text-end">
                                    <button class="btn btn-sm btn-light text-primary me-2 rounded-circle shadow-sm" style="width: 32px; height: 32px;"><i class="bi bi-pencil"></i></button>
                                    <button class="btn btn-sm btn-light text-danger rounded-circle shadow-sm" style="width: 32px; height: 32px;"><i class="bi bi-trash"></i></button>
                                </td>
                            </tr>
                            {% else %}
                            <tr><td colspan="5" class="text-center py-5 text-muted">No products found.</td></tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>
<style>
    .tracking-wide { letter-spacing: 1px; }
    .hover-navy:hover { background-color: #f8f9fa; color: var(--luxon-navy) !important; }
    .admin-sidebar, .stat-card, .data-table { opacity: 0; }
</style>
<script type="module">
    import { animate, stagger } from "https://cdn.jsdelivr.net/npm/motion@11.11.13/+esm";
    animate(".admin-sidebar", { opacity: [0, 1], x: [-30, 0] }, { duration: 0.6, easing: "ease-out" });
    animate(".stat-card", { opacity: [0, 1], y: [20, 0] }, { duration: 0.5, delay: stagger(0.1, { start: 0.2 }), easing: "ease-out" });
    animate(".data-table", { opacity: [0, 1], y: [30, 0] }, { duration: 0.6, delay: stagger(0.2, { start: 0.5 }), easing: "ease-out" });
</script>
{% endblock %}"""

    paths = {
        'd:\\projects\\Luxon\\app\\templates\\auth\\login.html': login_html,
        'd:\\projects\\Luxon\\app\\templates\\auth\\register.html': register_html,
        'd:\\projects\\Luxon\\app\\templates\\shop\\order_confirmation.html': order_confirmation_html,
        'd:\\projects\\Luxon\\app\\templates\\admin\\dashboard.html': admin_dashboard_html
    }

    for path, content in paths.items():
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
            
    print("Templates successfully updated with Premium UI!")

if __name__ == '__main__':
    cleanup_ghost_orders()
    update_templates()
