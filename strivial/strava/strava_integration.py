import os.path
import logging

from strivial.services import user_service, athlete_service, activity_service
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

    def log_in_user_with_active_session(self, username):
        self.client.access_token = user_service.get_user_token(username)


    # called after we get the Oauth credentials from Strava
    def log_in_user(self, username, code, scope):
        # get the auth tokens from strava based on the returned code
        # in the case of a failed login we will never get to this method, so we don't need to worry about the case of an invalid code
        token_response = self.get_token_response(code)
        athlete = self.get_athlete(username)
        activity_access = self.get_activity_access(scope)

        user_service.create_user(username, athlete.athlete_id, token_response, activity_access)
        self.client.access_token = token_response['access_token']

    # logs a user out, we delete their User object but no need to delete the Athlete object
    # they might come back and we don't want to have to download their profile and activities again
    def log_out_user(self, username):
        self.client.deauthorize()
        user_service.remove_user(username)

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
        athlete = athlete_service.get_athlete(username)
        if athlete is None:
            athlete_stream = self.client.get_athlete()
            athlete = athlete_service.create_athlete(athlete_stream)

        return athlete

    # used to pull in activities for the logged in user
    # accepts optional arguments for the search start date, end date and a limit on number of results
    def load_activities(self, start_date=None, end_date=None, limit=None):
        logging.info("Attempting to load rides for current user since date {}.".format(start_date))
        activity_list = self.client.get_activities(before=end_date, after=start_date, limit=limit)
        for activity in activity_list:
            power_stream = self.client.get_activity_streams(activity_id=activity.id, types=['watts'], series_type='time')
            activity_service.create_activity(activity, power_stream)
