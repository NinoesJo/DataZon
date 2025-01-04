from flask import Blueprint, request, render_template, redirect, url_for, jsonify, flash, app
from .models.product import Product
from .models.cart import Cart
from .models.productlisting import ProductListing
from .models.account import Account
from .models.review import Review

from flask_login import current_user, login_required

bp = Blueprint('product_controller', __name__)

def get_current_user_id():
    return current_user.get_id() if current_user.is_authenticated else None

@bp.route('/product', methods = ["GET"])
# def product():
#     top_k = request.args.get('top_k')
#     products = []
#     if top_k:
#         products = Product.product_get_topk(int(top_k))

#     return render_template('product.html', products = products)


def product():
    # Get search and filter parameters from the request
    name_query = request.args.get('name_query', '')  # Search by product name
    sort_by = request.args.get('sort_by', '')  # Sort by '' if not provided
    category_id = request.args.get('category_id', '')
    page = int(request.args.get('page', 1))
    limit = 50
    offset = (page - 1) * limit
    
    # Fetch filtered products based on search and filter criteria
    products = Product.search_and_filter(name_query=name_query, sort_by=sort_by, category_id=category_id, limit=limit, offset=offset)
    total_products = Product.get_total_products(name_query, category_id)

    total_pages = (total_products + limit - 1) // limit
    
    # Group products by category_name
    categories = {}
    for product in products:
        if product.category_name not in categories:
            categories[product.category_name] = []
        categories[product.category_name].append(product)
    
    all_categories = Product.get_all_categories()
    
    return render_template('product.html', categories=categories, name_query=name_query, sort_by=sort_by, category_id=category_id, page=page, total_pages=total_pages, all_categories=all_categories)

def index():
    name_query = request.args.get('name_query', '')
    sort_by = request.args.get('sort_by', '')
    category_id = request.args.get('category_id', None)

    # Query to get categories for the sidebar
    categories = db.session.query(Category).all()

    # Build the product query with filters
    query = db.session.query(Product, Category, ProductListing, Account).join(Category).join(ProductListing).join(Account)

    if name_query:
        query = query.filter(Product.product_name.ilike(f"%{name_query}%"))

    if category_id:
        query = query.filter(Product.category_id == category_id)

    if sort_by == 'cheapest':
        query = query.order_by(ProductListing.price.asc())
    elif sort_by == 'expensive':
        query = query.order_by(ProductListing.price.desc())
    
    
    products = query.all()

    return render_template('products.html', categories=categories, products=products)


@bp.route('/product/<int:product_id>', methods=["GET"])
def product_detail(product_id):
    get_count = request.args.get('get_count', 15)  # Default to showing 15 results
    order_by = request.args.get('sort_type', 'datetime')
    current_user_id = get_current_user_id()  # Safely get the current user ID

    # Fetch product details based on product_id
    product = Product.get_product_by_id(product_id)

    # Check if the product exists
    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for('product_controller.product'))

    # Find the name of the product category via table lookup
    category_name = Product.get_category_name(product.category_id)[0]

    # Fetch all available listings for this product
    listings = ProductListing.get_listings_by_product_id(product_id)

    # Find average rating of each listing's seller
    seller_ratings = []
    if listings:
        for listing in listings:
            seller_ratings.append((listing, Review.get_average_rating_for_seller(listing.seller_id)))

    # Fetch filtered reviews for the product
    reviews_with_upvote_status = []
    product_reviews = Review.review_get_productid(product_id, int(get_count), order_by)

    # Get the upvote status and reviewer name for each review
    for review in product_reviews:
        has_upvoted = False
        if current_user_id:  # Check if the user is authenticated before fetching upvote status
            has_upvoted = Review.check_if_upvoted(current_user_id, review.user_id, review.reviewed_id, review.review_type)
        reviewer_name = Account.account_get_userid(review.user_id).full_name
        reviews_with_upvote_status.append((review, has_upvoted, reviewer_name))

    # Calculate the average rating using all reviews
    average_rating, review_count = Review.get_average_rating_for_product(product_id)

    # Check if user is eligible to leave a review
    if current_user.is_authenticated:

        can_create_review = Review.can_leave_new_product_review(current_user_id, product_id)
        
        # Return current user's existing review of product, if exists
        user_has_review = Review.product_review_exists(current_user_id, product_id)
        if user_has_review:
            existing_review = Review.get_product_review(current_user_id, product_id)
        else:
            existing_review = None

        if current_user.is_seller:
            user_listing = ProductListing.get_single_listing(product_id, current_user.get_id())
            user_has_listing = user_listing is not None
        else:
            user_has_listing = False

    else:
        can_create_review = False
        user_has_review = False
        existing_review = None
        user_has_listing = False

    

    # Render product detail page
    return render_template('product_detail.html', 
        product=product,
        product_id=product_id,
        listings=listings,
        seller_ratings=seller_ratings,
        product_reviews=reviews_with_upvote_status,
        get_count=get_count,
        order_by=order_by,
        category_name=category_name,
        average_rating=average_rating,
        review_count=review_count,
        current_user_id=current_user_id,
        user_has_review=user_has_review,
        can_create_review=can_create_review,
        existing_review=existing_review,
        user_has_listing=user_has_listing)


# Route for adding a new review or updating an existing one.
@bp.route('/product/<int:product_id>/add_review', methods=['POST'])
@login_required
def add_or_update_review(product_id):
    # Check if the user is authenticated and retrieve user_id
    user_id = current_user.get_id()

    # Get form data
    rating = request.form.get('rating')
    title = request.form.get('title')
    description = request.form.get('content')

    # Check if all required fields are provided
    if not rating or not title or not description:
        flash("All fields are required to submit a review.", "danger")
        return redirect(url_for('product_controller.product_detail', product_id=product_id))
    
    # Validate the length of title and description
    if len(title) > 255:
        flash("Title cannot exceed 255 characters.", "danger")
        return redirect(url_for('product_controller.product_detail', product_id=product_id))
    
    if len(description) > 2500:
        flash("Description cannot exceed 2500 characters.", "danger")
        return redirect(url_for('product_controller.product_detail', product_id=product_id))

    try:
        # Check if a review already exists for this user and product
        existing_review = Review.get_product_review(user_id=user_id, product_id=product_id)
        
        if existing_review:
            # Update the existing review
            Review.update_product_review(user_id=user_id, product_id=product_id, new_rating=rating, new_title=title, new_description=description)
            flash("Review updated successfully!", "success")
        else:
            # Create a new review
            Review.create_product_review(user_id=user_id, product_id=product_id, rating=rating, title=title, description=description)
            flash("Review added successfully!", "success")

    except Exception as e:
        # If there's an issue during insertion or update
        flash(f"Error adding or updating review: {str(e)}", "danger")

    # Redirect back to the product's review page
    return redirect(url_for('product_controller.product_detail', product_id=product_id))


# Route for deleting an existing review.
@bp.route('/product/<int:product_id>/delete_review', methods=['POST'])
@login_required
def delete_review(product_id):
    # Check if the user is authenticated and retrieve user_id
    user_id = current_user.get_id()

    try:
        # Delete the review from the database
        Review.delete_product_review(user_id=user_id, product_id=product_id)
        flash("Review deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting review: {str(e)}", "danger")

    # Redirect back to the product's review page
    return redirect(url_for('product_controller.product_detail', product_id=product_id))


@bp.route('/product/add_to_cart', methods=["POST"])
def add_to_cart():
    user_id = request.form.get('user_id')
    product_id = request.form.get('product_id')
    seller_id = request.form.get('seller_id')
    quantity = request.form.get('quantity')
    next_url = request.form.get('next', url_for('product_controller.product'))
    success, message = Cart.add_cart_item(int(user_id), int(product_id), int(seller_id), int(quantity))
    if success:
        flash(message, "success")
    else:
        flash(message, "danger")
    return redirect(next_url)
