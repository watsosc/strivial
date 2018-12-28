#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from flask import Blueprint, render_template, request, redirect, url_for
from flask import current_app as app

bp = Blueprint('routes', __name__, url_prefix='/')

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#
@bp.route('/')
def home():
    app.strava.check_if_user_has_valid_token(request.remote_addr)

    if app.strava.logged_in:
        return show_after_auth()

    return render_template('pages/main.home.html', logged_in=app.strava.logged_in)


@bp.route('/about')
def about():
    return render_template('pages/main.about.html', logged_in=app.strava.logged_in)

@bp.route('/authorized', methods=['GET', 'POST'])
def authorized():
    error = request.args.get('error')
    if error:
        return render_template('pages/main.auth-failed.html', error=error, logged_in=app.strava.logged_in)

    if app.strava.logged_in is False:
        # Strava sends back something like this:
        #    /authorized?state=&code=xxxxxxxxxxxxxxxxxxxxxxxxxx&scope=read,activity:read
        # the code confirms the Oauth login, the scope gives our access to a user's files
        code = request.args.get('code')
        scope = request.args.get('scope')
        app.strava.log_in_user(request.remote_addr, code, scope)

    return show_after_auth()

def show_after_auth():
    athlete = app.strava.get_athlete()
    athlete_name = "{0} {1}".format(athlete.firstname, athlete.lastname)
    thirty_day_averages = app.strava.get_thirty_day_averages()
    last_five_activities = app.strava.get_last_activities(5)
    print(last_five_activities)

    return render_template('pages/main.auth.html', logged_in=app.strava.logged_in, athlete_name=athlete_name,
                           averages=thirty_day_averages, last_activities=last_five_activities)

@bp.route('/logout', methods=['GET', 'POST'])
def logout():
    app.strava.log_out_user(request.remote_addr)

    return redirect(url_for('home'))


@bp.context_processor
def variables():
    return dict(auth_url=app.strava.get_auth_url())