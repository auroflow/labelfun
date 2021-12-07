from flask import url_for

from test import BaseTestCase


class TestTaskLifeCycle(BaseTestCase):

    def test_task_life_cycle(self):

        def check_returned_dict(retval: dict, **kwargs):
            for key, val in kwargs.items():
                if isinstance(val, tuple):
                    target = retval[key]
                    for item in val[:-1]:
                        target = target[item]
                    self.assertEqual(target, val[-1])
                else:
                    self.assertEqual(retval[key], val, msg="key is %s" % key)

        # Amy created a task
        token = self.get_auth_token('amy@email.com', '12345678')
        response = self.client.post(
            url_for('api.task.tasks'),
            headers=self.set_headers(token),
            json=dict(
                name="Amy's New Task",
                type="image_seg",
                labels=['phone', 'book', 'shelf']
            )
        )
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        task_id = data['id']
        check_returned_dict(data,
                            name="Amy's New Task",
                            type="image_seg",
                            status="unlabeled",
                            published=False,
                            labeled_count=0,
                            reviewed_count=0,
                            label_done=True,
                            review_done=True,
                            creator=('id', 1001),
                            labeler=None,
                            reviewer=None,
                            labels=['phone', 'book', 'shelf'],
                            entities=[])

        # Amy added some entities
        paths = ['C:\\Users\\imbiansl\\Desktop\\s1.jpg',
                 'C:\\Users\\imbiansl\\Desktop\\s2.jpg']
        response = self.client.post(
            url_for('api.entity.entities'),
            headers=self.set_headers(token),
            json=dict(
                task_id=task_id,
                paths=paths
            )
        )
        self.assertEqual(response.status_code, 201)
        creds = response.get_json()['credentials']
        entities_id = [cred['id'] for cred in creds]
        entities_path = [cred['path'] for cred in creds]
        entities_key = [cred['key'] for cred in creds]
        for cred in creds:
            self.assertTrue('token' in cred)
        self.assertEqual(paths, entities_path)

        # Amy changes the name, and publishes the task
        response = self.client.put(
            url_for('api.task.task', task_id=task_id),
            headers=self.set_headers(token),
            json=dict(
                name="Amy's New Task Name",
                published=True
            )
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        check_returned_dict(data,
                            name="Amy's New Task Name",
                            type="image_seg",
                            status="unlabeled",
                            published=True,
                            entity_count=2,
                            labeled_count=0,
                            reviewed_count=0,
                            label_done=False,
                            review_done=False,
                            creator=('id', 1001),
                            labeler=None,
                            reviewer=None,
                            entities=(0, 'key', entities_key[0]),
                            labels=['phone', 'book', 'shelf'])

        # Amy cannot add more entities
        paths = ['C:\\Users\\imbiansl\\Desktop\\no-you-cant.jpg']
        response = self.client.post(
            url_for('api.entity.entities'),
            headers=self.set_headers(token),
            json=dict(
                task_id=task_id,
                paths=paths
            )
        )
        self.assertEqual(response.status_code, 400)
        message = response.get_json()['message']
        self.assertEqual(message, 'TASK_PUBLISHED')

        # Bob claims the label task
        token = self.get_auth_token('bob@email.com', '!@#$%^&*')
        response = self.client.post(
            url_for('api.task.task', task_id=task_id),
            headers=self.set_headers(token),
            json=dict(
                type='label'
            )
        )
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        check_returned_dict(data,
                            name="Amy's New Task Name",
                            type="image_seg",
                            status="unlabeled",
                            published=True,
                            entity_count=2,
                            labeled_count=0,
                            reviewed_count=0,
                            label_done=False,
                            review_done=False,
                            creator=('id', 1001),
                            labeler=('id', 1002),
                            reviewer=None,
                            entities=(0, 'key', entities_key[0]),
                            labels=['phone', 'book', 'shelf'])

        # Bob labels two entities
        response = self.client.post(
            url_for('api.entity.entity', entity_id=entities_id[0]),
            headers=self.set_headers(token),
            json=dict(
                annotation="annotation #1"
            )
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        check_returned_dict(data,
                            id=entities_id[0],
                            key=entities_key[0],
                            type='image_seg',
                            status='unreviewed',
                            annotation='annotation #1',
                            frames=[])
        response = self.client.post(
            url_for('api.entity.entity', entity_id=entities_id[1]),
            headers=self.set_headers(token),
            json=dict(
                annotation="annotation #2"
            )
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        check_returned_dict(data,
                            id=entities_id[1],
                            key=entities_key[1],
                            type='image_seg',
                            status='unreviewed',
                            annotation='annotation #2',
                            frames=[])

        # Bob reverts annotation to 1
        response = self.client.post(
            url_for('api.entity.entity', entity_id=entities_id[0]),
            headers=self.set_headers(token),
            json=dict(
                annotation=""
            )
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        check_returned_dict(data,
                            id=entities_id[0],
                            key=entities_key[0],
                            type='image_seg',
                            status='unlabeled',
                            annotation=None,
                            frames=[])

        # Bob cannot finish task yet
        token = self.get_auth_token('bob@email.com', '!@#$%^&*')
        response = self.client.patch(
            url_for('api.task.task', task_id=task_id),
            headers=self.set_headers(token),
            json=dict(
                type='label'
            )
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['message'],
                         'JOB_IS_NOT_DONE')

        # Bob changes 1, reverts 2
        response = self.client.post(
            url_for('api.entity.entity', entity_id=entities_id[0]),
            headers=self.set_headers(token),
            json=dict(
                annotation="annotation #3"
            )
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        check_returned_dict(data,
                            id=entities_id[0],
                            key=entities_key[0],
                            type='image_seg',
                            status='unreviewed',
                            annotation='annotation #3',
                            frames=[])
        response = self.client.post(
            url_for('api.entity.entity', entity_id=entities_id[1]),
            headers=self.set_headers(token),
            json=dict(
                annotation="annotation #4"
            )
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        check_returned_dict(data,
                            id=entities_id[1],
                            key=entities_key[1],
                            type='image_seg',
                            status='unreviewed',
                            annotation='annotation #4',
                            frames=[])
        response = self.client.get(
            url_for('api.task.task', task_id=task_id),
            headers=self.set_headers(token),
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        check_returned_dict(data,
                            name="Amy's New Task Name",
                            type="image_seg",
                            status="unlabeled",
                            published=True,
                            entity_count=2,
                            labeled_count=2,
                            reviewed_count=0,
                            label_done=True,
                            review_done=False,
                            creator=('id', 1001),
                            labeler=('id', 1002),
                            reviewer=None,
                            entities=(0, 'key', entities_key[0]),
                            labels=['phone', 'book', 'shelf'])

        # Bob finishes task
        token = self.get_auth_token('bob@email.com', '!@#$%^&*')
        response = self.client.patch(
            url_for('api.task.task', task_id=task_id),
            headers=self.set_headers(token),
            json=dict(
                type='label'
            )
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        check_returned_dict(data,
                            name="Amy's New Task Name",
                            type="image_seg",
                            status="unreviewed",
                            published=True,
                            entity_count=2,
                            labeled_count=2,
                            reviewed_count=0,
                            label_done=True,
                            review_done=False,
                            creator=('id', 1001),
                            labeler=('id', 1002),
                            reviewer=None,
                            entities=(0, 'key', entities_key[0]),
                            labels=['phone', 'book', 'shelf'])

        # Bob cannot label again
        response = self.client.post(
            url_for('api.entity.entity', entity_id=entities_id[0]),
            headers=self.set_headers(token),
            json=dict(
                annotation="annotation #4"
            )
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['message'],
                         'TASK_IS_NOT_UNLABELED')

        # Admin takes the review task
        token = self.get_auth_token('admin@email.com', 'abcdefgh')
        response = self.client.post(
            url_for('api.task.task', task_id=task_id),
            headers=self.set_headers(token),
            json=dict(
                type='review'
            )
        )
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        check_returned_dict(data,
                            name="Amy's New Task Name",
                            type="image_seg",
                            status="unreviewed",
                            published=True,
                            entity_count=2,
                            labeled_count=2,
                            reviewed_count=0,
                            label_done=True,
                            review_done=False,
                            creator=('id', 1001),
                            labeler=('id', 1002),
                            reviewer=('id', 2001),
                            entities=(0, 'key', entities_key[0]),
                            labels=['phone', 'book', 'shelf'])

        # Admin reviews entities (1 is correct 2 is not)
        response = self.client.put(
            url_for('api.entity.entity', entity_id=entities_id[0]),
            headers=self.set_headers(token),
            json=dict(
                review='correct'
            )
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        check_returned_dict(data,
                            id=entities_id[0],
                            key=entities_key[0],
                            type='image_seg',
                            status='done',
                            annotation='annotation #3',
                            frames=[])
        response = self.client.put(
            url_for('api.entity.entity', entity_id=entities_id[1]),
            headers=self.set_headers(token),
            json=dict(
                review='incorrect'
            )
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        check_returned_dict(data,
                            id=entities_id[1],
                            key=entities_key[1],
                            type='image_seg',
                            status='unlabeled',
                            annotation=None,
                            frames=[])

        # Admin finishes task
        response = self.client.patch(
            url_for('api.task.task', task_id=task_id),
            headers=self.set_headers(token),
            json=dict(
                type='review'
            )
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        check_returned_dict(data,
                            name="Amy's New Task Name",
                            type="image_seg",
                            status="unlabeled",
                            published=True,
                            entity_count=2,
                            labeled_count=1,
                            reviewed_count=1,
                            label_done=False,
                            review_done=False,
                            creator=('id', 1001),
                            labeler=('id', 1002),
                            reviewer=('id', 2001),
                            entities=(0, 'key', entities_key[0]),
                            labels=['phone', 'book', 'shelf'])

        # Bob cannot label 1 again
        token = self.get_auth_token('bob@email.com', '!@#$%^&*')
        response = self.client.post(
            url_for('api.entity.entity', entity_id=entities_id[0]),
            headers=self.set_headers(token),
            json=dict(
                annotation="annotation #5"
            )
        )
        self.assertEqual(response.status_code, 400)
        message = response.get_json()['message']
        self.assertEqual(message, 'ENTITY_IS_NOT_UNLABELED_NOR_UNREVIEWED')

        # Bob labels 2 again
        token = self.get_auth_token('bob@email.com', '!@#$%^&*')
        response = self.client.post(
            url_for('api.entity.entity', entity_id=entities_id[1]),
            headers=self.set_headers(token),
            json=dict(
                annotation="annotation #5"
            )
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        check_returned_dict(data,
                            id=entities_id[1],
                            key=entities_key[1],
                            type='image_seg',
                            status='unreviewed',
                            annotation='annotation #5',
                            frames=[])

        # Bob finishes task again
        response = self.client.patch(
            url_for('api.task.task', task_id=task_id),
            headers=self.set_headers(token),
            json=dict(
                type='label'
            )
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        check_returned_dict(data,
                            name="Amy's New Task Name",
                            type="image_seg",
                            status="unreviewed",
                            published=True,
                            entity_count=2,
                            labeled_count=2,
                            reviewed_count=1,
                            label_done=True,
                            review_done=False,
                            creator=('id', 1001),
                            labeler=('id', 1002),
                            reviewer=('id', 2001),
                            entities=(0, 'key', entities_key[0]),
                            labels=['phone', 'book', 'shelf'])

        # Admin cannot review 1 again
        token = self.get_auth_token('admin@email.com', 'abcdefgh')
        response = self.client.put(
            url_for('api.entity.entity', entity_id=entities_id[0]),
            headers=self.set_headers(token),
            json=dict(
                review='correct'
            )
        )
        self.assertEqual(response.status_code, 400)
        message = response.get_json()['message']
        self.assertEqual(message, 'ENTITY_IS_NOT_UNREVIEWED')

        # Admin reviews 2 again
        response = self.client.put(
            url_for('api.entity.entity', entity_id=entities_id[1]),
            headers=self.set_headers(token),
            json=dict(
                review='correct'
            )
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        check_returned_dict(data,
                            id=entities_id[1],
                            key=entities_key[1],
                            type='image_seg',
                            status='done',
                            annotation='annotation #5',
                            frames=[])

        # Admin finishes task; hurray!
        response = self.client.patch(
            url_for('api.task.task', task_id=task_id),
            headers=self.set_headers(token),
            json=dict(
                type='review'
            )
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        check_returned_dict(data,
                            name="Amy's New Task Name",
                            type="image_seg",
                            status="done",
                            published=True,
                            entity_count=2,
                            labeled_count=2,
                            reviewed_count=2,
                            label_done=True,
                            review_done=True,
                            creator=('id', 1001),
                            labeler=('id', 1002),
                            reviewer=('id', 2001),
                            entities=(0, 'key', entities_key[0]),
                            labels=['phone', 'book', 'shelf'])
