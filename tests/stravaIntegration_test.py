from urllib.parse import quote
from stravaIntegration import StravaIntegration
from unittest import TestCase


class StravaIntegrationTest(TestCase):
    # make sure that the initialization and we default to not logged in and we're reading the right file
    def test_initialize_strava(self):
        strava_int = StravaIntegration()
        self.assertFalse(strava_int.logged_in)
        self.assertEqual(strava_int.client_id, '25142')

    # make sure we get the right client id and redirect url out of the strava integration
    def test_get_auth_url(self):
        strava_int = StravaIntegration()
        auth_url = strava_int.get_auth_url()
        self.assertEqual(auth_url, "https://www.strava.com/oauth/authorize?client_id={cid}&"
                                   "redirect_uri={redirect}&"
                                   "approval_prompt=auto&response_type=code&scope=read%2Cactivity%3Aread"
                         .format(cid=strava_int.client_id, redirect=quote(strava_int.redirect_uri, safe='')))

    # make sure our get_activity_access method works on some expected strings
    def test_get_activity_acess(self):
        strava_int = StravaIntegration()
        # should return true on this one
        scope_string = "read,activity:read"
        is_activity_readable = strava_int.get_activity_acess(scope_string)
        self.assertTrue(is_activity_readable)

        # should return false for anything other than 'read' following the activity
        scope_string = "read,activity:none"
        is_activity_readable = strava_int.get_activity_acess(scope_string)
        self.assertFalse(is_activity_readable)

        # should return false if there is no activity entry
        scope_string = "read"
        is_activity_readable = strava_int.get_activity_acess(scope_string)
        self.assertFalse(is_activity_readable)