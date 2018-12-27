from strivial.database import db

'''
Table for storing strava user data: user name, tokens, expiry, etc.
'''
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    access_token = db.Column(db.String(120))
    refresh_token = db.Column(db.String(120))
    token_expires_at = db.Column(db.BigInteger())
    activity_access = db.Column(db.Boolean())

    def __init__(self, name=None, access_token=None, refresh_token=None, token_expires_at=None, activity_access=False):
        self.name = name
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_expires_at = token_expires_at
        self.activity_access = activity_access

    def __repr__(self):
        return '<id {}>'.format(self.id)