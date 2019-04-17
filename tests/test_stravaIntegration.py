from datetime import datetime, timedelta
from urllib.parse import quote

from strivial.models import users

from mockito import when, unstub

# make sure that the initialization succeeds, we default to not logged in and we're reading the right file
def test_initialize_strava(app):
    assert app.strava.logged_in is False
    assert app.strava.client_id == '25142'

# make sure we get the right client id and redirect url out of the strava integration
def test_get_auth_url(app):
    auth_url = app.strava.get_auth_url()
    expected_url = "https://www.strava.com/oauth/authorize?client_id={cid}&redirect_uri={redirect}&" \
                   "approval_prompt=auto&response_type=code&scope=read%2Cactivity%3Aread"\
        .format(cid=app.strava.client_id, redirect=quote(app.strava.redirect_uri, safe=''))
    assert auth_url == expected_url

# make sure our get_activity_access method works on some expected strings
def test_get_activity_acess(app):
    # should return true on this one
    scope_string = "read,activity:read"
    is_activity_readable = app.strava.get_activity_access(scope_string)
    assert is_activity_readable

    # should return false for anything other than 'read' following the activity
    scope_string = "read,activity:none"
    is_activity_readable = app.strava.get_activity_access(scope_string)
    assert not is_activity_readable

    # should return false if there is no activity entry
    scope_string = "read"
    is_activity_readable = app.strava.get_activity_access(scope_string)
    assert not is_activity_readable

# make sure that we update the status to logged in when a user logs in
def test_log_in_user(app):
    now = datetime.utcnow()
    future = now + timedelta(days=7)

    token_response = {
        'access_token' : 'this-token-grants-access',
        'refresh_token' : 'this-token-refreshes',
        'expires_at' : int(future.timestamp())
    }
    # we need to stub out the get_token_response method and force it to spit out some manufactured data
    when(app.strava).get_token_response('xxx').thenReturn(token_response)

    # we should be logged out
    assert not app.strava.logged_in

    username = '127.0.0.1'
    app.strava.log_in_user(username, 'xxx', 'r')

    # we should now be logged in
    assert app.strava.logged_in

    unstub()


# make sure that we get marked as logged in if the current user has a valid token and the reverse
def test_check_if_user_has_valid_token(app):
    username = '127.0.0.1'

    app.strava.check_if_user_has_valid_token(username)
    # there is no token, so user should not be logged in
    assert not app.strava.logged_in

    now = datetime.utcnow()
    future = now + timedelta(days=7)

    token_response = {
        'access_token': 'this-token-grants-access',
        'refresh_token': 'this-token-refreshes',
        'expires_at': int(future.timestamp())
    }
    # we need to stub out the get_token_response method and force it to spit out some manufactured data
    when(app.strava).get_token_response('xxx').thenReturn(token_response)
    app.strava.log_in_user(username, 'xxx', 'r')
    # user should be logged in
    assert app.strava.logged_in

    app.strava.logged_in = False
    app.strava.check_if_user_has_valid_token(username)
    # user has a valid token and should be logged back in
    assert app.strava.logged_in

def test_check_if_user_with_expired_token_is_marked_invalid(app):
    username = '127.0.0.1'
    now = datetime.utcnow()
    past = now - timedelta(days=1)

    token_response = {
        'access_token': 'this-token-grants-access',
        'refresh_token': 'this-token-refreshes',
        'expires_at': int(past.timestamp())
    }
    # we need to stub out the get_token_response method and force it to spit out some manufactured data
    when(app.strava).get_token_response('xxx').thenReturn(token_response)
    app.strava.log_in_user(username, 'xxx', 'r')
    # user should be logged in
    assert app.strava.logged_in

    app.strava.logged_in = False
    app.strava.check_if_user_has_valid_token(username)
    # user has an expired token and should not be logged back in
    assert not app.strava.logged_in

def test_log_out_user(app):
    username = '127.0.0.1'
    now = datetime.utcnow()
    future = now + timedelta(days=7)

    token_response = {
        'access_token': 'this-token-grants-access',
        'refresh_token': 'this-token-refreshes',
        'expires_at': int(future.timestamp())
    }
    # we need to stub out the get_token_response method and force it to spit out some manufactured data
    when(app.strava).get_token_response('xxx').thenReturn(token_response)
    app.strava.log_in_user(username, 'xxx', 'r')
    # user should be logged in
    assert app.strava.logged_in

    # now log the user out
    app.strava.log_out_user(username)
    assert not app.strava.logged_in