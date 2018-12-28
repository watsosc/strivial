import os.path
import time

from strivial.database import db
from strivial.models.users import User
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
        user = db.session.query(User).filter(
            User.name == username).first()
        # we found a user and the token is still valid, that's great!
        if user is not None and user.token_expires_at > int(time.time()):
            self.client = Client(access_token=user.access_token)
            self.logged_in = True
        # we found a user but their token is expired, let's delete them
        # TODO: there must be a way to refresh this token
        elif user is not None:
            db.session.delete(user)
            db.session.commit()
            db.session.close()

    def log_in_user(self, username, code, scope):
        # get the auth tokens from strava based on the returned code
        token_response = self.get_token_response(code)

        # set the user name to the current IP address, this way if someone comes back from the same IP we can log them right in
        user = User(
            name=username,
            access_token=token_response['access_token'],
            refresh_token=token_response['refresh_token'],
            token_expires_at=token_response['expires_at'],
            activity_access=self.get_activity_acess(scope)
        )
        db.session.add(user)
        db.session.commit()
        db.session.close()

        self.logged_in = True

    def log_out_user(self, username):
        self.client.deauthorize()
        user = db.session.query(User).filter(
            User.name == username).first()
        db.session.delete(user)
        db.session.commit()
        db.session.close()
        self.logged_in = False

    def get_token_response(self, code):
        return self.client.exchange_code_for_token(client_id=self.client_id, client_secret=self.client_secret, code=code)

    def get_activity_acess(self, scope):
        activity_scope = scope.split(':')
        if len(activity_scope) > 1:
            return activity_scope[1] == 'read'
        else:
            return False

    def get_athlete(self):
        return self.client.get_athlete()

    def get_last_activities(self, limit):
        activities = self.client.get_activities(limit=limit)
        for activity in activities:
            print(activity)
            # new_activity = Activity(activity_id=activity.activity_id)
            # db.session.add(new_activity)
            # db.session.commit()
            # db.session.close()

        return activities

    def get_thirty_day_averages(self):
        return None
