from flask import Blueprint, request, render_template, jsonify, redirect, url_for, flash
from .models.review import Review
from .models.account import Account
from .models.product import Product
from . import limiter  # Import limiter from the __init__.py module

from flask_login import current_user, login_required

bp = Blueprint('review_controller', __name__)

# TODO: Replace with function which fetches currently logged-in user id
def get_current_user_id():
    if current_user.is_authenticated:
        return current_user.get_id()
    else:
        return None

# @bp.route('/social', methods=["GET"])
# def review():
#     user_id = request.args.get('user_id')
#     get_count = request.args.get('get_count')
#     order_by = request.args.get('sort_type')
#     current_user_id = get_current_user_id() # TODO: REPLACE WITH the method to get the current logged-in user’s ID

#     reviews_with_upvote_status = get_reviews_with_upvote_status(user_id, get_count, order_by, current_user_id)

#     return render_template('review.html', reviews=reviews_with_upvote_status)

def get_reviews_with_upvote_status(user_id, get_count, order_by, current_user_id):
    reviews_with_upvote_status = []
    if user_id and get_count and order_by:
        reviews = Review.review_get_userid(int(user_id), int(get_count), order_by)

        # Get the full name for each reviewer and check if the current user has upvoted each review
        for review in reviews:
            reviewer_account = Account.account_get_userid(review.user_id)
            reviewer_name = reviewer_account.full_name if reviewer_account else "Unknown"
            # Append the review, along with whether the user has upvoted it and the reviewer's name
            has_upvoted = Review.check_if_upvoted(user_id, review.user_id, review.reviewed_id, review.review_type)
            reviews_with_upvote_status.append((review, has_upvoted, reviewer_name))

    return reviews_with_upvote_status


# Specific social page for each user, with filtering options.
@bp.route('/social/<int:user_id>', methods=["GET"])
def review(user_id):
    get_count = request.args.get('get_count', 15)  # Default to showing 15 results
    order_by = request.args.get('sort_type', 'datetime')
    current_user_id = get_current_user_id()  # Replace this with the method to get the current logged-in user’s ID

    reviews_with_upvote_status = []
    reviewer_name = None
    account_exists = False

    # Get account information for the reviewer
    reviewer_account = Account.account_get_userid(user_id)
    if reviewer_account:
        account_exists = True
        reviewer_name = reviewer_account.full_name

        # Get user reviews
        reviews = Review.review_get_userid(user_id, int(get_count), order_by)
        
        # Get the upvote status for each review
        for review in reviews:
            has_upvoted = Review.check_if_upvoted(current_user_id, review.user_id, review.reviewed_id, review.review_type)
            reviews_with_upvote_status.append((review, has_upvoted, reviewer_name))

    return render_template(
        'review.html', 
        reviews=reviews_with_upvote_status, 
        reviewer_name=reviewer_name,
        user_id=user_id, 
        account_exists=account_exists
    )

# Endpoint for upvoting
@bp.route('/social/upvote', methods=["POST"])
@login_required  # Ensure user must be logged in to upvote
@limiter.limit("100 per minute")  # Limit to 120 requests per minute per IP
def add_upvote():
    data = request.get_json()
    reviewer_id = data.get('reviewer_id')
    reviewed_id = data.get('reviewed_id')
    review_type = data.get('review_type')
    upvoter_id = get_current_user_id()

    if reviewer_id and reviewed_id and review_type:
        Review.check_then_add_upvote(upvoter_id, reviewer_id, reviewed_id, review_type)
        return jsonify(success=True, message="Upvote added"), 200
    return jsonify(success=False, message="Invalid data"), 400

# Endpoint for removing an upvote
@bp.route('/social/remove_upvote', methods=["POST"])
@login_required  # Ensure user must be logged in to remove upvote
@limiter.limit("100 per minute")  # Limit to 1 requests per minute per IP
def remove_upvote():
    data = request.get_json()
    reviewer_id = data.get('reviewer_id')
    reviewed_id = data.get('reviewed_id')
    review_type = data.get('review_type')
    upvoter_id = get_current_user_id()

    if reviewer_id and reviewed_id and review_type:
        Review.check_then_remove_upvote(upvoter_id, reviewer_id, reviewed_id, review_type)
        return jsonify(success=True, message="Upvote removed"), 200
    return jsonify(success=False, message="Invalid data"), 400


@bp.route('/seller/<int:seller_id>', methods=["GET"])
def seller_details(seller_id):
    get_count = request.args.get('get_count', 5)  # Default to showing 10 results
    order_by = request.args.get('sort_type', 'datetime')
    current_user_id = get_current_user_id()  # Replace this with the method to get the current logged-in user’s ID

    reviews_with_upvote_status = []
    seller_name = None
    is_seller = False
    average_rating = None
    review_count = None
    can_create_review = False
    user_has_review = None
    existing_review = None
    seller_products = None

    # Get account information for the seller
    seller_account = Account.account_get_userid(seller_id)
    if seller_account:
        is_seller = seller_account.is_seller
        seller_name = seller_account.full_name
        seller_id=seller_account.user_id

        if is_seller:
            # Get reviews to be displayed (limited by get_count)
            reviews = Review.review_get_sellerid(seller_id, int(get_count), order_by)

            # Calculate the average rating using all reviews
            average_rating, review_count = Review.get_average_rating_for_seller(seller_id)

            # Prepare review data with upvote status
            for review in reviews:
                has_upvoted = Review.check_if_upvoted(current_user_id, review.user_id, review.reviewed_id, review.review_type)
                reviewer_name = Account.account_get_userid(review.user_id).full_name
                reviews_with_upvote_status.append((review, has_upvoted, reviewer_name))

            # Check if user is eligible to leave a review
            if current_user.is_authenticated:
                can_create_review = Review.can_leave_new_seller_review(current_user_id, seller_id)

            # Return current user's existing review of seller, if exists
            user_has_review = Review.seller_review_exists(current_user_id, seller_id)
            if user_has_review:
                existing_review = Review.get_seller_review(current_user_id, seller_id)

            # Retrieve products sold by this seller
            seller_products = Product.get_product_by_seller(seller_id)

    return render_template(
        'seller.html',
        reviews=reviews_with_upvote_status,
        seller_name=seller_name,
        seller_id=seller_id,
        is_seller=is_seller,
        average_rating=average_rating,
        review_count=review_count,
        can_create_review=can_create_review,
        user_has_review=user_has_review,
        existing_review=existing_review,
        seller_products=seller_products
    )


# Route for adding a new review or updating an existing one.
@bp.route('/seller/<int:seller_id>/add_review', methods=['POST'])
@login_required
def add_or_update_review(seller_id):
    # Check if the user is authenticated and retrieve user_id
    user_id = current_user.get_id()

    # Get form data
    rating = request.form.get('rating')
    title = request.form.get('title')
    description = request.form.get('content')

    # Check if all required fields are provided
    if not rating or not title or not description:
        flash("All fields are required to submit a review.", "danger")
        return redirect(url_for('review_controller.seller_details', seller_id=seller_id))
    
    # Validate the length of title and description
    if len(title) > 255:
        flash("Title cannot exceed 255 characters.", "danger")
        return redirect(url_for('review_controller.seller_details', seller_id=seller_id))
    
    if len(description) > 2500:
        flash("Description cannot exceed 2500 characters.", "danger")
        return redirect(url_for('review_controller.seller_details', seller_id=seller_id))

    try:
        # Check if a review already exists for this user and seller
        existing_review = Review.get_seller_review(user_id=user_id, seller_id=seller_id)
        
        if existing_review:
            # Update the existing review
            Review.update_seller_review(user_id=user_id, seller_id=seller_id, new_rating=rating, new_title=title, new_description=description)
            flash("Review updated successfully!", "success")
        else:
            # Create a new review
            Review.create_seller_review(user_id=user_id, seller_id=seller_id, rating=rating, title=title, description=description)
            flash("Review added successfully!", "success")

    except Exception as e:
        # If there's an issue during insertion or update
        flash(f"Error adding or updating review: {str(e)}", "danger")

    # Redirect back to the seller's review page
    return redirect(url_for('review_controller.seller_details', seller_id=seller_id))


# Route for deleting an existing review.
@bp.route('/seller/<int:seller_id>/delete_review', methods=['POST'])
@login_required
def delete_review(seller_id):
    # Check if the user is authenticated and retrieve user_id
    user_id = current_user.get_id()

    try:
        # Delete the review from the database
        Review.delete_seller_review(user_id=user_id, seller_id=seller_id)
        flash("Review deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting review: {str(e)}", "danger")

    # Redirect back to the seller's review page
    return redirect(url_for('review_controller.seller_details', seller_id=seller_id))
