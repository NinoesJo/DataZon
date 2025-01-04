from flask import Blueprint, request, render_template, redirect, url_for, jsonify, flash, app
from flask import current_app as app
from flask_login import current_user, login_required
from markupsafe import Markup

from .models.product import Product
from .models.cart import Cart
from .models.productlisting import ProductListing
from .models.account import Account
from .models.review import Review
from .models.inventory import Inventory
from .models.category import Category
from .models.ordersummary import Ordersummary
from .models.orderitem import Orderitem

bp = Blueprint('listing_controller', __name__)

@bp.route('/seller', methods = ["GET"])
@login_required
def inventory():
    # Ensure only sellers can access this page
    if not current_user.is_seller:
        flash("Only seller accounts can acces the Seller Dashboard.", "danger")
        return redirect(url_for('account_controller.account'))  # Redirect to home page

    seller_id = current_user.get_id()
    inventories = []
    inventories = Inventory.inventory_get_sellerid(int(seller_id))

    return render_template('inventory.html', inventories=inventories, seller_id=seller_id)

@bp.route('/seller/create_listing', methods=['GET', 'POST'])
def create_listing():
    if not current_user.is_authenticated:
        flash("You need to log in to create listing.", "danger")
        return redirect(url_for('users.login'))
    # Ensure only sellers can access this page
    if not current_user.is_seller:
        flash("Only seller accounts can create product listings.", "danger")
        return redirect(url_for('index.index'))  # Redirect to home page
    
    if request.method == 'POST':
        # Handle the form submission for creating a new listing
        product_id = request.form.get('product_id')
        price = request.form.get('price')
        inventory_count = request.form.get('inventory_count')

        # Ensure all fields are provided
        if not product_id or not price or not inventory_count:
            flash("All fields are required", "danger")
            return redirect(url_for('listing_controller.create_listing'))

        # Convert and validate the fields
        try:
            price = float(price)
            inventory_count = int(inventory_count)
        except ValueError:
            flash("Price must be a valid number and inventory count must be an integer.", "danger")
            return redirect(url_for('listing_controller.create_listing'))

        # Validate price and inventory count limits
        if price <= 0 or price >= 9999999.0:
            flash("Price must be between 0.01 and 9999999.00.", "danger")
            return redirect(url_for('listing_controller.create_listing'))

        if inventory_count <= 0 or inventory_count >= 9999999:
            flash("Inventory count must be an integer greater than 0 and less than 9999999.", "danger")
            return redirect(url_for('listing_controller.create_listing'))

        # Create new listing for the current user, return listing if successful
        listing = ProductListing.create_listing(
            product_id=product_id,
            seller_id=current_user.get_id(),
            price=price,
            inventory_count=inventory_count
        )

        if listing:
            # Generate the URL for the new product page
            dashboard_url = url_for('listing_controller.inventory')
            # Flash the success message with a link to the product
            flash(Markup(f"Listing created successfully! <a href='{dashboard_url}'>View My Listings</a>"), "success")
            return redirect(url_for('listing_controller.create_listing'))
        else:
            flash("Failed to create listing. Maybe it already exists?", "danger")
            return redirect(url_for('listing_controller.create_listing'))

    else:
        # Handle the GET request to display available products
        query = request.args.get('q', '')
        products = []
        # If a query is present, fetch all (999,999,999) matching products
        if query:
            products = app.db.execute('''
                SELECT product_id, product_name 
                FROM Product
                WHERE product_name ILIKE :query
                LIMIT 999999999
            ''', query=f'%{query}%')

            if products is None:    # if no products match search term in name, search product descriptions
                products = app.db.execute('''
                    SELECT product_id, product_name 
                    FROM Product
                    WHERE product_description ILIKE :query
                    LIMIT 999999999
                ''', query=f'%{query}%')
        else:
            # Fetch all products for displaying on the page
            products = app.db.execute('''
                SELECT product_id, product_name, product_description, image_url
                FROM Product
                LIMIT 999999999
            ''')

        # Check if a product ID is provided to prefill the form
        product_id = request.args.get('product_id')
        selected_product = None
        if product_id:
            selected_product = Product.get_product_by_id(product_id)

        return render_template('createlisting.html',
                               products=products,
                               selected_product=selected_product,
                               categories=Category.category_getall())

@bp.route('/seller/update_listing', methods=['POST'])
def update_listing():
    if not current_user.is_authenticated:
        flash("You need to log in to update listing.", "danger")
        return redirect(url_for('users.login'))
    # Ensure only sellers can access this page
    if not current_user.is_seller:
        flash("Only seller accounts can update product listings.", "danger")
        return redirect(url_for('index.index'))  # Redirect to home page

    # Get form data
    product_id = request.form.get('product_id')
    price = request.form.get('price')
    inventory_count = request.form.get('inventory_count')

    if not product_id:
        flash("Product ID is required to update a listing.", "danger")
        return redirect(url_for('listing_controller.inventory'))
    
    # Convert and validate the fields
    try:
        price = float(price)
        inventory_count = int(inventory_count)
    except ValueError:
        flash("Price must be a valid number and inventory count must be an integer.", "danger")
        return redirect(url_for('listing_controller.inventory'))

    # Validate price and inventory count limits
    if price <= 0 or price >= 9999999.0:
        flash("Price must be between 0.01 and 9999999.00.", "danger")
        return redirect(url_for('listing_controller.inventory'))

    if inventory_count <= 0 or inventory_count >= 9999999:
        flash("Inventory count must be an integer greater than 0 and less than 9999999.", "danger")
        return redirect(url_for('listing_controller.inventory'))

    # Attempt to update the listing
    try:
        listing = ProductListing.update_listing(
            product_id=product_id,
            seller_id=current_user.get_id(),
            price=price,
            inventory_count=inventory_count
        )
        if listing:
            flash("Listing updated successfully!", "success")
        else:
            flash("Failed to update listing. Please check the inputs.", "danger")

    except Exception as e:
        flash(f"An error occurred while updating the listing: {e}", "danger")

    return redirect(url_for('listing_controller.inventory'))

@bp.route('/seller/delete_listing', methods=['POST'])
def delete_listing():
    if not current_user.is_authenticated:
        flash("You need to log in to delete listing.", "danger")
        return redirect(url_for('users.login'))
    # Ensure only sellers can access this page
    if not current_user.is_seller:
        flash("Only seller accounts can delete product listings.", "danger")
        return redirect(url_for('index.index'))  # Redirect to home page

    # Get product ID from request
    product_id = request.form.get('product_id')

    if not product_id:
        flash("Product ID is required to delete a listing.", "danger")
        return redirect(url_for('listing_controller.inventory'))

    # Attempt to delete the listing
    try:
        ProductListing.delete_listing(
            product_id=product_id,
            seller_id=current_user.get_id()
        )
        flash("Listing deleted successfully!", "success")
    except Exception as e:
        flash(f"An error occurred while deleting the listing: {e}", "danger")

    return redirect(url_for('listing_controller.inventory'))


@bp.route('/seller/create_new_product', methods=['POST'])
def create_new_product():
    if not current_user.is_authenticated:
        flash("You need to log in to create new products.", "danger")
        return redirect(url_for('users.login'))
    # Ensure only sellers can create products
    if not current_user.is_seller:
        flash("Only seller accounts can add new products.", "danger")
        return redirect(url_for('index.index'))  # Redirect to home page

    # Get form data
    product_title = request.form.get('product_title')
    product_description = request.form.get('product_description')
    category_id = request.form.get('category_id')
    image_url = request.form.get('image_url')
    price = request.form.get('price')
    inventory_count = request.form.get('inventory_count')

    # Validate form data
    if not (product_title and product_description and category_id and image_url and price and inventory_count):
        flash("All fields are required", "danger")
        return redirect(url_for('listing_controller.create_listing'))

    # Validate lengths
    if len(product_title) > 255 or len(product_title) < 5:
        flash("Product title must be between 5 and 255 characters.", "danger")
        return redirect(url_for('listing_controller.create_listing'))
    
    if len(product_description) > 4000:
        flash("Product description cannot exceed 4000 characters.", "danger")
        return redirect(url_for('listing_controller.create_listing'))

    if len(image_url) > 255:
        flash("Image URL cannot exceed 255 characters.", "danger")
        return redirect(url_for('listing_controller.create_listing'))
    
    # Check if the product already exists
    existing_product = Product.get_product_by_name(product_title)
    if existing_product:
        flash("A product with the same name already exists in Datazon. Please use a unique product name.", "danger")
        return redirect(url_for('listing_controller.create_listing'))

    # Insert new product into the database
    try:
        new_product = Product.create_product(
            category_id=category_id,
            product_name=product_title,
            product_description=product_description,
            image_url=image_url
        )
        
        if new_product is None:
            flash("Failed to create the new product.", "danger")
        
        # Create the product listing for the seller
        listing = ProductListing.create_listing(
            product_id=new_product.product_id,
            seller_id=current_user.get_id(),
            price=price,
            inventory_count=inventory_count
        )
        
        if listing:
            # Generate the URL for the new product page
            product_url = url_for('product_controller.product_detail', product_id=new_product.product_id)
            # Flash the success message with a link to the product
            flash(Markup(f"New product and listing created successfully! <a href='{product_url}'>View Product</a>"), "success")
        else:
            flash("Failed to create listing for the new product.", "danger")
    
    except Exception as e:
        flash(f"An error occurred while adding the product: {str(e)}", "danger")

    return redirect(url_for('listing_controller.create_listing'))

@bp.route('/seller/fulfillment', methods=["GET", "POST"])
def order_fulfillment():
    if not current_user.is_authenticated:
        flash("You need to log in to go to order fulfillment.", "danger")
        return redirect(url_for('users.login'))
    if not current_user.is_seller:
        flash("Only seller accounts can access the Order Fulfillment Dashboard.", "danger")
        return redirect(url_for('account_controller.account'))
    seller_id = current_user.get_id()
    sort_by = request.args.get('sort_by', 'recent')
    fulfillment_filter = request.args.get('filter', 'all')
    order_items = Orderitem.get_orderitems_by_seller(seller_id, sort_by, fulfillment_filter)
    return render_template('order_fulfillment.html', order_items = order_items, sort_by = sort_by, filter = fulfillment_filter)

@bp.route('/seller/fulfill_item', methods=["POST"])
def fulfill_order_item():
    if not current_user.is_authenticated:
        flash("You need to log in to go to fulfill orders.", "danger")
        return redirect(url_for('users.login'))
    if not current_user.is_seller:
        flash("Only seller accounts can fulfill order items.", "danger")
        return redirect(url_for('listing_controller.order_fulfillment'))
    order_id = request.form.get('order_id')
    product_id = request.form.get('product_id')
    if not order_id or not product_id:
        flash("Order ID and Product ID are required to fulfill an item.", "danger")
        return redirect(url_for('listing_controller.order_fulfillment'))
    try:
        success = Orderitem.fulfill_order_item(order_id, product_id, current_user.get_id())
        if success:
            flash("Order item marked as fulfilled successfully!", "success")
        else:
            flash("Failed to mark the order item as fulfilled.", "danger")
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")
    return redirect(url_for('listing_controller.order_fulfillment'))
