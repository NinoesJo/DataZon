from flask import current_app as app

class Product:
    def __init__(self, product_id, category_id, category_name, product_name, product_description, seller_id, seller_name, price, image_url):
        self.product_id = product_id
        self.category_id = category_id
        self.category_name = category_name
        self.product_name = product_name
        self.product_description = product_description
        self.seller_id = seller_id
        self.seller_name = seller_name
        self.price = price
        self.image_url = image_url

    @staticmethod
    def product_get_topk(top_k):
        rows = app.db.execute('''
        SELECT P.product_id, P.category_id, C.category_name, P.product_name, P.product_description, PL.seller_id, A.full_name AS seller_name, PL.price, P.image_url
        FROM Product P
        JOIN Category C ON P.category_id = C.category_id
        JOIN ProductListing PL ON P.product_id = PL.product_id
        JOIN Account A ON PL.seller_id = A.user_id
        ORDER BY PL.price DESC
        LIMIT :top_k''',
        top_k = top_k)
        return [Product(*row) for row in rows] if rows else []

    @staticmethod
    def product_getall():
        rows = app.db.execute('''
        SELECT P.product_id, P.category_id, C.category_name, P.product_name, P.product_description, PL.seller_id, A.full_name AS seller_name, PL.price, P.image_url
        FROM Product P
        JOIN Category C ON P.category_id = C.category_id
        JOIN ProductListing PL ON P.product_id = PL.product_id
        JOIN Account A ON PL.seller_id = A.user_id''')
        return [Product(*row) for row in rows] if rows else []
    
    @staticmethod
    def get_product_by_seller(seller_id):
        rows = app.db.execute('''
        SELECT P.product_id, P.category_id, C.category_name, P.product_name, P.product_description, PL.seller_id, A.full_name AS seller_name, PL.price, P.image_url
        FROM Product P
        JOIN Category C ON P.category_id = C.category_id
        JOIN ProductListing PL ON P.product_id = PL.product_id
        JOIN Account A ON PL.seller_id = A.user_id
        WHERE PL.seller_id = :seller_id''',
        seller_id=seller_id)
        return [Product(*row) for row in rows] if rows else []

    @staticmethod
    def get_product_by_id(product_id):
        rows = app.db.execute('''
        SELECT P.product_id, P.category_id, NULL, P.product_name, P.product_description, NULL, NULL, NULL, P.image_url
        FROM Product P
        WHERE P.product_id = :product_id
        ''', product_id=product_id)
        return Product(*rows[0]) if rows else None
    
    @staticmethod
    def get_product_by_name(product_title):     # Retrieve first product with name
        product_id = app.db.execute('''
        SELECT P.product_id
        FROM Product P
        WHERE P.product_name = :product_title
        ''', product_title=product_title)
        return Product.get_product_by_id(product_id[0][0]) if product_id else None
    
    @staticmethod
    def get_products_by_name(product_title):    # Retrieve all products with name
        # Execute the query to fetch all products with the given name
        products = app.db.execute('''
            SELECT P.product_id
            FROM Product P
            WHERE P.product_name = :product_title
        ''', product_title=product_title)

        # Create a list of Product objects by fetching details for each product_id
        product_list = [Product.get_product_by_id(product['product_id']) for product in products]

        return product_list if product_list else None
    
    @staticmethod
    def get_category_name(category_id):
        rows = app.db.execute('''
        SELECT category_name
        FROM Category
        WHERE category_id = :category_id
        ''', category_id=category_id)
        return rows[0] if rows else None

    @staticmethod
    def get_total_products(name_query=None, category_id=None):
        query = '''
        SELECT COUNT(*)
        FROM Product P
        JOIN ProductListing PL ON P.product_id = PL.product_id
        '''
        filters = []
        if name_query:
            filters.append("LOWER(P.product_name) LIKE LOWER(:name_query)")
        if category_id:
            filters.append("P.category_id = :category_id")
        if filters:
            query += "WHERE " + " AND ".join(filters)
        rows = app.db.execute(query, name_query=f"%{name_query}%", category_id=category_id)
        return rows[0][0] if rows else 0
    
    @staticmethod
    def create_product(category_id, product_name, product_description, image_url):
        product_id = int(Product.find_max_product_id()) + 1
        try:
            app.db.execute('''
            INSERT INTO Product (product_id, category_id, product_name, product_description, image_url)
            VALUES (:product_id, :category_id, :product_name, :product_description, :image_url)
            ''',
            product_id=product_id, category_id=category_id, product_name=product_name,
            product_description=product_description, image_url=image_url)

            return Product.get_product_by_id(product_id)
        except Exception as e:
            print(str(e))
            return None

    @staticmethod
    def search_and_filter(name_query=None, sort_by="recent", category_id=None, limit=None, offset=None):
        # Build the base query
        query = '''
        SELECT P.product_id, P.category_id, C.category_name, P.product_name, P.product_description, PL.seller_id, A.full_name AS seller_name, PL.price, P.image_url
        FROM Product P
        JOIN Category C ON P.category_id = C.category_id
        JOIN ProductListing PL ON P.product_id = PL.product_id
        JOIN Account A ON PL.seller_id = A.user_id
        '''

        filters = []
        if name_query:
            filters.append("LOWER(P.product_name) LIKE LOWER(:name_query)")
        if category_id:
            filters.append("P.category_id = :category_id")
        if filters:
            query += "WHERE " + " AND ".join(filters)

        if sort_by == "cheapest":
            query += " ORDER BY PL.price ASC "
        elif sort_by == "expensive":
            query += " ORDER BY PL.price DESC "
        else:
            query += " ORDER BY P.product_name ASC "
        
        if limit:
            query += "LIMIT :limit OFFSET :offset"

         # Add filtering for cheapest or most expensive
        #if sort_by == "cheapest":
        #    query += "AND PL.price = (SELECT MIN(price) FROM ProductListing PL2 WHERE PL2.product_id = PL.product_id) "
        #elif sort_by == "expensive":
        #    query += "AND PL.price = (SELECT MAX(price) FROM ProductListing PL2 WHERE PL2.product_id = PL.product_id) "

    # Optionally add sorting (e.g., by price or most recent)
    
        #elif sort_by == "cheapest":
        #    query += "ORDER BY PL.price ASC "
        #elif sort_by == "expensive":
        #    query += "ORDER BY PL.price DESC "
        #elif not sort_by:  # This means 'sort_by' is either blank or None
        #    query += "ORDER BY P.product_name ASC"  # Or any default sorting you prefer
        # Limit results if top_k is specified
        #if top_k:
        #    query += "LIMIT :top_k"

        # Execute query with parameters
        rows = app.db.execute(query, name_query=f"%{name_query}%", category_id=category_id, limit=limit, offset=offset)

        return [Product(*row) for row in rows] if rows else []

    @staticmethod
    def get_all_categories():
        rows = app.db.execute('''
        SELECT category_id, category_name
        FROM Category
        ORDER BY category_name ASC''')
        return rows
        
    @staticmethod
    def find_max_product_id():
        rows = app.db.execute('''
        SELECT MAX(product_id) FROM Product;
        ''')
        return rows[0][0]
