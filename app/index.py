from flask import Blueprint, request, render_template
from flask_login import login_required

bp = Blueprint('index', __name__)


@bp.route('/', methods = ["GET"])
#@login_required

def index():
    return render_template('index.html')
