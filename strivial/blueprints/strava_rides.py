from flask import Blueprint, render_template, request
from flask import current_app as app
from datetime import datetime
from dateutil.relativedelta import relativedelta

bp = Blueprint('strava_rides', __name__, url_prefix='/')

@bp.route('/load-rides', methods=['GET'])
def load_rides():
    start_date = datetime.utcnow() - relativedelta(months=1)
    date_string = start_date.replace(microsecond=0).isoformat()
    user_has_valid_token = app.strava.check_if_user_has_valid_token(request.remote_addr)
    if user_has_valid_token:
        app.strava.load_activities(start_date=date_string)
        return render_template('pages/main.load.html', logged_in=user_has_valid_token, athlete_name=app.strava.get_athlete_name())
    else:
        return render_template('pages/main.auth.html', logged_in=user_has_valid_token)