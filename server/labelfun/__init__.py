import os

import click
from apiflask import APIFlask
from labelfun.settings import config
from labelfun.apis import api_bp
from labelfun.extensions import db
from labelfun.models.user import User
from passlib.hash import argon2


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = APIFlask('labelfun')
    app.config.from_object(config[config_name])

    register_blueprints(app)
    register_extensions(app)
    register_commands(app)

    return app


def register_blueprints(app: APIFlask):
    app.register_blueprint(api_bp, url_prefix="/api")


def register_extensions(app: APIFlask):
    db.init_app(app)


def register_commands(app: APIFlask):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def initdb(drop):
        """Initialize the database."""
        if drop:
            click.confirm(
                'This operation will delete the database, do you want to continue?', abort=True)
            db.drop_all()
            click.echo('Drop tables.')
        db.create_all()
        click.echo('Initialized database.')

    @app.cli.command()
    def fakedb():
        """Fake users."""
        user = User(id=1001, name="Justin Liu", email="imbiansl@live.cn",
                    pwdhash=argon2.hash('12345678'), type="user")
        admin = User(id=2001, name='Amy Admin', pwdhash=argon2.hash('abcdefgh'),
                     email='amyadmin@live.cn', type='admin')
        db.drop_all()
        db.create_all()
        db.session.add(user)
        db.session.add(admin)
        db.session.commit()
