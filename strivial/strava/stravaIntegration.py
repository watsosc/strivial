import os.path
from datetime import date, timedelta
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

    def log_in_user(self, user):
        self.client = Client(access_token=user.access_token)
        self.logged_in = True

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
