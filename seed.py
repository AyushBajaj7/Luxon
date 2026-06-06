import random
from app import create_app, db
from app.models import Category, Subcategory, Product, CartItem, Wishlist, OrderItem

app = create_app()

PRODUCTS_DATA = [
    # Watches
    {'cat': 'Fashion', 'sub': 'Watches', 'brand': 'Rolex', 'name': 'Rolex Submariner Stainless Steel', 'price': 850000, 'img': 'https://images.unsplash.com/photo-1523170335258-f5ed11844a49?w=600&auto=format&fit=crop'},
    {'cat': 'Fashion', 'sub': 'Watches', 'brand': 'Tissot', 'name': 'Tissot Classic Rose Gold Chronograph', 'price': 65000, 'img': 'https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=600&auto=format&fit=crop'},
    {'cat': 'Fashion', 'sub': 'Watches', 'brand': 'Daniel Wellington', 'name': 'Minimalist Leather Watch', 'price': 15000, 'img': 'https://images.unsplash.com/photo-1522312346375-d1a52e2b99b3?w=600&auto=format&fit=crop'},
    {'cat': 'Fashion', 'sub': 'Watches', 'brand': 'Omega', 'name': 'Omega Speedmaster Professional', 'price': 420000, 'img': 'https://images.unsplash.com/photo-1587836374828-4dbafa94cf0e?w=600&auto=format&fit=crop'},
    
    # Bags
    {'cat': 'Fashion', 'sub': 'Bags', 'brand': 'Louis Vuitton', 'name': 'Premium Black Leather Backpack', 'price': 120000, 'img': 'https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=600&auto=format&fit=crop'},
    {'cat': 'Fashion', 'sub': 'Bags', 'brand': 'Prada', 'name': 'Prada Saffiano Leather Tote', 'price': 180000, 'img': 'https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=600&auto=format&fit=crop'},
    {'cat': 'Fashion', 'sub': 'Bags', 'brand': 'Chanel', 'name': 'Chanel Classic Pink Flap Bag', 'price': 260000, 'img': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600&auto=format&fit=crop'},
    
    # Clothing
    {'cat': 'Fashion', 'sub': 'Clothing', 'brand': 'Balenciaga', 'name': 'Balenciaga Premium White Sweatshirt', 'price': 45000, 'img': 'https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=600&auto=format&fit=crop'},
    {'cat': 'Fashion', 'sub': 'Clothing', 'brand': 'Tom Ford', 'name': 'Tom Ford Tailored Navy Blue Suit', 'price': 220000, 'img': 'https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=600&auto=format&fit=crop'},
    {'cat': 'Fashion', 'sub': 'Clothing', 'brand': 'Gucci', 'name': 'Gucci Silk Floral Dress', 'price': 145000, 'img': 'https://images.unsplash.com/photo-1539008835657-9e8e9680c956?w=600&auto=format&fit=crop'},
    
    # Shoes
    {'cat': 'Fashion', 'sub': 'Shoes', 'brand': 'Christian Louboutin', 'name': 'Louboutin Floral Print Stiletto Pumps', 'price': 65000, 'img': 'https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=600&auto=format&fit=crop'},
    {'cat': 'Fashion', 'sub': 'Shoes', 'brand': 'Gucci', 'name': 'Gucci Classic White Leather Sneakers', 'price': 58000, 'img': 'https://images.unsplash.com/photo-1460353581641-37baddab0fa2?w=600&auto=format&fit=crop'},
    {'cat': 'Fashion', 'sub': 'Shoes', 'brand': 'Balenciaga', 'name': 'Balenciaga Red Designer Sneakers', 'price': 75000, 'img': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop'},
    {'cat': 'Fashion', 'sub': 'Shoes', 'brand': 'Berluti', 'name': 'Berluti Brown Leather Oxford Shoes', 'price': 85000, 'img': 'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=600&auto=format&fit=crop'},
    
    # Smartphones
    {'cat': 'Premium Tech', 'sub': 'Smartphones', 'brand': 'Apple', 'name': 'Apple iPhone X Silver 256GB', 'price': 89900, 'img': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=600&auto=format&fit=crop'},
    {'cat': 'Premium Tech', 'sub': 'Smartphones', 'brand': 'Apple', 'name': 'Apple iPhone 13 Pro Graphite', 'price': 119900, 'img': 'https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?w=600&auto=format&fit=crop'},
    {'cat': 'Premium Tech', 'sub': 'Smartphones', 'brand': 'Samsung', 'name': 'Samsung Galaxy Premium Edition', 'price': 114990, 'img': 'https://images.unsplash.com/photo-1556656793-08538906a9f8?w=600&auto=format&fit=crop'},
    
    # Laptops
    {'cat': 'Premium Tech', 'sub': 'Laptops', 'brand': 'Apple', 'name': 'Apple MacBook Pro 15-inch Space Gray', 'price': 249900, 'img': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=600&auto=format&fit=crop'},
    {'cat': 'Premium Tech', 'sub': 'Laptops', 'brand': 'Apple', 'name': 'Apple MacBook Air M2 Silver', 'price': 119900, 'img': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=600&auto=format&fit=crop'},
    {'cat': 'Premium Tech', 'sub': 'Laptops', 'brand': 'Microsoft', 'name': 'Microsoft Surface Laptop Studio', 'price': 219999, 'img': 'https://images.unsplash.com/photo-1531297484001-80022131f5a1?w=600&auto=format&fit=crop'},
    
    # Audio
    {'cat': 'Premium Tech', 'sub': 'Audio', 'brand': 'Bose', 'name': 'Bose Wireless Over-Ear Headphones', 'price': 29990, 'img': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop'},
    {'cat': 'Premium Tech', 'sub': 'Audio', 'brand': 'Sony', 'name': 'Sony Noise Cancelling Wireless Earbuds', 'price': 24900, 'img': 'https://images.unsplash.com/photo-1583394838336-acd977736f90?w=600&auto=format&fit=crop'},
    {'cat': 'Premium Tech', 'sub': 'Audio', 'brand': 'Sennheiser', 'name': 'Sennheiser Studio Reference Headphones', 'price': 39990, 'img': 'https://images.unsplash.com/photo-1545127398-14699f92334b?w=600&auto=format&fit=crop'},
    
    # Smartwatches
    {'cat': 'Premium Tech', 'sub': 'Smartwatches', 'brand': 'Apple', 'name': 'Apple Watch Series 8 Aluminum', 'price': 45900, 'img': 'https://images.unsplash.com/photo-1434493789847-2f02dc6ca35d?w=600&auto=format&fit=crop'},
    {'cat': 'Premium Tech', 'sub': 'Smartwatches', 'brand': 'Garmin', 'name': 'Garmin Minimalist Fitness Watch', 'price': 28990, 'img': 'https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=600&auto=format&fit=crop'},
    {'cat': 'Premium Tech', 'sub': 'Smartwatches', 'brand': 'Tag Heuer', 'name': 'Tag Heuer Connected Sport Edition', 'price': 145000, 'img': 'https://images.unsplash.com/photo-1546868871-af0de0ae72be?w=600&auto=format&fit=crop'},
    
    # Home Decor
    {'cat': 'Lifestyle', 'sub': 'Home Decor', 'brand': 'Baccarat', 'name': 'Baccarat Minimalist Decorative Vase', 'price': 45000, 'img': 'https://images.unsplash.com/photo-1581783342308-f792dbdd27c5?w=600&auto=format&fit=crop'},
    {'cat': 'Lifestyle', 'sub': 'Home Decor', 'brand': 'Lalique', 'name': 'Lalique Elegant Table Lamp', 'price': 92000, 'img': 'https://images.unsplash.com/photo-1506898667547-42e22a46e125?w=600&auto=format&fit=crop'},
    {'cat': 'Lifestyle', 'sub': 'Home Decor', 'brand': 'Versace Home', 'name': 'Versace Home Decorative Ceramic Piece', 'price': 65000, 'img': 'https://images.unsplash.com/photo-1544457070-4cd773b4d71e?w=600&auto=format&fit=crop'},
    
    # Fragrances
    {'cat': 'Lifestyle', 'sub': 'Fragrances', 'brand': 'Chanel', 'name': 'Chanel No.5 Eau de Parfum 100ml', 'price': 18500, 'img': 'https://images.unsplash.com/photo-1541643600914-78b084683601?w=600&auto=format&fit=crop'},
    {'cat': 'Lifestyle', 'sub': 'Fragrances', 'brand': 'Tom Ford', 'name': 'Tom Ford Signature Gold Edition 50ml', 'price': 22000, 'img': 'https://images.unsplash.com/photo-1588405748880-12d1d2a59f75?w=600&auto=format&fit=crop'},
    {'cat': 'Lifestyle', 'sub': 'Fragrances', 'brand': 'Creed', 'name': 'Creed Aventus Premium Bottle 100ml', 'price': 35000, 'img': 'https://images.unsplash.com/photo-1523293182086-7651a899d37f?w=600&auto=format&fit=crop'},
    
    # Accessories
    {'cat': 'Lifestyle', 'sub': 'Accessories', 'brand': 'Tom Ford', 'name': 'Tom Ford Aviator Sunglasses', 'price': 35000, 'img': 'https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=600&auto=format&fit=crop'},
    {'cat': 'Lifestyle', 'sub': 'Accessories', 'brand': 'Cartier', 'name': 'Cartier Diamond Ring', 'price': 480000, 'img': 'https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=600&auto=format&fit=crop'},
    {'cat': 'Lifestyle', 'sub': 'Accessories', 'brand': 'Montblanc', 'name': 'Montblanc Classic Leather Watch', 'price': 85000, 'img': 'https://images.unsplash.com/photo-1601121141461-9d6647bca1ed?w=600&auto=format&fit=crop'},
    
    # Art
    {'cat': 'Lifestyle', 'sub': 'Art', 'brand': 'Pace Gallery', 'name': 'Modernist Abstract Canvas Print', 'price': 45000, 'img': 'https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=600&auto=format&fit=crop'},
    {'cat': 'Lifestyle', 'sub': 'Art', 'brand': 'White Cube', 'name': 'Contemporary Oil Painting', 'price': 120000, 'img': 'https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?w=600&auto=format&fit=crop'},
    {'cat': 'Lifestyle', 'sub': 'Art', 'brand': 'Gagosian', 'name': 'Minimalist Gallery Print', 'price': 85000, 'img': 'https://images.unsplash.com/photo-1561214115-f2f134cc4912?w=600&auto=format&fit=crop'},
]


def seed_database():
    with app.app_context():
        print("Clearing database...")
        CartItem.query.delete()
        Wishlist.query.delete()
        OrderItem.query.delete()
        Product.query.delete()
        Subcategory.query.delete()
        Category.query.delete()
        db.session.commit()
        
        # Build category map
        cats = {}
        subcats = {}
        
        print("Creating categories & products...")
        for p in PRODUCTS_DATA:
            if p['cat'] not in cats:
                category = Category(name=p['cat'])
                db.session.add(category)
                db.session.flush()
                cats[p['cat']] = category
                
            cat_obj = cats[p['cat']]
            sub_key = f"{p['cat']}-{p['sub']}"
            
            if sub_key not in subcats:
                sub = Subcategory(name=p['sub'], category_id=cat_obj.id)
                db.session.add(sub)
                db.session.flush()
                subcats[sub_key] = sub
                
            sub_obj = subcats[sub_key]
            
            product = Product(
                name=p['name'],
                description=f"Experience the pinnacle of luxury with this piece from {p['brand']}. Crafted with uncompromising attention to detail and utilizing only the finest materials, this item represents the apex of design and engineering. A true statement of elegance.",
                price=p['price'],
                stock=random.choices([0, random.randint(1, 15)], weights=[10, 90])[0],
                brand=p['brand'],
                image_url=p['img'],
                category_id=cat_obj.id,
                subcategory_id=sub_obj.id,
                is_featured=random.choice([True, False, False])
            )
            db.session.add(product)
            
        db.session.commit()
        print(f"Successfully seeded {len(PRODUCTS_DATA)} perfectly matched luxury products without duplicates!")

if __name__ == '__main__':
    seed_database()
