#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import logging
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
    return render_template('pages/placeholder.home.html')


@app.route('/about')
def about():
    return render_template('pages/placeholder.about.html')

@app.route('/authorized', methods=['GET', 'POST'])
def authorized():
    # Strava sends back something like this:
    #    /authorized?state=&code=3b90387114bf639aee734e13f76df5bc43ca4d5d&scope=read,activity:read
    code = request.args.get('code')
    scope = request.args.get('scope')

    token_response = strava.get_token_response(code)
    access_token = token_response['access_token']
    refresh_token = token_response['refresh_token']
    expires_at = token_response['expires_at']
    activity_access = strava.get_activity_acess(scope)

    name = 'temporary'
    user = db.session.query(User).filter(
        User.name == name).first()
    if user is None:
        user = User(
            name="temporary",
            access_token=access_token,
            refresh_token=refresh_token,
            token_expires_at=expires_at,
            activity_access=activity_access
        )
        db.session.add(user)
    else:
        user.access_token = access_token
        user.refresh_token = refresh_token
        user.token_expires_at = expires_at

    db.session.commit()
    db.session.close()

    return render_template('pages/placeholder.auth.html')

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