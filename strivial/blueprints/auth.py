from strivial.services import user_service, athlete_service, activity_service

from flask import Blueprint, render_template, request, redirect, url_for
from flask import current_app as app

bp = Blueprint('auth', __name__, url_prefix='/')

'''
this is the generic home route that all users will originally hit
it checks to see if the visiting IP has a currently logged in session and redirects if so
'''
@bp.route('/')
def home():
    logged_in = user_service.check_if_user_has_valid_token(request.remote_addr)

    if logged_in:
        app.strava.log_in_user_with_active_session(request.remote_addr)
        return show_after_auth()

    return render_template('pages/main.home.html', logged_in=logged_in)

'''
this route is accessed by a Strava redirect after Oauth2 authentication
'''
@bp.route('/authorized', methods=['GET', 'POST'])
def authorized():
    error = request.args.get('error')
    if error:
        return render_template('pages/main.auth-failed.html', error=error, logged_in=app.strava.logged_in)

    # Strava sends back something like this:
    #    /authorized?state=&code=xxxxxxxxxxxxxxxxxxxxxxxxxx&scope=read,activity:read
    # the code confirms the Oauth login, the scope gives our access to a user's files
    code = request.args.get('code')
    scope = request.args.get('scope')
    app.strava.log_in_user(request.remote_addr, code, scope)

    return redirect(url_for('home'))

'''
this method shows the authorized page and is called in the case where a user has been authorized with Strava
'''
def show_after_auth():
    athlete_name = athlete_service.get_athlete_name(request.remote_addr)
    #thirty_day_averages = app.strava.get_thirty_day_averages()
    last_five_activities = activity_service.get_last_activities_minimal(5)

    return render_template('pages/main.auth.html', logged_in=True, athlete_name=athlete_name,
                           averages=None, last_activities=last_five_activities)

'''
this route logs a user out
'''
@bp.route('/logout', methods=['GET', 'POST'])
def logout():
    app.strava.log_out_user(request.remote_addr)

    return redirect(url_for('home'))

'''
puts the Strava authorization URL out as a blueprint variable
'''
@bp.context_processor
def variables():
    return dict(auth_url=app.strava.get_auth_url())