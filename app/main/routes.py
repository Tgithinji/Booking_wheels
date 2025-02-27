from flask_login import current_user
from app.main import bp
from flask import render_template


@bp.before_app_request
def before_request():
    from app.utils import check_and_update_bookings
    if current_user.is_authenticated:
        check_and_update_bookings()


@bp.route('/')
@bp.route('/index')
def index():
    """Home page route"""
    return render_template('index.html', title='Home', section='home')
