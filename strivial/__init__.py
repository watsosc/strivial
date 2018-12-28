import os
import logging
from logging import Formatter, FileHandler
from flask import Flask

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(os.environ['APP_SETTINGS'])

    if not app.debug:
        file_handler = FileHandler('error.log')
        file_handler.setFormatter(
            Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
        )
        app.logger.setLevel(logging.INFO)
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.info('errors')

    #ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # register the database
    from strivial.database import db
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    from strivial.strava import stravaIntegration
    app.strava = stravaIntegration.StravaIntegration()

    # apply the blueprints
    from strivial.blueprints import routes, errors
    app.register_blueprint(routes.bp)
    app.register_blueprint(errors.bp)

    app.add_url_rule('/', endpoint='home')

    return app