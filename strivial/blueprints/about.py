from flask import Blueprint, render_template, request
from flask import current_app as app

bp = Blueprint('about', __name__, url_prefix='/')

@bp.route('/about')
def about():
    logged_in = app.strava.check_if_user_has_valid_token(request.remote_addr)

    return render_template('pages/main.about.html', logged_in=logged_in)