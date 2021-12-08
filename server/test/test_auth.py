from flask import url_for, current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from labelfun.models.user import User
from test import BaseTestCase


class AuthTestCase(BaseTestCase):

    def test_login(self):
        num_users = User.query.count()
        response = self.client.post(
            url_for('api.auth.login'),
            json=dict(
                email='amy@email.com',
                password='12345678',
                grant_type="password"
            ),
            headers=self.set_headers()
        )
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['id'], 1001)
        self.assertEqual(data['email'], 'amy@email.com')
        self.assertEqual(data['type'], 'user')
        self.assertEqual(data['token_type'], 'Bearer')
        token = data['access_token']
        s = Serializer(current_app.config['SECRET_KEY'])
        token_id = s.loads(token)['id']
        self.assertEqual(token_id, 1001)

    def test_get_user_user_success(self):
        token = self.get_auth_token('amy@email.com', '12345678')
        response = self.client.get(
            url_for('api.user.user', user_id=1001),
            headers=self.set_headers(token)
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['id'], 1001)
        self.assertEqual(data['name'], 'Amy')
        self.assertEqual(data['email'], 'amy@email.com')
        self.assertEqual(data['type'], 'user')

    def test_get_user_admin_success(self):
        token = self.get_auth_token('admin@email.com', 'abcdefgh')
        response = self.client.get(
            url_for('api.user.user', user_id=1001),
            headers=self.set_headers(token)
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['id'], 1001)
        self.assertEqual(data['name'], 'Amy')
        self.assertEqual(data['email'], 'amy@email.com')
        self.assertEqual(data['type'], 'user')

    def test_get_user_fail(self):
        token = self.get_auth_token('amy@email.com', '12345678')
        response = self.client.get(
            url_for('api.user.user', user_id=2001),
            headers=self.set_headers(token)
        )
        self.assertEqual(response.status_code, 403)

    def test_create_user(self):
        response = self.client.post(
            url_for('api.user.users'), headers=self.set_headers(), json=dict(
                name="Another User",
                email="another@email.com",
                password="abcdefg1234'"
            )
        )
        self.assertEqual(response.status_code, 201)
        id = response.get_json()['id']
        token = self.get_auth_token('another@email.com', 'abcdefg1234\'')
        response = self.client.get(
            url_for('api.user.user', user_id=id),
            headers=self.set_headers(token)
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['name'], 'Another User')

    def test_patch_user_user_success(self):
        token = self.get_auth_token('amy@email.com', '12345678')
        response = self.client.patch(
            url_for('api.user.user', user_id=1001),
            headers=self.set_headers(token), json=dict(
                name="New Name",
                old_password="12345678"
            )
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.patch(
            url_for('api.user.user', user_id=1001),
            headers=self.set_headers(token), json=dict(
                email="newemail@email.com",
                new_password="123467abcd5'",
                old_password="12345678"
            )
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.get(
            url_for('api.user.user', user_id=1001),
            headers=self.set_headers(token)
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['email'], 'newemail@email.com')
        self.assertEqual(data['name'], 'New Name')
        self.get_auth_token("newemail@email.com", "123467abcd5'")

    def test_patch_user_admin_success(self):
        token = self.get_auth_token('admin@email.com', 'abcdefgh')
        response = self.client.patch(
            url_for('api.user.user', user_id=1001),
            headers=self.set_headers(token), json=dict(
                name="New Name",
            )
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.patch(
            url_for('api.user.user', user_id=1001),
            headers=self.set_headers(token), json=dict(
                email="newemail@email.com",
                new_password="123467abcd5'",
            )
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.get(
            url_for('api.user.user', user_id=1001),
            headers=self.set_headers(token)
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['email'], 'newemail@email.com')
        self.assertEqual(data['name'], 'New Name')
        self.get_auth_token("newemail@email.com", "123467abcd5'")

    def test_patch_user_duplicate_email_fail(self):
        token = self.get_auth_token('admin@email.com', 'abcdefgh')
        response = self.client.patch(
            url_for('api.user.user', user_id=1001),
            headers=self.set_headers(token), json=dict(
                email="bob@email.com"
            )
        )
        self.assertEqual(response.status_code, 400)
        error_msg = response.get_json()['message']
        self.assertEqual(error_msg, 'DUPLICATED_EMAIL')
