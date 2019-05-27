import logging

from sqlalchemy import exc
from pickle import dumps

from strivial.database import db
from strivial.models import activities

# creates an activity for saving in DB based on the original strava activity and the power stream
def create_activity(strava_activity, power_stream):
    try:
        new_activity = activities.Activity(
            activity_id=strava_activity.id,
            athlete_id=strava_activity.athlete.id,
            name=strava_activity.name,
            date=strava_activity.start_date,
            length_in_time=float(strava_activity.moving_time.seconds),
            length_in_distance=float(strava_activity.distance),
            normalized_power=strava_activity.weighted_average_watts,
            total_power=strava_activity.kilojoules,
            power_stream=dumps(power_stream)
        )
        db.session.add(new_activity)
        db.session.commit()
        logging.info("Successfully loaded activity {}".format(strava_activity.id))
    except exc.SQLAlchemyError as error:
        logging.warning("Unable to add activity with ID: {0}\n Error: {1}".format(strava_activity.id, error))
        db.session.rollback()

def get_activity(activity_id):
    try:
        activity = db.session\
            .query(activities.Activity)\
            .filter_by(activity_id=activity_id)\
            .first()
        if activity is not None:
            return activity
    except exc.SQLAlchemyError as error:
        logging.warning("Unable to load activity {0}\n Error: {1}".format(activity_id, error))

    return None

# get a subset of most recent activities from the DB
# required argument limit gives the maximum number to return
def get_last_activities_minimal(limit):
    if limit < 1:
        return None

    latest_activities = db.session\
        .query(activities.Activity.name, activities.Activity.date, activities.Activity.length_in_time, activities.Activity.total_power)\
        .order_by(activities.Activity.date.desc())\
        .limit(limit).all()

    logging.info("Found {} recent activities in db".format(len(latest_activities)))

    return latest_activities

def get_most_recent_activity_date_for_athlete(athlete_id):
    try:
        latest_activity = db.session\
            .query(activities.Activity)\
            .filter_by(athlete_id=athlete_id)\
            .order_by(activities.Activity.date.desc())\
            .first()
        if latest_activity is not None:
            return latest_activity.date
    except exc.SQLAlchemyError as error:
        logging.warning("Unable to load activities for athlete {0}\n Error: {1}".format(athlete_id, error))
    return None
