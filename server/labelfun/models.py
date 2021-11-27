# Source: https://github.com/authlib/example-oauth2-server/blob/master/website/oauth2.py

from labelfun.extensions import db
from passlib.hash import argon2


class User(db.Model):
    __name__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    pwdhash = db.Column(db.String)
    type = db.Column(db.String)

    def __init__(self, password=None, **kwargs):
        super(User, self).__init__(**kwargs)
        if password is not None:
            self.set_password(password)

    def __str__(self):
        return self.name

    def set_password(self, password):
        self.pwdhash = argon2.hash(password)

    def check_password(self, password):
        return argon2.verify(password, self.pwdhash)
