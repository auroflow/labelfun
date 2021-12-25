from datetime import datetime

from apiflask import APIBlueprint, input, output, abort, pagination_builder
from apiflask.schemas import EmptySchema
from flask import g, current_app, send_file
from flask.views import MethodView
from qiniu import BucketManager, Auth
from sqlalchemy import desc

from labelfun.apis.auth import auth_required
from labelfun.extensions import db
from labelfun.fiftyone import export_task
from labelfun.models import UserType, TaskType, JobStatus
from labelfun.models.task import Task
from labelfun.schemas.task import TaskOutSchema, TasksOutSchema, TaskInSchema, \
    TasksQuerySchema, TaskProcessInSchema, TaskModifyInSchema, ExportInSchema

task_bp = APIBlueprint('task', __name__)


@task_bp.route('/<int:task_id>', endpoint="task")
class TaskView(MethodView):

    @output(TaskOutSchema)
    @auth_required()
    def get(self, task_id):
        """Get a task."""
        task = Task.query.get_or_404(task_id)
        user = g.current_user
        if not task.published:
            if task.creator != user and user.type != UserType.ADMIN:
                abort(403, 'TASK_UNPUBLISHED')
        return task

    @input(TaskProcessInSchema)
    @output(TaskOutSchema, 201)
    @auth_required()
    def post(self, task_id, data):
        """Claim a task."""
        task = Task.query.get_or_404(task_id)
        user = g.current_user
        if not task.published:
            abort(400, 'TASK_UNPUBLISHED')
        if data['type'] == 'label':
            if task.labeler is not None:
                abort(400, 'TASK_UNDERTAKEN')
            task.labeler = user
        else:  # 'review'
            if task.status != JobStatus.UNREVIEWED:
                abort(400, 'TASK_NOT_LABELED')
            if task.reviewer is not None:
                abort(400, 'TASK_UNDERTAKEN')
            task.reviewer = user
        db.session.commit()
        return task

    @input(TaskModifyInSchema)
    @output(TaskOutSchema, 200)
    @auth_required()
    def put(self, task_id, data):
        """Modify or publish a task."""
        task = Task.query.get_or_404(task_id)
        user = g.current_user
        if user.type != UserType.ADMIN and task.creator != user:
            abort(403)
        if task.published:
            abort(400, "TASK_PUBLISHED")
        if data.get('published') is not None and not len(task.entities):
            abort(400, "NO_ENTITIES")

        task.name = data.get('name', task.name)
        if 'labels' in data:
            task.labels = ','.join(data['labels'])
        task.published = data.get('published', task.published)
        db.session.commit()
        return task

    @input(TaskProcessInSchema)
    @output(TaskOutSchema, 200)
    @auth_required()
    def patch(self, task_id, data):
        """Complete a claimed task."""
        task = Task.query.get_or_404(task_id)
        user = g.current_user
        if data['type'] == 'label':
            if task.labeler != user and user.type != UserType.ADMIN:
                abort(403)
            if task.status != JobStatus.UNLABELED:
                abort(400, 'TASK_STATUS_IS_NOT_UNLABELED')
            if len(task.entities) != task.labeled_count:
                abort(400, 'JOB_IS_NOT_DONE')
            task.status = JobStatus.UNREVIEWED
        else:  # 'review'
            if task.reviewer != user and user.type != UserType.ADMIN:
                abort(403)
            if task.status != JobStatus.UNREVIEWED:
                abort(400, 'TASK_STATUS_IS_NOT_UNREVIEWED')
            if task.reviewed_count != len(task.entities):
                abort(400, 'JOB_IS_NOT_DONE')
            for entity in task.entities:
                if entity.status == JobStatus.REVIEWED:
                    if entity.review:
                        entity.status = JobStatus.DONE
                    else:
                        entity.status = JobStatus.UNLABELED
                        entity.annotation = None
                        task.reviewed_count -= 1
                        task.labeled_count -= 1
            if task.reviewed_count == len(task.entities):
                task.status = JobStatus.DONE
            else:
                task.status = JobStatus.UNLABELED
        db.session.commit()
        return task

    @output(EmptySchema, 204)
    @auth_required()
    def delete(self, task_id):
        """Deletes a task."""
        task = Task.query.get(task_id)
        if task is None:
            abort(404)
        if g.current_user.id != task.creator_id and g.current_user.type != UserType.ADMIN:
            abort(403, message="UNAUTHORIZED")

        access_key = current_app.config['QINIU_ACCESS_KEY']
        secret_key = current_app.config['QINIU_SECRET_KEY']
        q = Auth(access_key, secret_key)
        bucket = BucketManager(q)
        bucket_name = current_app.config['QINIU_BUCKET_NAME']
        for entity in task.entities:
            if entity.uploaded:
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

                delete_prefix(entity.key)
                delete_prefix(entity.thumb_key)

            db.session.delete(entity)
        db.session.delete(task)
        db.session.commit()
        return {}


@task_bp.route('', endpoint='tasks')
class TasksView(MethodView):

    @input(TasksQuerySchema, location='query')
    @output(TasksOutSchema)
    @auth_required()
    def get(self, query):
        """Get task list."""
        tasks = Task.query

        tipe = query.get('type')
        if tipe is not None:
            task_type: TaskType = eval('TaskType.' + tipe.upper())
            tasks = tasks.filter_by(type=task_type)

        creator_id = query.get('creator')
        if creator_id is not None:
            tasks = tasks.filter_by(creator_id=creator_id)

        labeler_id = query.get('labeler')
        if labeler_id is not None:
            tasks = tasks.filter_by(labeler_id=labeler_id)

        reviewer_id = query.get('reviewer')
        if reviewer_id is not None:
            tasks = tasks.filter_by(reviewer_id=reviewer_id)

        if query.get('order') == 'asc':
            tasks = tasks.order_by(Task.time)
        else:
            tasks = tasks.order_by(desc(Task.time))

        pagination = tasks.paginate(page=query['page'],
                                    per_page=query['per_page'])
        return {
            'tasks': pagination.items,
            'pagination': pagination_builder(pagination)
        }

    @input(TaskInSchema)
    @output(TaskOutSchema, 201)
    @auth_required()
    def post(self, task):
        """Create a task."""
        task_with_same_name = Task.query.filter_by(name=task.name).first()
        if task_with_same_name is not None:
            abort(400, 'DUPLICATED_TASK_NAME')

        task.status = JobStatus.UNLABELED
        task.time = datetime.now()
        task.creator = g.current_user
        task.published = False

        db.session.add(task)
        db.session.commit()

        return task


@task_bp.route('/export/<int:task_id>', endpoint='export')
class ExportView(MethodView):
    @input(ExportInSchema, 'query')
    @auth_required()
    def get(self, task_id, data):
        print(task_id, data)
        task = Task.query.get(task_id)
        if task.status != JobStatus.DONE:
            abort(400, 'TASK_IS_NOT_DONE')
        export_dir = export_task(task, data['export_type'])
        if export_dir is None:
            abort(400, 'EXPORT_DIR_NOT_FOUND')
        try:
            return send_file(export_dir, as_attachment=True)
        except FileNotFoundError:
            abort(400, 'FILE_NOT_FOUND')
