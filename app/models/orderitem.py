from flask import current_app as app

class Orderitem:
    def __init__(self, order_id, user_id, product_id, product_name, product_description, quantity, quantity_price, seller_id, seller_name, is_fulfilled):
        self.order_id = order_id
        self.user_id = user_id
        self.product_id = product_id
        self.product_name = product_name
        self.product_description = product_description
        self.quantity = quantity
        self.quantity_price = quantity_price
        self.seller_id = seller_id
        self.seller_name = seller_name
        self.is_fulfilled = is_fulfilled

    @staticmethod
    def orderitem_get_userid(user_id):
        rows = app.db.execute('''
        SELECT OS.order_id, OS.user_id, OI.product_id, P.product_name, P.product_description, OI.quantity, OI.quantity_price, OI.seller_id, A.full_name AS seller_name, OI.is_fulfilled
        FROM OrderSummary OS
        JOIN OrderItem OI ON OS.order_id = OI.order_id
        JOIN Product P ON OI.product_id = P.product_id
        JOIN Account A ON OI.seller_id = A.user_id
        WHERE OS.user_id = :user_id''',
        user_id = user_id)
        return [Orderitem(*row) for row in rows] if rows else []

    @staticmethod
    def orderitem_getall():
        rows = app.db.execute('''
        SELECT OS.order_id, OS.user_id, OI.product_id, P.product_name, P.product_description, OI.quantity, OI.quantity_price, OI.seller_id, A.full_name AS seller_name, OI.is_fulfilled
        FROM OrderSummary OS
        JOIN OrderItem OI ON OS.order_id = OI.order_id
        JOIN Product P ON OI.product_id = P.product_id
        JOIN Account A ON OI.seller_id = A.user_id''')
        return [Order(*row) for row in rows] if rows else []

    @staticmethod
    def get_orderitems_by_seller(seller_id, sort_by = 'recent', fulfillment_filter = 'all'):
        sort_column = {
            'recent': 'OS.datetime_placed DESC',
            'oldest': 'OS.datetime_placed ASC',
            'most_items': 'OI.quantity DESC',
            'least_items': 'OI.quantity ASC',
            'highest_earnings': 'OI.quantity_price DESC',
            'lowest_earnings': 'OI.quantity_price ASC'
        }.get(sort_by, 'OS.datetime_placed DESC')
        filter_condition = ''
        if fulfillment_filter == 'fulfilled':
            filter_condition = 'AND OI.is_fulfilled = TRUE'
        elif fulfillment_filter == 'not_fulfilled':
            filter_condition = 'AND OI.is_fulfilled = FALSE'
        rows = app.db.execute(f'''
            SELECT OS.order_id, OS.user_id, P.product_id, P.product_name, P.product_description, OI.quantity, OI.quantity_price, OS.datetime_placed, OI.is_fulfilled, A.full_name AS customer_name, A.street, A.city, A.state, A.zip_code, A.country
            FROM OrderItem OI
            JOIN OrderSummary OS ON OI.order_id = OS.order_id
            JOIN Product P ON OI.product_id = P.product_id
            JOIN Account A ON OS.user_id = A.user_id
            WHERE OI.seller_id = :seller_id
            {filter_condition}
            ORDER BY {sort_column}''', 
            seller_id = seller_id)
        return rows

    @staticmethod
    def fulfill_order_item(order_id, product_id, seller_id):
        try:
            rows = app.db.execute('''
                SELECT is_fulfilled
                FROM OrderItem
                WHERE order_id = :order_id AND product_id = :product_id AND seller_id = :seller_id''', 
                order_id = order_id, 
                product_id = product_id, 
                seller_id = seller_id)
            if not rows or rows[0][0]:
                return False
            app.db.execute('''
            UPDATE OrderItem
            SET is_fulfilled = TRUE
            WHERE order_id = :order_id AND product_id = :product_id AND seller_id = :seller_id''', 
            order_id = order_id, 
            product_id = product_id, 
            seller_id = seller_id)
            return True
        except Exception as e:
            print(f"Error fulfilling order item: {e}")
            return False 
