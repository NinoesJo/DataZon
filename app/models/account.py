from flask import current_app as app
from decimal import Decimal

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .. import login

class Account(UserMixin):
    def __init__(self, user_id, email, password, full_name, balance, is_seller, street, city, state, zip_code, country):
        self.user_id = user_id
        self.email = email
        self.password = password
        self.full_name = full_name
        self.balance = balance
        self.is_seller = is_seller
        self.street = street
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.country = country

    @staticmethod
    @login.user_loader
    def account_get_userid(user_id):
        rows = app.db.execute('''
        SELECT user_id, email, password, full_name, balance, is_seller, street, city, state, zip_code, country
        FROM Account
        WHERE user_id = :user_id''',
        user_id = user_id)
        return Account(*rows[0]) if rows else None
    
    def get_id(self):
        return str(self.user_id)
    
    @staticmethod
    def get_by_auth(email, password):
        rows = app.db.execute("""
        SELECT user_id, email, password, full_name, balance, is_seller, street, city, state, zip_code, country
        FROM Account
        WHERE email = :email
        """, email=email)
        if not rows:  # email not found
            return None
        elif not check_password_hash(rows[0][2], password): # CHECK if rows[0][2] or rows[0][0]
            # incorrect password
            return None
        else:
            return Account(*rows[0])

    @staticmethod
    def email_exists(email):
        rows = app.db.execute("""
        SELECT email
        FROM Account
        WHERE email = :email
        """, email=email)
        return len(rows) > 0

    @staticmethod
    def register(email, password, full_name, is_seller):
        user_id = int(Account.find_max_user_id()) + 1
        try:
            rows = app.db.execute("""
            INSERT INTO Account (user_id, email, password, full_name, balance, is_seller)
            VALUES (:user_id, :email, :password, :full_name, 0, :is_seller)
            RETURNING user_id
            """,
            email=email,
            password=generate_password_hash(password),
            full_name=full_name,
            is_seller=is_seller,
            user_id=user_id)
            return Account.account_get_userid(user_id)
        except Exception as e:
            print(str(e))
            return None

    @staticmethod
    def account_balance_deposit(user_id, amount):
        try:
            # Convert the deposit amount to a Decimal for validation
            amount = Decimal(amount)
            
            # Ensure the deposit amount is positive and within allowed range
            if amount <= 0:
                return False, "Deposit amount must be greater than 0."
            if amount >= 9999999.0:
                return False, "Deposit amount must be less than 9999999."

            # Fetch the current balance to check if adding the amount will exceed the limit
            current_balance = app.db.execute('''
                SELECT balance
                FROM Account
                WHERE user_id = :user_id
            ''', user_id=user_id)[0][0]

            # Check if the new balance will exceed the allowed limit
            if current_balance + amount >= Decimal('9999999.0'):
                return False, "Deposit would exceed the maximum allowed balance of 9999999.0."

            # Perform the deposit if all checks pass
            app.db.execute('''
                UPDATE Account
                SET balance = balance + :amount
                WHERE user_id = :user_id
            ''', user_id=user_id, amount=amount)
            
            return True, "Deposit successful."
        except Exception as e:
            return False, f"Deposit failed: {e}"

    @staticmethod
    def account_balance_withdrawal(user_id, amount):
        try:
            if Decimal(amount) <= 0:
                return False, "Withdrawl amount must be greater than 0."
            rows = app.db.execute('''
            SELECT balance
            FROM Account
            WHERE user_id = :user_id''', 
            user_id = user_id)
            if not rows:
                return False, "User does not exist."
            current_balance = rows[0][0]
            if Decimal(amount) > current_balance:
                return False, "Insufficient balance."
            app.db.execute('''
            UPDATE Account
            SET balance = balance - :amount
            WHERE user_id = :user_id''', 
            user_id = user_id, 
            amount = Decimal(amount))
            return True, "Withdrawal successful."
        except Exception as e:
            return False, f"Withdrawal failed: {e}"

    @staticmethod
    def update_address(user_id, street, city, state, zip_code, country):
        try:
            if not (street and city and state and zip_code and country):
                return False, "All address fields are required."
            app.db.execute('''
            UPDATE Account
            SET street = :street, city = :city, state = :state, zip_code = :zip_code, country = :country
            WHERE user_id = :user_id''',
            user_id =user_id, 
            street = street, 
            city = city, 
            state = state, 
            zip_code = zip_code,
            country = country)
            return True, "Address updated successfully."
        except Exception as e:
            return False, f"Failed to update address: {e}"
        
    @staticmethod
    def find_max_user_id():
        rows = app.db.execute('''
        SELECT MAX(user_id) FROM Account;
        ''')
        return rows[0][0]

    @staticmethod
    def update_email(user_id, new_email):
        try:
            app.db.execute('''
            UPDATE Account
            SET email = :new_email
            WHERE user_id = :user_id''',
            user_id = user_id,
            new_email = new_email)
            return True, "Email updated successfully."
        except Exception as e:
            return False, f"Failed to update email: {e}"

    @staticmethod
    def update_name(user_id, new_name):
        try:
            rows = app.db.execute('''
            SELECT full_name
            FROM Account
            WHERE user_id = :user_id''',
            user_id = user_id)
            if not rows:
                return False, "User not found."
            current_name = rows[0][0]
            if current_name == new_name:
                return False, "The new name cannot be the same as the current name."
            app.db.execute('''
            UPDATE Account
            SET full_name = :new_name
            WHERE user_id = :user_id''',
            user_id = user_id,
            new_name = new_name)
            return True, "Name updated successfully."
        except Execption as e:
            return False, f"Failed to update name: {e}"

    @staticmethod
    def update_password(user_id, new_password):
        try:
            rows = app.db.execute('''
            SELECT password
            FROM Account
            WHERE user_id = :user_id''',
            user_id = user_id)
            if not rows:
                return False, "User not found."
            stored_password = rows[0][0]
            if check_password_hash(stored_password, new_password):
                return False, "New password cannot be the same as the current password."
            hashed_new_password = generate_password_hash(new_password)
            app.db.execute('''
            UPDATE Account
            Set password = :hashed_new_password
            WHERE user_id = :user_id''',
            user_id = user_id,
            hashed_new_password = hashed_new_password)
            return True, "Password updated successfully."
        except Exception as e:
            return False, f"Failed to update passowrd: {e}"
