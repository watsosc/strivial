from strivial.database import db

'''
Table for storing strava athlete data: athlete id, name, etc.
'''
class Athlete(db.Model):
    __tablename__ = 'athletes'

    athlete_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120))
    last_name = db.Column(db.String(120))

    def __repr__(self):
        return '<id {}>'.format(self.athlete_id)