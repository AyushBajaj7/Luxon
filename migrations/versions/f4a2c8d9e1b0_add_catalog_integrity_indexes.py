"""Add catalog integrity indexes

Revision ID: f4a2c8d9e1b0
Revises: b8cf2199de0b
Create Date: 2026-06-06 20:45:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'f4a2c8d9e1b0'
down_revision = 'b8cf2199de0b'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        DELETE FROM cart_items a
        USING cart_items b
        WHERE a.id > b.id
          AND a.cart_id = b.cart_id
          AND a.product_id = b.product_id
    """)
    op.execute("""
        DELETE FROM wishlists a
        USING wishlists b
        WHERE a.id > b.id
          AND a.user_id = b.user_id
          AND a.product_id = b.product_id
    """)

    op.create_unique_constraint('uq_subcategories_category_name', 'subcategories', ['category_id', 'name'])
    op.create_unique_constraint('uq_cart_items_cart_product', 'cart_items', ['cart_id', 'product_id'])
    op.create_unique_constraint('uq_wishlists_user_product', 'wishlists', ['user_id', 'product_id'])

    op.create_index('ix_subcategories_category_name', 'subcategories', ['category_id', 'name'])
    op.create_index('ix_products_category_price', 'products', ['category_id', 'price'])
    op.create_index('ix_products_subcategory_price', 'products', ['subcategory_id', 'price'])
    op.create_index('ix_products_featured_created', 'products', ['is_featured', 'created_at'])
    op.create_index('ix_products_brand', 'products', ['brand'])
    op.create_index('ix_products_name', 'products', ['name'])
    op.create_index('ix_cart_items_cart_id', 'cart_items', ['cart_id'])
    op.create_index('ix_wishlists_user_id', 'wishlists', ['user_id'])
    op.create_index('ix_order_items_order_id', 'order_items', ['order_id'])
    op.create_index('ix_order_items_product_id', 'order_items', ['product_id'])
    op.create_index('ix_payments_order_id', 'payments', ['order_id'])
    op.create_index('ix_payments_status_created', 'payments', ['status', 'created_at'])


def downgrade():
    op.drop_index('ix_payments_status_created', table_name='payments')
    op.drop_index('ix_payments_order_id', table_name='payments')
    op.drop_index('ix_order_items_product_id', table_name='order_items')
    op.drop_index('ix_order_items_order_id', table_name='order_items')
    op.drop_index('ix_wishlists_user_id', table_name='wishlists')
    op.drop_index('ix_cart_items_cart_id', table_name='cart_items')
    op.drop_index('ix_products_name', table_name='products')
    op.drop_index('ix_products_brand', table_name='products')
    op.drop_index('ix_products_featured_created', table_name='products')
    op.drop_index('ix_products_subcategory_price', table_name='products')
    op.drop_index('ix_products_category_price', table_name='products')
    op.drop_index('ix_subcategories_category_name', table_name='subcategories')

    op.drop_constraint('uq_wishlists_user_product', 'wishlists', type_='unique')
    op.drop_constraint('uq_cart_items_cart_product', 'cart_items', type_='unique')
    op.drop_constraint('uq_subcategories_category_name', 'subcategories', type_='unique')
