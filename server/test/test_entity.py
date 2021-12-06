from flask import url_for
from qiniu import put_file, urlsafe_base64_decode

from test import BaseTestCase


class TestTask(BaseTestCase):
    def test_tasks_get(self):
        token = self.get_auth_token('amy@email.com', '12345678')
        paths = ['C:\\Users\\imbiansl\\Desktop\\s1.jpg',
                 'C:\\Users\\imbiansl\\Desktop\\s2.jpg']
        response = self.client.post(
            url_for('api.entity.token'),
            headers=self.set_headers(token),
            json=dict(
                task_id=1,
                paths=paths
            )
        )
        credentials = response.get_json()['credentials']
        print(credentials)
        for i, cred in enumerate(credentials):
            ret, info = put_file(cred['token'], cred['key'], cred['path'],
                                 version='v2')
            key = str(urlsafe_base64_decode(ret['key']))
            task_id, path, time = key.split('&')
            print(task_id, path, time)
