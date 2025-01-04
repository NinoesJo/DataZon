from flask import current_app as app

class Category:
    def __init__(self, category_id, category_name):
        self.category_id = category_id
        self.category_name = category_name

    @staticmethod
    def category_getall():
        rows = app.db.execute('''
        SELECT category_id, category_name
        FROM Category''')
        return [Category(*row) for row in rows] if rows else None
    
    @staticmethod
    def get_category_name(category_id):
        rows = app.db.execute('''
        SELECT category_name
        FROM Category
        WHERE category_id = :category_id
        ''', category_id=category_id)
        return rows[0] if rows else None
