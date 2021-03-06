from flask import Blueprint, render_template, request
from strivial.services import user_service

bp = Blueprint('about', __name__, url_prefix='/')

@bp.route('/about')
def about():
    logged_in = user_service.check_if_user_has_valid_token(request.remote_addr)

    return render_template('pages/main.about.html', logged_in=logged_in)