#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from strivial.services import user_service, athlete_service, activity_service

from flask import Blueprint, render_template, request, redirect, url_for
from flask import current_app as app

bp = Blueprint('auth', __name__, url_prefix='/')

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#
@bp.route('/')
def home():
    logged_in = user_service.check_if_user_has_valid_token(request.remote_addr)

    if logged_in:
        app.strava.log_in_user_with_active_session(request.remote_addr)
        return show_after_auth()

    return render_template('pages/main.home.html', logged_in=logged_in)

@bp.route('/authorized', methods=['GET', 'POST'])
def authorized():
    error = request.args.get('error')
    if error:
        return render_template('pages/main.auth-failed.html', error=error, logged_in=app.strava.logged_in)

    logged_in = user_service.check_if_user_has_valid_token(request.remote_addr)
    if logged_in is False:
        # Strava sends back something like this:
        #    /authorized?state=&code=xxxxxxxxxxxxxxxxxxxxxxxxxx&scope=read,activity:read
        # the code confirms the Oauth login, the scope gives our access to a user's files
        code = request.args.get('code')
        scope = request.args.get('scope')
        app.strava.log_in_user(request.remote_addr, code, scope)

    return show_after_auth()

def show_after_auth():
    logged_in = user_service.check_if_user_has_valid_token(request.remote_addr)

    athlete_name = athlete_service.get_athlete_name(request.remote_addr)
    #thirty_day_averages = app.strava.get_thirty_day_averages()
    last_five_activities = activity_service.get_last_activities_minimal(5)

    return render_template('pages/main.auth.html', logged_in=logged_in, athlete_name=athlete_name,
                           averages=None, last_activities=last_five_activities)

@bp.route('/logout', methods=['GET', 'POST'])
def logout():
    app.strava.log_out_user(request.remote_addr)

    return redirect(url_for('home'))


@bp.context_processor
def variables():
    return dict(auth_url=app.strava.get_auth_url())