#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import logging
import time
from logging import Formatter, FileHandler
from stravaIntegration import StravaIntegration
import os

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
strava = StravaIntegration()

from models import *

# Login required decorator.
# def login_required(test):
#     @wraps(test)
#     def wrap(*args, **kwargs):
#         if 'logged_in' in session:
#             return test(*args, **kwargs)
#         else:
#             flash('You need to login first.')
#             return redirect(url_for('login'))
#     return wrap
#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def home():
    name = request.remote_addr
    user = db.session.query(User).filter(
        User.name == name).first()
    # we found a user and the token is still valid, that's great!
    if user is not None and user.token_expires_at > int(time.time()):
        strava.log_in_user(user)
        return redirect(url_for('authorized'))

    # TODO: there should be a way to refresh the token if it has expired
    return render_template('pages/main.home.html')


@app.route('/about')
def about():
    return render_template('pages/main.about.html')

@app.route('/authorized', methods=['GET', 'POST'])
def authorized():
    error = request.args.get('error')
    if error:
        return render_template('pages/main.auth-failed.html', error=error)

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
    athlete = strava.get_athlete()
    athlete_name = "{0} {1}".format(athlete.firstname, athlete.lastname)

    return render_template('pages/main.auth.html', athlete_name=athlete_name)

@app.context_processor
def variables():
    return dict(auth_url=strava.get_auth_url())

# Error handlers.

@app.errorhandler(500)
def internal_error(error):
    #db_session.rollback()
    return render_template('errors/500.html'), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''