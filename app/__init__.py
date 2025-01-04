from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from .config import Config
from .db import DB

login = LoginManager()
login.login_view = 'users.login'

# Create the Limiter instance
limiter = Limiter(key_func=get_remote_address)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.db = DB(app)
    login.init_app(app)

    # Initialize Limiter with the app instance
    limiter.init_app(app)

    from .users import bp as user_bp
    app.register_blueprint(user_bp)

    from .index import bp as index_bp
    app.register_blueprint(index_bp)

    from .cart_controller import bp as cart_bp
    app.register_blueprint(cart_bp)

    from .order_controller import bp as order_bp
    app.register_blueprint(order_bp)

    from .inventory_controller import bp as inventory_bp
    app.register_blueprint(inventory_bp)

    from .product_controller import bp as product_bp
    app.register_blueprint(product_bp)

    from .review_controller import bp as review_bp
    app.register_blueprint(review_bp)

    from .account_controller import bp as account_bp
    app.register_blueprint(account_bp)

    from .listing_controller import bp as listing_bp
    app.register_blueprint(listing_bp)

    return app
