# Source: https://github.com/authlib/example-oauth2-server/blob/master/website/oauth2.py

from passlib.hash import argon2

from labelfun.extensions import db


class User(db.Model):
    __tablename__ = 'user'

    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String, nullable=False)
    email: str = db.Column(db.String, nullable=False)
    pwdhash: str = db.Column(db.String, nullable=False)
    type = db.Column(db.Integer, nullable=False)

    created_tasks = db.relationship('Task', foreign_keys='[Task.creator_id]',
                                    back_populates='creator')
    labeled_tasks = db.relationship('Task', foreign_keys='[Task.labeler_id]',
                                    back_populates='labeler')
    reviewed_tasks = db.relationship('Task', foreign_keys='[Task.reviewer_id]',
                                     back_populates='reviewer')

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
