from flask import current_app as app

class Ordersummary:
    def __init__(self, order_id, user_id, total_cost, item_quantity, datetime_placed):
        self.order_id = order_id
        self.user_id = user_id
        self.total_cost = total_cost
        self.item_quantity = item_quantity
        self.datetime_placed = datetime_placed
        
    @staticmethod
    def ordersummary_get_userid(user_id, sort_by = 'recent'):
        sort_column = {
            'recent': 'datetime_placed DESC',
            'oldest': 'datetime_placed ASC',
            'most_costly': 'total_cost DESC',
            'least_costly': 'total_cost ASC',
            'most_items': 'item_quantity DESC',
            'least_items': 'item_quantity ASC'
        }.get(sort_by, 'datetime_placed DESC')
        rows = app.db.execute(f'''
        SELECT order_id, user_id, total_cost, item_quantity, datetime_placed
        FROM OrderSummary
        WHERE user_id = :user_id
        ORDER BY {sort_column}''',
        user_id = user_id)
        return [Ordersummary(*row) for row in rows] if rows else []

    @staticmethod
    def ordersummary_getall():
        rows = app.db.execute('''
        SELECT order_id, user_id, total_cost, item_quantity, datetime_placed
        FROM OrderSummary
        ORDER BY datetime_placed DESC''')
        return [Ordersummary(*row) for row in rows] if rows else []
 