from flask import current_app as app

class Inventory:
    def __init__(self, product_id, product_name, product_description, seller_id, price, inventory_count):
        self.product_id = product_id
        self.product_name = product_name
        self.product_description = product_description
        self.seller_id = seller_id
        self.price = price
        self.inventory_count = inventory_count

    @staticmethod
    def inventory_get_sellerid(seller_id):
        rows = app.db.execute('''
        SELECT PL.product_id, P.product_name, P.product_description, PL.seller_id, PL.price, PL.inventory_count
        FROM ProductListing PL
        JOIN Product P ON PL.product_id = P.product_id
        WHERE PL.seller_id = :seller_id''',
        seller_id = seller_id)
        return [Inventory(*row) for row in rows] if rows else []

    @staticmethod
    def inventory_getall():
        rows = app.db.execute('''
        SELECT PL.product_id, P.product_name, P.product_description, PL.seller_id, PL.price, PL.inventory_count
        FROM ProductListing PL
        JOIN Product P ON PL.product_id = P.product_id''')
        return [Inventory(*row) for row in rows] if rows else []
