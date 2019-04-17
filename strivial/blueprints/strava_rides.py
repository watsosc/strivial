from flask import Blueprint, render_template
from flask import current_app as app
from datetime import datetime, timedelta

bp = Blueprint('strava_rides', __name__, url_prefix='/')

@bp.route('/load-rides')
def load_rides():
    start_date = datetime.now() - timedelta(months=1)
    app.strava.load_activities(start_date=start_date)
    return render_template('pages/main.load.html', logged_in=app.strava.logged_in)