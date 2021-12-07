from datetime import datetime

from flask import url_for

from labelfun.extensions import db
from labelfun.models import JobStatus
from labelfun.models.entity import Entity
from labelfun.models.task import Task
from test import BaseTestCase


class TestTask(BaseTestCase):

    def test_tasks_get(self):
        token = self.get_auth_token('amy@email.com', '12345678')

        # filter creator
        response = self.client.get(
            url_for('api.task.tasks'),
            headers=self.set_headers(token),
            query_string=dict(
                creator=1001
            )
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        tasks = data['tasks']
        pagination = data['pagination']
        self.assertEqual(pagination['total'], 2)
        tasks_id = {task['id'] for task in tasks}
        self.assertEqual(tasks_id, {101, 103})

        # filter labeler
        response = self.client.get(
            url_for('api.task.tasks'),
            headers=self.set_headers(token),
            query_string=dict(
                labeler=1001
            )
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        tasks = data['tasks']
        self.assertEqual(len(tasks), 1)
        tasks_id = {task['id'] for task in tasks}
        self.assertEqual(tasks_id, {102})

        # filter reviewer
        response = self.client.get(
            url_for('api.task.tasks'),
            headers=self.set_headers(token),
            query_string=dict(
                reviewer=2001
            )
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        tasks = data['tasks']
        self.assertEqual(len(tasks), 1)
        tasks_id = {task['id'] for task in tasks}
        self.assertEqual(tasks_id, {103})

        # filter pagination
        response = self.client.get(
            url_for('api.task.tasks'),
            headers=self.set_headers(token),
            query_string=dict(
                per_page=2
            )
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        tasks = data['tasks']
        self.assertEqual(len(tasks), 2)
        pagination = data['pagination']
        self.assertEqual(pagination['total'], 3)
        self.assertEqual(pagination['pages'], 2)
        next = pagination['next']
        response = self.client.get(
            next,
            headers=self.set_headers(token),
        )
        self.assertEqual(response.status_code, 200)
        tasks = response.get_json()['tasks']
        self.assertEqual(len(tasks), 1)
        pagination = response.get_json()['pagination']
        self.assertEqual(pagination['page'], 2)

        # test order
        response = self.client.get(
            url_for('api.task.tasks'),
            headers=self.set_headers(token),
            query_string=dict(
                order='asc'
            )
        )
        times = [task['time'] for task in response.get_json()['tasks']]
        self.assertTrue(all(a <= b for a, b in zip(times, times[1:])))

        # test desc order
        response = self.client.get(
            url_for('api.task.tasks'),
            headers=self.set_headers(token),
            query_string=dict(
                order='desc'
            )
        )
        times = [task['time'] for task in response.get_json()['tasks']]
        self.assertTrue(all(a >= b for a, b in zip(times, times[1:])))

    def test_task_get(self):
        token = self.get_auth_token('amy@email.com', '12345678')
        response = self.client.get(
            url_for('api.task.task', task_id=101),
            headers=self.set_headers(token)
        )
        self.assertEqual(response.status_code, 200)
        task = response.get_json()
        self.assertEqual(task['id'], 101)
        self.assertEqual(task['status'], 'unlabeled')
        self.assertEqual(task['type'], 'image_cls')
        entities = task['entities']
        self.assertIsNotNone(entities)
        self.assertEqual(len(entities), 2)
        entity = entities[0]
        self.assertEqual(entity['key'], 'key1')

    def test_task_get_status_and_counts(self):
        # Create an empty task
        token = self.get_auth_token('amy@email.com', '12345678')
        response = self.client.post(
            url_for('api.task.tasks'),
            headers=self.set_headers(token),
            json=dict(
                name="New Task #1",
                type="image_seg",
                labels=['bottle', 'tissue', 'earphone'],
            )
        )
        self.assertEqual(response.status_code, 201)
        id = response.get_json()['id']

        # Test status = empty, counts = 0
        response = self.client.get(
            url_for('api.task.task', task_id=id),
            headers=self.set_headers(token)
        )
        self.assertEqual(response.status_code, 200)
        task = response.get_json()
        self.assertEqual(task['id'], id)
        self.assertEqual(task['creator']['email'], 'amy@email.com')
        self.assertIsNotNone(datetime.fromisoformat(task['time']))
        self.assertEqual(task['published'], False)
        self.assertEqual(task['status'], 'unlabeled')
        self.assertEqual(task['name'], 'New Task #1')
        self.assertEqual(task['type'], 'image_seg')
        self.assertEqual(task['entity_count'], 0)
        self.assertEqual(task['labeled_count'], 0)
        self.assertEqual(task['reviewed_count'], 0)
        self.assertEqual(task['labels'], ['bottle', 'tissue', 'earphone'])

        # Add some entities
        paths = ['C:\\Users\\imbiansl\\Desktop\\s1.jpg',
                 'C:\\Users\\imbiansl\\Desktop\\s2.jpg']
        response = self.client.post(
            url_for('api.entity.entities'),
            headers=self.set_headers(token),
            json=dict(
                task_id=id,
                paths=paths
            )
        )

        entities_id = [cred['id'] for cred in
                       response.get_json()['credentials']]

        # Test status = unlabeled, entity_count = 2
        response = self.client.get(
            url_for('api.task.task', task_id=id),
            headers=self.set_headers(token)
        )
        self.assertEqual(response.status_code, 200)
        task = response.get_json()
        self.assertEqual(task['status'], 'unlabeled')
        self.assertEqual(task['entity_count'], 2)
        self.assertEqual(task['labeled_count'], 0)
        self.assertEqual(task['reviewed_count'], 0)

        # Label 2, review 1
        Task.query.get(id).status = JobStatus.UNREVIEWED
        Task.query.get(id).labeler_id = 1002
        Task.query.get(id).reviewer_id = 2001
        entities = Entity.query.filter(Entity.id.in_(entities_id)).all()
        self.assertEqual(len(entities), 2)
        entities[0].status = JobStatus.UNREVIEWED
        entities[1].status = JobStatus.UNREVIEWED
        entities[1].status = JobStatus.DONE
        db.session.commit()

        # Test status = unlabeled, entity_count = 2
        response = self.client.get(
            url_for('api.task.task', task_id=id),
            headers=self.set_headers(token)
        )
        self.assertEqual(response.status_code, 200)
        task = response.get_json()
        self.assertEqual(task['status'], 'unreviewed')
        self.assertEqual(task['entity_count'], 2)
        self.assertEqual(task['labeled_count'], 2)
        self.assertEqual(task['reviewed_count'], 1)
        self.assertEqual(task['labeler']['email'], 'bob@email.com')
        self.assertEqual(task['reviewer']['email'], 'admin@email.com')
        self.assertEqual(task['label_done'], True)
        self.assertEqual(task['review_done'], False)

        # Label 2, review 2
        entities = Entity.query.filter(Entity.id.in_(entities_id)).all()
        self.assertEqual(len(entities), 2)
        entities[0].status = JobStatus.DONE
        Task.query.get(id).status = JobStatus.DONE
        db.session.commit()

        # Test status = unlabeled, entity_count = 2
        response = self.client.get(
            url_for('api.task.task', task_id=id),
            headers=self.set_headers(token)
        )
        self.assertEqual(response.status_code, 200)
        task = response.get_json()
        self.assertEqual(task['status'], 'done')
        self.assertEqual(task['entity_count'], 2)
        self.assertEqual(task['labeled_count'], 2)
        self.assertEqual(task['reviewed_count'], 2)
        self.assertEqual(task['label_done'], True)
        self.assertEqual(task['review_done'], True)

    def test_task_post(self):
        token = self.get_auth_token('amy@email.com', '12345678')
        response = self.client.post(
            url_for('api.task.tasks'),
            headers=self.set_headers(token),
            json=dict(
                name="New Task #1",
                type="image_seg",
                labels=['bottle', 'tissue', 'earphone'],
            )
        )
        self.assertEqual(response.status_code, 201)
        task = response.get_json()
        self.assertEqual(task['creator']['name'], 'Amy')
        self.assertEqual(task['status'], 'unlabeled')
        self.assertEqual(task['type'], 'image_seg')
        entities = task['entities']
        self.assertEqual(len(entities), 0)
        labels = task['labels']
        self.assertEqual(len(labels), 3)
        self.assertEqual(labels[2], 'earphone')

    def test_task_delete(self):
        token = self.get_auth_token('amy@email.com', '12345678')
        response = self.client.delete(
            url_for('api.task.task', task_id=101),
            headers=self.set_headers(token)
        )
        self.assertEqual(response.status_code, 204)
        task = Task.query.get(1)
        self.assertIsNone(task)

    def test_task_delete_unauthorized_fail(self):
        token = self.get_auth_token('bob@email.com', r'!@#$%^&*')
        response = self.client.delete(
            url_for('api.task.task', task_id=101),
            headers=self.set_headers(token)
        )
        self.assertEqual(response.status_code, 403)

    def test_task_claim(self):
        pass
