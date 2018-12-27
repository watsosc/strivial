#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from flask import Blueprint, render_template, request, redirect, url_for
import time
from strivial.strava.stravaIntegration import StravaIntegration
from strivial.database import db

bp = Blueprint('routes', __name__, url_prefix='/')

strava = StravaIntegration()

from strivial.models.models import *

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#
@bp.route('/')
def home():
    name = request.remote_addr
    user = db.session.query(User).filter(
        User.name == name).first()
    # we found a user and the token is still valid, that's great!
    if user is not None and user.token_expires_at > int(time.time()):
        strava.log_in_user(user)
        return show_after_auth()
    elif user is not None:
        db.session.delete(user)
        db.session.commit()
        db.session.close()

    # TODO: there should be a way to refresh the token if it has expired
    return render_template('pages/main.home.html', logged_in=strava.logged_in)


@bp.route('/about')
def about():
    return render_template('pages/main.about.html', logged_in=strava.logged_in)

@bp.route('/authorized', methods=['GET', 'POST'])
def authorized():
    error = request.args.get('error')
    if error:
        return render_template('pages/main.auth-failed.html', error=error, logged_in=strava.logged_in)

    if strava.logged_in is False:
        # Strava sends back something like this:
        #    /authorized?state=&code=xxxxxxxxxxxxxxxxxxxxxxxxxx&scope=read,activity:read
        code = request.args.get('code')
        scope = request.args.get('scope')

        # get the auth tokens from strava based on the returned code
        token_response = strava.get_token_response(code)
        access_token = token_response['access_token']
        refresh_token = token_response['refresh_token']
        expires_at = token_response['expires_at']
        activity_access = strava.get_activity_acess(scope)

        # set the user name to the current IP address, this way if someone comes back from the same IP we can log them right in
        user = User(
            name=request.remote_addr,
            access_token=access_token,
            refresh_token=refresh_token,
            token_expires_at=expires_at,
            activity_access=activity_access
        )
        db.session.add(user)
        db.session.commit()
        db.session.close()

        strava.logged_in = True
    return show_after_auth()

def show_after_auth():
    athlete = strava.get_athlete()
    athlete_name = "{0} {1}".format(athlete.firstname, athlete.lastname)
    thirty_day_averages = strava.get_thirty_day_averages()
    last_five_activities = strava.get_last_activities(5)
    print(last_five_activities)

    return render_template('pages/main.auth.html', logged_in=strava.logged_in, athlete_name=athlete_name,
                           averages=thirty_day_averages, last_activities=last_five_activities)

@bp.route('/logout', methods=['GET', 'POST'])
def logout():
    strava.client.deauthorize()
    user = db.session.query(User).filter(
        User.name == request.remote_addr).first()
    db.session.delete(user)
    db.session.commit()
    db.session.close()
    strava.logged_in = False

    return redirect(url_for('home'))


@bp.context_processor
def variables():
    return dict(auth_url=strava.get_auth_url())