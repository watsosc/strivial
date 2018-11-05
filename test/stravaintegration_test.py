from main.stravaintegration import StravaIntegration
from unittest import TestCase
from mockito import when, mock, unstub

class StravaIntegrationTest(TestCase):
    def test_initialize_strava(self):
        strava_int = StravaIntegration()
        self.assertFalse(strava_int.logged_in)
        self.assertEqual(strava_int.client_id, '25142')