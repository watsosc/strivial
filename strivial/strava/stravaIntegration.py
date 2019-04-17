import os.path
import time
import logging

from sqlalchemy import exc
from pickle import dumps

from strivial.database import db
from strivial.models import users, athletes, activities
from stravalib.client import Client

class StravaIntegration:
    def __init__(self):
        file_location = os.path.dirname(__file__)
        client_file = open(file_location + '/clienttoken', 'r')
        client_info = dict(line.split('=') for line in client_file.read().splitlines())
        self.client_id = client_info['client_id']
        self.client_secret = client_info['secret']
        self.client = Client()
        self.redirect_uri = 'http://localhost:5000/authorized'
        self.logged_in = False
        client_file.close()

    def get_auth_url(self):
        return self.client.authorization_url(client_id=self.client_id, redirect_uri=self.redirect_uri)

    def check_if_user_has_valid_token(self, username):
        user = db.session.query(users.User).filter_by(name=username).first()
        # we found a user and the token is still valid, that's great!
        if user is not None and user.token_expires_at > int(time.time()):
            logging.debug("Valid token found for user at IP: {}".format(username))
            self.client = Client(access_token=user.access_token)
            self.logged_in = True
        # we found a user but their token is expired, let's delete them
        # TODO: there must be a way to refresh this token
        elif user is not None:
            logging.debug("Expired token found for user at IP: {}".format(username))
            db.session.delete(user)
            db.session.commit()

    def log_in_user(self, username, code, scope):
        # get the auth tokens from strava based on the returned code
        # in the case of a failed login we will never get to this method, so we don't need to worry about the case of an invalid code
        token_response = self.get_token_response(code)

        try:
            # we use the current IP address as the username, this way if someone comes back from the same IP we can log them right in
            user = users.User(
                name=username,
                access_token=token_response['access_token'],
                refresh_token=token_response['refresh_token'],
                token_expires_at=token_response['expires_at'],
                activity_access=self.get_activity_access(scope)
            )
            db.session.add(user)
            db.session.commit()
            logging.debug("Successfully logged in user with IP: {}".format(username))
        except exc.SQLAlchemyError:
            logging.warning("Unable to add user with IP: {}".format(username))
            db.session.rollback()
            pass

        self.logged_in = True

    def log_out_user(self, username):
        self.client.deauthorize()
        try:
            user = db.session.query(users.User).filter_by(name=username).first()
            db.session.delete(user)
            db.session.commit()
            logging.debug("Logged out user with IP: {}".format(username))
        except exc.SQLAlchemyError:
            logging.warning("Unable to log out user with IP: {}".format(username))
            db.session.rollback()
            pass

        self.logged_in = False

    def get_token_response(self, code):
        return self.client.exchange_code_for_token(client_id=self.client_id, client_secret=self.client_secret, code=code)

    def get_activity_access(self, scope):
        activity_scope = scope.split(':')
        if len(activity_scope) > 1:
            return activity_scope[1] == 'read'
        else:
            return False

    def get_athlete(self, username):
        athlete_stream = self.client.get_athlete()
        try:
            athlete = athletes.Athlete(
                athlete_id=athlete_stream.id,
                user_id=username,
                first_name=athlete_stream.firstname,
                last_name=athlete_stream.lastname
            )
            db.session.add(athlete)
            db.session.commit()
            logging.debug("Added new athlete with ID: {}".format(athlete_stream.id))
        except exc.SQLAlchemyError:
            logging.warning("Unable to add athlete with ID: {}".format(athlete_stream.id))
            db.session.rollback()
            pass

        return athlete

    def load_activities(self, start_date=None, end_date=None, limit=None):
        activities = self.client.get_activities(before=end_date, after=start_date, limit=limit)
        for activity in activities:
            power_stream = self.client.get_activity_streams(activity_id=activity.id, types=['watts'], series_type='time')
            try:
                new_activity = activities.Activity(
                    activity_id=activity.id,
                    athlete_id=activity.athlete.id,
                    name=activity.name,
                    date=activity.start_date,
                    length_in_time=activity.moving_time,
                    length_in_distance=activity.distance,
                    normalized_power=activity.weighted_average_power,
                    total_power=activity.kilojoules,
                    power_stream=dumps(power_stream)
                )
                db.session.add(new_activity)
                db.session.commit()
                logging.debug("Successfully loaded activity {}".format(activity.id))
            except exc.SQLAlchemyError:
                logging.warning("Unable to add activity with ID: {}".format(activity.id))
                db.session.rollback()

    def get_last_activities_minimal(self, limit):
        if limit < 1:
            return None

        latest_activities = db.session\
            .query(activities.Activity.name, activities.Activity.date, activities.Activity.length_in_time, activities.Activity.total_power)\
            .order_by(activities.Activity.date.desc())\
            .limit(limit).all()

        logging.debug("Found {} recent activities in db".format(len(latest_activities)))

        return latest_activities

    def get_thirty_day_averages(self):
        return None
