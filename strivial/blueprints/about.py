from flask import Blueprint, render_template
from flask import current_app as app

bp = Blueprint('about', __name__, url_prefix='/')

@bp.route('/about')
def about():
    return render_template('pages/main.about.html', logged_in=app.strava.logged_in)