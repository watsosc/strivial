import logging

from sqlalchemy import exc

from strivial.services import user_service
from strivial.database import db
from strivial.models import athletes

'''
attempts to get an athlete based on a username, returns None if there is no such athlete
'''
def get_athlete(username):
    try:
        user = user_service.get_user(username)
        if user is not None:
            return db.session.query(athletes.Athlete).filter_by(athlete_id=user.athlete_id).first()
    except exc.SQLAlchemyError:
        logging.warning("Unable to find athlete for user {}".format(username))
    return None

'''
takes an athlete stream from Strava and creates a local Athlete object from it
'''
def create_athlete(athlete_stream):
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

'''
pulls the athlete's name out of an Athlete object
'''
def get_athlete_name(username):
    athlete = get_athlete(username)
    if athlete is not None:
        name = "{0} {1}".format(athlete.first_name, athlete.last_name)
        return name
    else:
        return ''