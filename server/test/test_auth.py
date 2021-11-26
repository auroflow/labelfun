import unittest

from flask import url_for, current_app
from labelfun import create_app, db
from labelfun.models.user import User
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from passlib.hash import argon2
from labelfun.settings import config


class AuthTestCase(unittest.TestCase):

    def setUp(self):
        app = create_app('testing')
        app.config.from_object(config['testing'])
        self.app_context = app.test_request_context()
        self.app_context.push()
        db.drop_all()
        db.create_all()
        self.client = app.test_client()
        user = User(id=1001, name='Justin Liu', pwdhash=argon2.hash('12345678'),
                    email='imbiansl@live.cn', type='user')
        admin = User(id=2001, name='Amy Admin', pwdhash=argon2.hash('abcdefgh'),
                     email='amyadmin@live.cn', type='admin')
        db.session.add(user)
        db.session.add(admin)
        db.session.commit()

    def tearDown(self):
        db.drop_all()
        self.app_context.pop()

    def test_login(self):
        num_users = User.query.count()
        response = self.client.post(
            url_for('api.auth.login'),
            json=dict(
                email='imbiansl@live.cn',
                password='12345678',
                grant_type="password"
            ),
            headers=self.set_headers()
        )
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['id'], 1001)
        self.assertEqual(data['email'], 'imbiansl@live.cn')
        self.assertEqual(data['type'], 'user')
        self.assertEqual(data['token_type'], 'Bearer')
        token = data['access_token']
        s = Serializer(current_app.config['SECRET_KEY'])
        token_id = s.loads(token)['id']
        self.assertEqual(token_id, 1001)

    def test_auth_user_success(self):
        token = self.get_auth_token('imbiansl@live.cn', '12345678')
        response = self.client.get(
            url_for('api.user.user', user_id=1001),
            headers=self.set_headers(token)
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['id'], 1001)
        self.assertEqual(data['name'], 'Justin Liu')
        self.assertEqual(data['email'], 'imbiansl@live.cn')
        self.assertEqual(data['type'], 'user')

    def test_auth_admin_success(self):
        token = self.get_auth_token('amyadmin@live.cn', 'abcdefgh')
        response = self.client.get(
            url_for('api.user.user', user_id=1001),
            headers=self.set_headers(token)
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['id'], 1001)
        self.assertEqual(data['name'], 'Justin Liu')
        self.assertEqual(data['email'], 'imbiansl@live.cn')
        self.assertEqual(data['type'], 'user')

    def test_auth_fail(self):
        token = self.get_auth_token('imbiansl@live.cn', '12345678')
        response = self.client.get(
            url_for('api.user.user', user_id=2001),
            headers=self.set_headers(token)
        )
        self.assertEqual(response.status_code, 403)

    def get_auth_token(self, email, password):
        response = self.client.post(url_for('api.auth.login'), json=dict(
            email=email,
            password=password,
            grant_type="password"
        ))
        return response.get_json()['access_token']

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
