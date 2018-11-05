import os.path
from stravalib.client import Client


class StravaIntegration:
    def __init__(self):
        file_location = os.path.dirname(__file__)
        client_file = open(file_location + '/../clienttoken', 'r')
        client_info = dict(line.split('=') for line in client_file.read().splitlines())
        self.client_id = client_info['client_id']
        self.client_secret = client_info['secret']
        self.client = Client()
        self.logged_in = False
        client_file.close()

    def get_activities(self):
        return [activity.to_dict() for activity in self.client.get_activities(limit=10)]