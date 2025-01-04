from flask import Blueprint, request, render_template, redirect, url_for, jsonify, flash
from .models.account import Account
from .models.review import Review
from flask_login import current_user, login_required

bp = Blueprint('account_controller', __name__)

@bp.route('/account', methods = ["GET"])
@login_required
def account():
    user_id = None
    account_details = None
    review_details = None
    user_reviews = []

    if current_user.is_authenticated:
        user_id = current_user.get_id()
        account_details = Account.account_get_userid(int(user_id))
        account_details = account_details if account_details else None
        if account_details:

            get_count = 5  # Always get the 5 most recent reviews
            order_by = 'datetime'  # Sort by datetime by default

            if account_details.is_seller is False:
                review_details = Review.review_get_userid(user_id, get_count, order_by)
            else:
                review_details = Review.review_get_sellerid(user_id, get_count, order_by)


            # Get the full name for each reviewer and check if the current user has upvoted each review
            for review in review_details:
                reviewer_account = Account.account_get_userid(review.user_id)
                reviewer_name = reviewer_account.full_name if reviewer_account else "Unknown"
                # Append the review, along with whether the user has upvoted it and the reviewer's name
                has_upvoted = Review.check_if_upvoted(user_id, review.user_id, review.reviewed_id, review.review_type)
                user_reviews.append((review, has_upvoted, reviewer_name))
        
        else: None

    return render_template('account.html', account=account_details, reviews=user_reviews)

@bp.route('/account/deposit', methods=["POST"])
def deposit():
    if not current_user.is_authenticated:
        flash("You need to log in to deposit.", "danger")
        return redirect(url_for('users.login'))
    user_id = request.form.get('user_id')
    amount = request.form.get('amount')
    if not user_id or not amount:
        flash("Invalid user ID or amount.", "danger")
        return redirect(url_for('account_controller.account', user_id = user_id))
    success, message = Account.account_balance_deposit(int(user_id), float(amount))
    flash(message, "success" if success else "danger")
    return redirect(url_for('account_controller.account', user_id = user_id))

@bp.route('/account/withdrawal', methods=["POST"])
def withdrawal():
    if not current_user.is_authenticated:
        flash("You need to log in to withdrawl.", "danger")
        return redirect(url_for('users.login'))
    user_id = request.form.get('user_id')
    amount = request.form.get('amount')
    if not user_id or not amount:
        flash("Invalid user ID or amount.", "danger")
        return redirect(url_for('account_controller.account', user_id = user_id))
    success, message = Account.account_balance_withdrawal(int(user_id), float(amount))
    flash(message, "success" if success else "danger")
    return redirect(url_for('account_controller.account', user_id = user_id))

@bp.route('/account/update_address', methods=["POST"])
def update_address():
    if not current_user.is_authenticated:
        flash("You need to log in to update your address.", "danger")
        return redirect(url_for('users.login'))
    user_id = request.form.get('user_id')
    street = request.form.get('street')
    city = request.form.get('city')
    state = request.form.get('state')
    zip_code = request.form.get('zip_code')
    country = request.form.get('country')
    if not user_id:
        flash("User ID is required.", "danger")
        return redirect(url_for('account_controller.account', user_id = user_id))
    success, message = Account.update_address(user_id, street, city, state, zip_code, country)
    flash(message, "success" if success else "danger")
    referrer = request.referrer
    if "checkout" in referrer:
        return redirect(url_for('cart_controller.checkout', user_id = user_id))
    else:
        return redirect(url_for('account_controller.account', user_id = user_id))

@bp.route('/account/update_email', methods=["POST"])
def update_email():
    if not current_user.is_authenticated:
        flash("You need to log in to update your email.", "danger")
        return redirect(url_for('users.login'))
    user_id = request.form.get('user_id')
    new_email = request.form.get('new_email').strip()
    if "@" not in new_email:
        flash("Invalid email address. Please enter a valid email.", "danger")
        return redirect(url_for('account_controller.account'))
    if " " in new_email:
        flash("Invalid email address. Please enter a valid email.", "danger")
        return redirect(url_for('account_controller.account'))
    if Account.email_exists(new_email):
        flash("This email is already in use. Please choose another one.", "danger")
        return redirect(url_for('account_controller.account'))
    success, message = Account.update_email(user_id, new_email)
    flash(message, "success" if success else "danger")
    return redirect(url_for('account_controller.account'))

@bp.route('/account/update_name', methods=["POST"])
def update_name():
    if not current_user.is_authenticated:
        flash("You need to log in to update your name.", "danger")
        return redirect(url_for('users.login'))
    user_id = request.form.get('user_id')
    new_name = new_email = request.form.get('new_name').strip()
    if not new_name:
        flash("Name cannot be empty.", "danger")
        return redirect(url_for('account_controller.account'))
    success, message = Account.update_name(user_id, new_name)
    flash(message, "success" if success else "danger")
    return redirect(url_for('account_controller.account'))

@bp.route('/account/update_password', methods=["POST"])
def update_password():
    if not current_user.is_authenticated:
        flash("You need to log in to update your password.", "danger")
        return redirect(url_for('users.login'))
    user_id = request.form.get('user_id')
    new_password = request.form.get('new_password').strip()
    if not new_password:
        flash("New password cannot be empty.", "danger")
        return redirect(url_for('account_controller.account'))
    success, message = Account.update_password(user_id, new_password)
    flash(message, "success" if success else "danger")
    return redirect(url_for('account_controller.account'))
