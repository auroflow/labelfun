import unittest

from flask import url_for, current_app
from labelfun import create_app, db
from labelfun.models import User
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from labelfun.settings import config


class AuthTestCase(unittest.TestCase):

    def setUp(self):
        app = create_app('testing')
        app.config.from_object(config['testing'])
        app.testing = True
        self.app_context = app.test_request_context()
        self.app_context.push()
        self.client = app.test_client()

    def tearDown(self):
        self.app_context.pop()

    def test_login(self):
        mydict = dict(
            key1="key1",
            key2="",
            key3=None,
        )
        response = self.client.post(
            url_for('api.hello'),
            json=mydict,
            headers=self.set_headers()
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        print(data)

    def set_headers(self, token=None):
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
