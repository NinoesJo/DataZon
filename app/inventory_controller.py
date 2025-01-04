from flask import Blueprint, request, render_template
from .models.inventory import Inventory

from flask_login import current_user, login_required

bp = Blueprint('inventory_controller', __name__)
