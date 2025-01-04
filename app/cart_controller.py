from flask import Blueprint, request, render_template, redirect, url_for, jsonify, flash
from flask_login import current_user, login_required
from .models.cart import Cart
from .models.account import Account
from flask_login import current_user

bp = Blueprint('cart_controller', __name__)

@bp.route('/cart', methods = ["GET"])
@login_required
def cart():
    user_id = None
    carts = []
    total_cost = 0
    if current_user.is_authenticated:
        user_id = current_user.user_id
        carts = Cart.cart_get_userid(int(user_id))
        total_cost = 0
        for cart in carts:
            if not cart.saved_for_later:
                total_cost += cart.price * cart.quantity
    return render_template('cart.html', carts = carts, total_cost = total_cost)

@bp.route('/cart/update_sfl', methods=["POST"])
def update_sfl():
    if not current_user.is_authenticated:
        flash("You need to log in to update the saved for later in cart.", "danger")
        return redirect(url_for('users.login'))
    user_id = request.form.get('user_id')
    product_id = request.form.get('product_id')
    seller_id = request.form.get('seller_id')
    if user_id and product_id and seller_id:
        Cart.update_SFL_status(int(user_id), int(product_id), int(seller_id))
        flash("Item successfully moved!", "success")
    return redirect(url_for('cart_controller.cart', user_id = user_id))

@bp.route('/cart/delete_item', methods=["POST"])
def delete_item():
    if not current_user.is_authenticated:
        flash("You need to log in to delete item in cart.", "danger")
        return redirect(url_for('users.login'))
    user_id = request.form.get('user_id')
    product_id = request.form.get('product_id')
    seller_id = request.form.get('seller_id')
    if user_id and product_id and seller_id:
        Cart.delete_cart_item(int(user_id), int(product_id), int(seller_id))
        flash("Item successfully deleted!", "success")
    return redirect(url_for('cart_controller.cart', user_id = user_id))

@bp.route('/cart/update_quantity', methods=["POST"])
def update_quantity():
    if not current_user.is_authenticated:
        flash("You need to log in to update quantity in cart.", "danger")
        return redirect(url_for('users.login'))
    user_id = request.form.get('user_id')
    product_id = request.form.get('product_id')
    seller_id = request.form.get('seller_id')
    updated_quantity = request.form.get('quantity')
    if user_id and product_id and seller_id and updated_quantity:
        success, message = Cart.update_item_quantity(int(user_id), int(product_id), int(seller_id), int(updated_quantity))
        if not success:
            flash(message, 'danger')
        else:
            flash(message, 'success')
    return redirect(url_for('cart_controller.cart', user_id=user_id))

@bp.route('/checkout', methods = ["GET"])
def checkout():
    if not current_user.is_authenticated:
        flash("You need to log in to go to checkout.", "danger")
        return render_template('index.html')
    user_id = request.args.get('user_id')
    checkout_items = []
    total_cost = 0
    user_info = None
    if user_id:
        checkout_items = Cart.cart_checkout(int(user_id))
        total_cost = 0
        for items in checkout_items:
            total_cost += items.price * items.quantity
        user_info = Account.account_get_userid(int(user_id)) if Account.account_get_userid(int(user_id)) else None
    return render_template('checkout.html', checkout_items = checkout_items, total_cost = total_cost, user_info = user_info, user_id = user_id)

@bp.route('/checkout/submit_order', methods=["POST"])
def submit_order():
    if not current_user.is_authenticated:
        flash("You need to log in to submit an order.", "danger")
        return render_template('index.html')
    user_id = request.form.get('user_id')
    if not user_id:
        flash("Invalid user ID.", "danger")
        return redirect(url_for('cart_controller.checkout', user_id = user_id))
    checkout_items = Cart.cart_checkout(int(user_id))
    user_info = Account.account_get_userid(int(user_id)) if Account.account_get_userid(int(user_id)) else None
    if not checkout_items or not user_info:
        flash("No items available for checkout or invalid user.", "danger")
        return redirect(url_for('cart_controller.checkout', user_id = user_id))
    success, message = Cart.checkout_process(int(user_id), checkout_items, user_info.balance)
    if not success:
        flash(message, "danger")
        return redirect(url_for('cart_controller.checkout', user_id = user_id))
    order_summary, order_items = Cart.create_order(int(user_id), checkout_items)
    if order_summary:
        return render_template('ordersummary.html', order_summary = order_summary, order_items = order_items)
    else:
        flash("An error occurred while creating the order.", "danger")
        return redirect(url_for('cart_controller.checkout', user_id = user_id))
