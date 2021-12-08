from flask import url_for

from test import BaseTestCase


class HelloTestCase(BaseTestCase):

    def test_hello(self):
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
