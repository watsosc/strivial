from strivial.database import db

'''
This table is used to store strava activities: their id and essential info
'''
class Activity(db.Model):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.String(120), unique=True)

    def __init__(self, activity_id=None):
        self.activity_id = activity_id

    def __repr__(self):
        return '<id {}>'.format(self.id)