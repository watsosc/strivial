import logging
import time

from sqlalchemy import exc

from strivial.database import db
from strivial.models import users

'''
if the user has a valid token, returns True, otherwise False
'''
def check_if_user_has_valid_token(username):
    user = db.session.query(users.User).filter_by(name=username).first()
    # we found a user and the token is still valid, that's great!
    if user is not None and user.token_expires_at > int(time.time()):
        logging.info("Valid token found for user at IP: {}".format(username))
        return True
    # we found a user but their token is expired, let's delete them
    # TODO: there must be a way to refresh this token
    elif user is not None:
        logging.info("Expired token found for user at IP: {}".format(user.name))
        db.session.delete(user)
        db.session.commit()
    return False

'''
gets the user based on the given username
'''
def get_user(username):
    return db.session.query(users.User).filter_by(name=username).first()

'''
creates a user object
takes in an athlete ID, a token response returned from Strava and an activity access level
'''
def create_user(username, athlete_id, token_response, activity_access):
    try:
        user = users.User(
            name=username,
            athlete_id=athlete_id,
            access_token=token_response['access_token'],
            refresh_token=token_response['refresh_token'],
            token_expires_at=token_response['expires_at'],
            activity_access=activity_access
        )
        db.session.add(user)
        db.session.commit()
        logging.info("Successfully created user with IP: {}".format(username))
    except exc.SQLAlchemyError:
        logging.warning("Unable to add user with IP: {}".format(username))
        db.session.rollback()
        pass

    return user

'''
based on a username, gets the active token if one can be found
'''
def get_user_token(username):
    try:
        user = db.session.query(users.User).filter_by(name=username).first()
        return user.access_token
    except exc.SQLAlchemyError:
        logging.warning("Unable to find any user with IP: {}".format(username))
        return None

'''
delete a given user when they log out
'''
def remove_user(username):
    try:
        user = db.session.query(users.User).filter_by(name=username).first()
        db.session.delete(user)
        db.session.commit()
        logging.info("Removed user with IP: {}".format(username))
    except exc.SQLAlchemyError:
        logging.warning("Unable to remove user with IP: {}".format(username))
        db.session.rollback()