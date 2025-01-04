from flask import current_app as app

class ProductListing:
    def __init__(self, product_id, seller_id, seller_name, price, inventory_count):
        self.product_id = product_id
        self.seller_id = seller_id
        self.seller_name = seller_name
        self.price = price
        self.inventory_count = inventory_count

    @staticmethod
    def get_listings_by_product_id(product_id):
        rows = app.db.execute('''
        SELECT product_id, seller_id, A.full_name, price, inventory_count
        FROM ProductListing
        JOIN Account A ON ProductListing.seller_id = A.user_id
        WHERE product_id = :product_id AND inventory_count > 0
        ORDER BY price ASC
        ''', product_id=product_id)
        
        return [ProductListing(*row) for row in rows] if rows else []
    
    @staticmethod
    def get_single_listing(product_id, seller_id):
        rows = app.db.execute('''
        SELECT product_id, seller_id, A.full_name, price, inventory_count
        FROM ProductListing
        JOIN Account A ON ProductListing.seller_id = A.user_id
        WHERE product_id = :product_id AND seller_id = :seller_id
        ORDER BY price ASC
        ''', product_id=product_id, seller_id=seller_id)
        
        return ProductListing(*rows[0]) if rows else None
    
    @staticmethod
    def create_listing(product_id, seller_id, price, inventory_count):
        check = app.db.execute('''
            SELECT COUNT(*)
            FROM ProductListing
            WHERE product_id = :product_id AND seller_id = :seller_id       
            ''', product_id=product_id, seller_id=seller_id)
        if check[0][0] == 0:
            rows = app.db.execute('''
                INSERT INTO ProductListing (product_id, seller_id, price, inventory_count)
                VALUES (:product_id, :seller_id, :price, :inventory_count)
            ''', product_id=product_id, seller_id=seller_id,
            price=price, inventory_count=inventory_count)

            return ProductListing.get_single_listing(product_id, seller_id)
        else:
            # Listing already exists, return None
            return None
        
    @staticmethod
    def update_listing(product_id, seller_id, price=None, inventory_count=None):
        if price and inventory_count is not None:
            if inventory_count is None: # update price only
                app.db.execute('''
                UPDATE ProductListing
                SET price = :price
                WHERE product_id = :product_id AND seller_id = :seller_id
                ''', product_id=product_id, seller_id=seller_id,
                price=price)
            elif price is None: # update inventory_count only
                app.db.execute('''
                UPDATE ProductListing
                SET inventory_count = :inventory_count
                WHERE product_id = :product_id AND seller_id = :seller_id
                ''', product_id=product_id, seller_id=seller_id,
                inventory_count=inventory_count)
            else: # update price and inventory_count
                app.db.execute('''
                UPDATE ProductListing
                SET price = :price, inventory_count = :inventory_count
                WHERE product_id = :product_id AND seller_id = :seller_id
                ''', product_id=product_id, seller_id=seller_id,
                price=price, inventory_count=inventory_count)
        
        return ProductListing.get_single_listing(product_id, seller_id)
    
    @staticmethod
    def delete_listing(product_id, seller_id, price=None, inventory_count=None):
        app.db.execute('''
            DELETE FROM ProductListing
            WHERE product_id = :product_id AND seller_id = :seller_id
        ''',
        product_id=product_id,
        seller_id=seller_id)
        
        return ProductListing.get_single_listing(product_id, seller_id)
