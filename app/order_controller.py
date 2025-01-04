from flask import Blueprint, request, render_template, redirect, url_for, jsonify, flash
from flask_login import current_user, login_required
from .models.ordersummary import Ordersummary
from .models.orderitem import Orderitem
from flask_login import current_user

bp = Blueprint('order_controller', __name__)

@bp.route('/order', methods = ["GET"])
@login_required
def order():
    user_id = None
    ordersummaries = []
    orderitems = []
    fulfillment_status = {}
    sort_by = request.args.get('sort_by', 'recent')
    if current_user.is_authenticated:
        user_id = current_user.user_id
        ordersummaries = Ordersummary.ordersummary_get_userid(int(user_id), sort_by)
        orderitems = Orderitem.orderitem_get_userid(int(user_id))
        for summary in ordersummaries:
            order_id = summary.order_id
            items = [item for item in orderitems if item.order_id == order_id]
            if all(item.is_fulfilled for item in items):
                fulfillment_status[order_id] = "Fulfilled"
            else:
                fulfillment_status[order_id] = "Not Fulfilled"
    return render_template('order.html', ordersummaries = ordersummaries, orderitems = orderitems, fulfillment_status = fulfillment_status, sort_by = sort_by)
