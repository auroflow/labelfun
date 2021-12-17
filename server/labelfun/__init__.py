import os

import click
from apiflask import APIFlask
from flask import current_app
from flask.cli import load_dotenv
from qiniu import Auth, BucketManager

from labelfun.apis import api_bp
from labelfun.extensions import db
from labelfun.models import UserType
from labelfun.models.task import Task, Entity
from labelfun.models.user import User
from labelfun.settings import config


def create_app(config_name=None):
    load_dotenv()
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
                'This operation will delete the database, do you want to '
                'continue?', abort=True)
            db.drop_all()
            click.echo('Drop tables.')
        db.create_all()
        click.echo('Initialized database.')

    @app.cli.command()
    def fakedb():
        """Fake users, tasks and entities."""
        db.session.commit()
        db.drop_all()
        db.create_all()
        access_key = os.getenv('QINIU_ACCESS_KEY')
        secret_key = os.getenv('QINIU_SECRET_KEY')
        q = Auth(access_key, secret_key)
        bucket = BucketManager(q)
        bucket_name = current_app.config['QINIU_BUCKET_NAME']

        def delete_prefix(prefix):
            marker = None
            while True:
                ret, eof, _ = bucket.list(bucket_name, prefix, marker)
                for item in ret.get('items'):
                    bucket.delete(bucket_name, item.get('key'))
                if not eof:
                    marker = ret.get('marker')
                else:
                    break

        delete_prefix("")

        user1 = User(id=1001, name='Amy', password='12345678',
                     email='amy@email.com', type=0)
        user2 = User(id=1002, name='Bob', password=r'!@#$%^&*',
                     email='bob@email.com', type=0)
        admin = User(id=2001, name='Admin', password='abcdefgh',
                     email='admin@email.com', type=1)

        # image1 = Entity(type=0, key='key1', thumb_key="t1", path='path1',
        #                 status=0)
        # image2 = Entity(type=0, key='key2', thumb_key="t2", path='path2',
        #                 status=0)
        # task1 = Task(id=101, status=0, published=True, name='task1',
        #              time=datetime.now(), type=0,
        #              labels=['flower', 'sun', 'sky'])
        # task1.creator = user1
        # task1.entities.append(image1)
        # task1.entities.append(image2)
        # sleep(0.01)
        # video1 = Entity(type=2, key='key3', thumb_key="t3", path='path3',
        #                 status=0)
        # video2 = Entity(type=2, key='key4', thumb_key="t4", path='path4',
        #                 status=1)
        # task2 = Task(id=102, status=0, name='task2', published=True,
        #              time=datetime.now(), type=2, labels=['dog', 'cat', 'bird'])
        # task2.creator = user2
        # task2.labeler = user1
        # task2.entities.append(video1)
        # task2.entities.append(video2)
        # sleep(0.01)
        # image5 = Entity(type=1, key='key5', thumb_key="t5", path='path5',
        #                 status=2)
        # image6 = Entity(type=1, key='key6', thumb_key="t6", path='path6',
        #                 status=2)
        # task3 = Task(id=103, status=2, name='task3', published=True,
        #              time=datetime.now(), type=1,
        #              labels=['water', 'air', 'fire'])
        # task3.creator = user1
        # task3.labeler = user2
        # task3.reviewer = admin
        # task3.entities.append(image5)
        # task3.entities.append(image6)

        db.session.add_all([user1, user2, admin])
        # db.session.add_all([image1, image2, task1,
        #                     video1, video2, task2])
        db.session.commit()
