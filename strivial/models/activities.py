from strivial.database import db
from sqlalchemy import ForeignKey

'''
This table is used to store strava activities: their id and essential info
'''
class Activity(db.Model):
    __tablename__ = 'activities'

    activity_id = db.Column(db.Integer, primary_key=True)
    athlete_id = db.Column(db.Integer, ForeignKey('athletes.athlete_id'), unique=True, nullable=False)
    athlete = db.relationship('Athlete', backref=db.backref('activities', cascade='all,delete', lazy=True))
    name = db.Column(db.String(250))
    date = db.Column(db.DateTime)
    length_in_time = db.Column(db.Integer)
    length_in_distance = db.Column(db.Integer)
    normalized_power = db.Column(db.Integer)
    total_power = db.Column(db.Integer)
    power_stream = db.Column(db.LargeBinary)

    def __repr__(self):
        return '<id {}>'.format(self.activity_id)