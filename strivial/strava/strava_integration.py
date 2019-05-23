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
        # remember to do this to set the minimum logging level
        logging.basicConfig(level=logging.DEBUG)

        # grab out all the client info, saved in a file in the same folder as this runs
        file_location = os.path.dirname(__file__)
        client_file = open(file_location + '/clienttoken', 'r')
        client_info = dict(line.split('=') for line in client_file.read().splitlines())
        self.client_id = client_info['client_id']
        self.client_secret = client_info['secret']
        client_file.close()

        self.client = Client()
        # redirect uri is where strava sends you after their Oauth runs
        self.redirect_uri = 'http://localhost:5000/authorized'

    # builds the url for Strava's Oauth
    def get_auth_url(self):
        return self.client.authorization_url(client_id=self.client_id, redirect_uri=self.redirect_uri)

    # if the user has a valid token, returns True, otherwise False
    def check_if_user_has_valid_token(self, username):
        user = db.session.query(users.User).filter_by(name=username).first()
        # we found a user and the token is still valid, that's great!
        if user is not None and user.token_expires_at > int(time.time()):
            logging.info("Valid token found for user at IP: {}".format(username))
            self.client = Client(access_token=user.access_token)
            return True
        # we found a user but their token is expired, let's delete them
        # TODO: there must be a way to refresh this token
        elif user is not None:
            logging.info("Expired token found for user at IP: {}".format(user.name))
            db.session.delete(user)
            db.session.commit()
        return False

    # called after we get the Oauth credentials from Strava
    # creates Athlete and User objects for this user and saves them to DB
    def log_in_user(self, username, code, scope):
        # get the auth tokens from strava based on the returned code
        # in the case of a failed login we will never get to this method, so we don't need to worry about the case of an invalid code
        token_response = self.get_token_response(code)
        athlete = self.get_athlete(username)

        try:
            # we use the current IP address as the username, this way if someone comes back from the same IP we can log them right in
            user = users.User(
                name=username,
                athlete_id = athlete.athlete_id,
                access_token=token_response['access_token'],
                refresh_token=token_response['refresh_token'],
                token_expires_at=token_response['expires_at'],
                activity_access=self.get_activity_access(scope)
            )
            self.client.access_token = token_response['access_token']
            db.session.add(user)
            db.session.commit()
            logging.info("Successfully logged in user with IP: {}".format(username))
        except exc.SQLAlchemyError:
            logging.warning("Unable to add user with IP: {}".format(username))
            db.session.rollback()
            pass

    # logs a user out, we delete their User object but no need to delete the Athlete object
    # they might come back and we don't want to have to download their profile and activities again
    def log_out_user(self, username):
        self.client.deauthorize()
        try:
            user = db.session.query(users.User).filter_by(name=username).first()
            db.session.delete(user)
            db.session.commit()
            logging.info("Logged out user with IP: {}".format(username))
        except exc.SQLAlchemyError:
            logging.warning("Unable to log out user with IP: {}".format(username))
            db.session.rollback()
            pass

    # gets the token response from Strava
    def get_token_response(self, code):
        return self.client.exchange_code_for_token(client_id=self.client_id, client_secret=self.client_secret, code=code)

    # reads an activity scope and finds out whether or not we have read access
    def get_activity_access(self, scope):
        activity_scope = scope.split(':')
        if len(activity_scope) > 1:
            return activity_scope[1] == 'read'
        else:
            return False

    # gets the Athlete object for the logged in user and saves to DB
    def get_athlete(self, username):
        athlete = db.session.query(athletes.Athlete).filter_by(user_id=username).first()
        if athlete is None:
            athlete_stream = self.client.get_athlete()
            try:
                athlete = athletes.Athlete(
                    athlete_id=athlete_stream.id,
                    first_name=athlete_stream.firstname,
                    last_name=athlete_stream.lastname
                )
                db.session.add(athlete)
                db.session.commit()
                logging.info("Added new athlete with ID: {}".format(athlete_stream.id))
            except exc.SQLAlchemyError:
                logging.warning("Unable to add athlete with ID: {}".format(athlete_stream.id))
                db.session.rollback()
                pass

        return athlete

    # pulls the athlete's name out of an Athlete object
    def get_athlete_name(self, username):
        athlete = self.get_athlete(username)
        if athlete is not None:
            name = "{0} {1}".format(athlete.first_name, athlete.last_name)
            return name
        else:
            return ''

    # used to pull in activities for the logged in user
    # accepts optional arguments for the search start date, end date and a limit on number of results
    def load_activities(self, start_date=None, end_date=None, limit=None):
        logging.info("Attempting to load rides for current user since date {}.".format(start_date))
        activity_list = self.client.get_activities(before=end_date, after=start_date, limit=limit)
        for activity in activity_list:
            power_stream = self.client.get_activity_streams(activity_id=activity.id, types=['watts'], series_type='time')
            try:
                new_activity = activities.Activity(
                    activity_id=activity.id,
                    athlete_id=activity.athlete.id,
                    name=activity.name,
                    date=activity.start_date,
                    length_in_time=activity.moving_time,
                    length_in_distance=activity.distance,
                    normalized_power=activity.weighted_average_watts,
                    total_power=activity.kilojoules,
                    power_stream=dumps(power_stream)
                )
                db.session.add(new_activity)
                db.session.commit()
                logging.info("Successfully loaded activity {}".format(activity.id))
            except exc.SQLAlchemyError:
                logging.warning("Unable to add activity with ID: {}".format(activity.id))
                db.session.rollback()

    # get a subset of most recent activities from the DB
    # required argument limit gives the maximum number to return
    def get_last_activities_minimal(self, limit):
        if limit < 1:
            return None

        latest_activities = db.session\
            .query(activities.Activity.name, activities.Activity.date, activities.Activity.length_in_time, activities.Activity.total_power)\
            .order_by(activities.Activity.date.desc())\
            .limit(limit).all()

        logging.info("Found {} recent activities in db".format(len(latest_activities)))

        return latest_activities

    def get_thirty_day_averages(self):
        return None
