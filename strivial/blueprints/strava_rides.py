from flask import Blueprint, render_template, request, redirect, url_for
from flask import current_app as app

from strivial.services import user_service, athlete_service, activity_service

from datetime import datetime
from dateutil.relativedelta import relativedelta

bp = Blueprint('strava_rides', __name__, url_prefix='/')

@bp.route('/load-rides', methods=['GET'])
def load_rides():
    username = request.remote_addr
    user_has_valid_token = user_service.check_if_user_has_valid_token(username)
    if user_has_valid_token:
        athlete = athlete_service.get_athlete(username)
        # try getting the most recent activity that we have saved for this user
        latest_activity_date = activity_service.get_most_recent_activity_date_for_athlete(athlete.athlete_id)
        # if we don't have one let's just load everything in the last month
        if latest_activity_date is None:
            latest_activity_date = datetime.utcnow() - relativedelta(months=1)
        # add one hour to the time we have, if we are looking at the last month it doesn't matter
        # but if we got the last activity time it prevents us getting that initial activity again
        latest_activity_date += relativedelta(hours=1)

        app.strava.load_activities(start_date=datetime.utcfromtimestamp(latest_activity_date.timestamp()))
        last_five_activities = activity_service.get_last_activities_minimal(5)

        return render_template('pages/main.load.html',
                               logged_in=user_has_valid_token,
                               athlete_name=athlete_service.get_athlete_name(username),
                               last_activities=last_five_activities)
    else:
        return redirect(url_for('home'))

@bp.route('/ride/<activity_id>', methods=['GET'])
def show_ride(activity_id):
    activity = activity_service.get_activity(activity_id)
    return redirect(url_for('home'))