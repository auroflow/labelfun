import os

import click
from apiflask import APIFlask
from labelfun.settings import config
from labelfun.apis import api_bp
from labelfun.extensions import db
from labelfun.models import User


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
        user = User(id=1001, name='User', password='12345678',
                    email='user@email.com', type='user')
        user2 = User(id=1002, name='New User', password=r'!@#$%^&*',
                     email='newuser@email.com', type='user')
        admin = User(id=2001, name='Admin', password='abcdefgh',
                     email='admin@email.com', type='admin')

        db.drop_all()
        db.create_all()
        db.session.add(user)
        db.session.add(user2)
        db.session.add(admin)
        db.session.commit()
