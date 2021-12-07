from flask import url_for
from qiniu import put_file, urlsafe_base64_decode

from test import BaseTestCase


class TestTask(BaseTestCase):
    def test_get_token(self):
        token = self.get_auth_token('amy@email.com', '12345678')
        paths = ['C:\\Users\\imbiansl\\Desktop\\s1.jpg',
                 'C:\\Users\\imbiansl\\Desktop\\s2.jpg']
        response = self.client.post(
            url_for('api.entity.entities'),
            headers=self.set_headers(token),
            json=dict(
                task_id=101,
                paths=paths
            )
        )
        self.assertEqual(response.status_code, 201)
        credentials = response.get_json()['credentials']
        ret_paths = list()
        for i, cred in enumerate(credentials):
            ret, info = put_file(cred['token'], cred['key'], cred['path'],
                                 version='v2')
            key = urlsafe_base64_decode(ret['key'])
            task_id, path, time = key.split(b'&')
            ret_paths.append(path.decode())
        self.assertEqual(paths, ret_paths)
