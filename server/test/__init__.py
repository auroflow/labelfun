import os
import unittest
from datetime import datetime
from time import sleep

from flask import url_for

from labelfun import create_app
from labelfun.extensions import db
from labelfun.models.entity import Entity
from labelfun.models.task import Task
from labelfun.models.user import User
from labelfun.settings import config


class BaseTestCase(unittest.TestCase):

    def setUp(self):

        app = create_app('testing')
        app.config.from_object(config['testing'])
        self.assertEqual(app.config['QINIU_ACCESS_KEY'],
                         os.getenv('QINIU_ACCESS_KEY'))
        app.testing = True
        self.app_context = app.test_request_context()
        self.app_context.push()
        self.fakedb()
        self.client = app.test_client()

    @staticmethod
    def fakedb():
        db.session.commit()
        db.drop_all()
        db.create_all()
        user1 = User(id=1001, name='Amy', password='12345678',
                     email='amy@email.com', type=0)
        user2 = User(id=1002, name='Bob', password=r'!@#$%^&*',
                     email='bob@email.com', type=0)
        admin = User(id=2001, name='Admin', password='abcdefgh',
                     email='admin@email.com', type=1)

        image1 = Entity(type=0, key='key1', thumb_key="t1",
                        status=0)
        image2 = Entity(type=0, key='key2', thumb_key="t2",
                        status=0)
        task1 = Task(id=101, status=0, published=True, name='task1',
                     time=datetime.now(), type=0,
                     labels=['flower', 'sun', 'sky'])
        task1.creator = user1
        task1.entities.append(image1)
        task1.entities.append(image2)
        sleep(0.01)
        video1 = Entity(type=2, key='key3', thumb_key="t3",
                        status=0)
        video2 = Entity(type=2, key='key4', thumb_key="t4",
                        status=1)
        task2 = Task(id=102, status=0, name='task2', published=True,
                     time=datetime.now(), type=2, labels=['dog', 'cat', 'bird'])
        task2.creator = user2
        task2.labeler = user1
        task2.entities.append(video1)
        task2.entities.append(video2)
        sleep(0.01)
        image5 = Entity(type=1, key='key5', thumb_key="t5",
                        status=2)
        image6 = Entity(type=1, key='key6', thumb_key="t6",
                        status=2)
        task3 = Task(id=103, status=2, name='task3', published=True,
                     time=datetime.now(), type=1,
                     labels=['water', 'air', 'fire'])
        task3.creator = user1
        task3.labeler = user2
        task3.reviewer = admin
        task3.entities.append(image5)
        task3.entities.append(image6)

        db.session.add_all([user1, user2, admin, image1, image2, task1,
                            video1, video2, task2])
        db.session.commit()

    def get_auth_token(self, email, password):
        response = self.client.post(url_for('api.auth.login'), json=dict(
            email=email,
            password=password,
            grant_type="password"
        ))
        return response.get_json()['access_token']

    @staticmethod
    def set_headers(token=None):
        if token is None:
            return {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        else:
            return {
                'Authorization': 'Bearer ' + token,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
