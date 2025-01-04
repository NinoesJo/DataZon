from flask import current_app as app

class Cart:
    def __init__(self, user_id, product_id, seller_id, product_name, seller_name, product_description, quantity, price, saved_for_later):
        self.user_id = user_id
        self.product_id = product_id
        self.seller_id = seller_id
        self.product_name = product_name
        self.seller_name = seller_name
        self.product_description = product_description
        self.quantity = quantity
        self.price = price
        self.saved_for_later = saved_for_later

    @staticmethod
    def cart_get_userid(user_id):
        rows = app.db.execute('''
        SELECT C.user_id, C.product_id, C.seller_id, P.product_name, A.full_name AS seller_name, P.product_description, C.quantity, PL.price, C.saved_for_later
        FROM CartItem C
        JOIN Product P ON C.product_id = P.product_id
        JOIN Account A ON C.seller_id = A.user_id
        JOIN ProductListing PL ON C.product_id = PL.product_id AND C.seller_id = PL.seller_id
        WHERE C.user_id = :user_id''',
        user_id = user_id)
        return [Cart(*row) for row in rows] if rows else []

    @staticmethod
    def cart_getall():
        rows = app.db.execute('''
        SELECT C.user_id, C.product_id, C.seller_id, P.product_name, A.full_name AS seller_name, P.product_description, C.quantity, PL.price, C.saved_for_later
        FROM CartItem C
        JOIN Product P ON C.product_id = P.product_id
        JOIN Account A ON C.seller_id = A.user_id
        JOIN ProductListing PL ON C.product_id = PL.product_id AND C.seller_id = PL.seller_id''')
        return [Cart(*row) for row in rows] if rows else []

    @staticmethod
    def update_SFL_status(user_id, product_id, seller_id):
        app.db.execute('''
        UPDATE CartItem
        SET saved_for_later = NOT saved_for_later
        WHERE user_id = :user_id AND product_id = :product_id AND seller_id = :seller_id''',
        user_id = user_id,
        product_id = product_id,
        seller_id = seller_id)
        return

    @staticmethod
    def delete_cart_item(user_id, product_id, seller_id):
        app.db.execute('''
        DELETE FROM CartItem
        WHERE user_id = :user_id AND product_id = :product_id AND seller_id = :seller_id''',
        user_id = user_id,
        product_id = product_id,
        seller_id = seller_id)
        return

    @staticmethod
    def update_item_quantity(user_id, product_id, seller_id, updated_quantity):
        rows = app.db.execute('''
        SELECT PL.inventory_count
        FROM ProductListing PL
        WHERE PL.product_id = :product_id AND PL.seller_id = :seller_id''',
        product_id=product_id,
        seller_id=seller_id)
        if not rows:
            return False, "Invalid product or seller."
        inventory_count = rows[0][0]
        if updated_quantity <= 0:
            return False, "Quantity must be greater than 0."
        elif updated_quantity > inventory_count:
            return False, f"Quantity exceeds inventory limit of {inventory_count}."
        app.db.execute('''
        UPDATE CartItem
        SET quantity = :updated_quantity
        WHERE user_id = :user_id AND product_id = :product_id AND seller_id = :seller_id''',
        user_id=user_id,
        product_id=product_id,
        seller_id=seller_id,
        updated_quantity=updated_quantity) 
        return True, "Quantity updated successfully."

    @staticmethod
    def cart_checkout(user_id):
        rows = app.db.execute('''
        SELECT C.user_id, C.product_id, C.seller_id, P.product_name, A.full_name AS seller_name, P.product_description, C.quantity, PL.price, C.saved_for_later
        FROM CartItem C
        JOIN Product P ON C.product_id = P.product_id
        JOIN Account A ON C.seller_id = A.user_id
        JOIN ProductListing PL ON C.product_id = PL.product_id AND C.seller_id = PL.seller_id
        WHERE C.user_id = :user_id AND saved_for_later = False''',
        user_id = user_id)
        return [Cart(*row) for row in rows] if rows else []

    @staticmethod
    def checkout_process(user_id, checkout_items, user_balance):
        total_cost = sum(item.price * item.quantity for item in checkout_items)
        for item in checkout_items:
            rows = app.db.execute('''
            SELECT inventory_count
            FROM ProductListing
            WHERE product_id = :product_id AND seller_id = :seller_id''', 
            product_id = item.product_id, 
            seller_id = item.seller_id)
            if not rows:
                return False, f"Insufficient inventory for product: {item.product_name}."
            if rows[0][0] < item.quantity:
                return False, f"Insufficient inventory for product: {item.product_name}. ({rows[0][0]})"
        if total_cost > user_balance:
            return False, f"Insufficient balance to complete the purchase. (${user_balance})"
        return True, "Validation passed."

    @staticmethod
    def sync_order_id_sequence():
        try:
            max_order_id = app.db.execute('''
            SELECT MAX(order_id)
            FROM OrderSummary''')[0][0]
            if max_order_id is None:
                max_order_id = 0
            app.db.execute('''
            SELECT setval('OrderSummary_order_id_seq', :max_order_id)''', 
            max_order_id = max_order_id)
        except Exception as e:
            print(f"Failed to sync order_id sequence: {e}")

    @staticmethod
    def create_order(user_id, checkout_items):
        total_cost = sum(item.price * item.quantity for item in checkout_items)
        total_items = sum(item.quantity for item in checkout_items) 
        try:
            Cart.sync_order_id_sequence()
            order_id = app.db.execute('''
            INSERT INTO OrderSummary (user_id, total_cost, item_quantity, datetime_placed)
            VALUES (:user_id, :total_cost, :item_quantity, CURRENT_TIMESTAMP)
            RETURNING order_id, datetime_placed''', 
            user_id = user_id, 
            total_cost = total_cost, 
            item_quantity = total_items)[0]
            datetime_placed = order_id[1]
            order_id = order_id[0]
            for item in checkout_items:
                app.db.execute('''
                INSERT INTO OrderItem (order_id, product_id, seller_id, quantity, quantity_price, is_fulfilled)
                VALUES (:order_id, :product_id, :seller_id, :quantity, :quantity_price, :is_fulfilled)''', 
                order_id = order_id, 
                product_id = item.product_id, 
                seller_id = item.seller_id,
                quantity = item.quantity, 
                quantity_price = item.price * item.quantity, 
                is_fulfilled = False)
                app.db.execute('''
                UPDATE ProductListing
                SET inventory_count = inventory_count - :quantity
                WHERE product_id = :product_id AND seller_id = :seller_id''', 
                product_id = item.product_id, 
                seller_id = item.seller_id, 
                quantity = item.quantity)
                seller_earning = item.quantity * item.price
                app.db.execute('''
                UPDATE Account
                SET balance = balance + :earning
                WHERE user_id = :seller_id''', 
                earning = seller_earning, 
                seller_id = item.seller_id)
            app.db.execute('''
            UPDATE Account
            SET balance = balance - :total_cost
            WHERE user_id = :user_id''', 
            total_cost = total_cost,
            user_id = user_id)
            app.db.execute('''
            DELETE FROM CartItem
            WHERE user_id = :user_id AND saved_for_later = False''', 
            user_id = user_id)
            return {"order_id": order_id, "total_cost": total_cost, "item_quantity": total_items, "datetime_placed": datetime_placed}, checkout_items
        except Exception as e:
            print(f"Error during order creation: {e}")
            return None, None

    @staticmethod
    def add_cart_item(user_id, product_id, seller_id, quantity):
        user_exists = app.db.execute('''
        SELECT *
        FROM Account
        WHERE user_id = :user_id''', 
        user_id = user_id)
        if not user_exists:
            return False, "User ID does not exist."
        if quantity <= 0:
            return False, "Quantity must be greater than 0."
        if user_id == seller_id:
            return False, "Sellers cannot add their own item that they are selling into the cart."
        rows = app.db.execute('''
        SELECT PL.inventory_count
        FROM ProductListing PL
        WHERE PL.product_id = :product_id AND PL.seller_id = :seller_id''',
        product_id = product_id,
        seller_id = seller_id)
        if not rows:
            return False, "Product or seller does not exist."
        inventory_count = rows[0][0]
        if quantity > inventory_count:
            return False, f"Requested quantity exceeds available inventory ({inventory_count})."
        existing_rows = app.db.execute('''
        SELECT *
        FROM CartItem
        WHERE user_id = :user_id AND product_id = :product_id AND seller_id = :seller_id''',
        user_id = user_id,
        product_id = product_id,
        seller_id = seller_id)
        if existing_rows:
            return False, "Product from the same seller is already in your cart."
        app.db.execute('''
        INSERT INTO CartItem (user_id, product_id, seller_id, quantity, saved_for_later)
        VALUES (:user_id, :product_id, :seller_id, :quantity, False)''',
        user_id = user_id,
        product_id = product_id,
        seller_id = seller_id,
        quantity = quantity)
        return True, f"Item successfully added to cart. ({quantity} item(s))"
