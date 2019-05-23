import os
import logging
from logging import Formatter, FileHandler
from flask import Flask

def create_app(test_config=False):
    app = Flask(__name__, instance_relative_config=True)
    if test_config:
        app.config.from_object('config.TestingConfig')
    else:
        app.config.from_object(os.environ['APP_SETTINGS'])

    # set up logging if applicable
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

    # required for database migration
    from flask_script import Manager
    from flask_migrate import Migrate, MigrateCommand

    migrate = Migrate(app, db, compare_type=True)
    manager = Manager(app)

    manager.add_command('db', MigrateCommand)

    # register the strava integration
    from strivial.strava import strava_integration
    app.strava = strava_integration.StravaIntegration()

    # apply the blueprints
    from strivial.blueprints import auth, about, errors, strava_rides
    app.register_blueprint(auth.bp)
    app.register_blueprint(errors.bp)
    app.register_blueprint(about.bp)
    app.register_blueprint(strava_rides.bp)

    app.add_url_rule('/', endpoint='home')

    return app