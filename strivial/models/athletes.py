from strivial.database import db
from sqlalchemy import ForeignKey

'''
Table for storing strava athlete data: athlete id, name, etc.
'''
class Athlete(db.Model):
    __tablename__ = 'athletes'

    athlete_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(120), ForeignKey('users.name'), nullable=False)
    user = db.relationship('User', cascade='all,delete', backref=db.backref('athletes', cascade='all,delete', lazy=True))
    first_name = db.Column(db.String(120))
    last_name = db.Column(db.String(120))

    def __repr__(self):
        return '<id {}>'.format(self.athlete_id)