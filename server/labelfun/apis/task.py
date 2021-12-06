from datetime import datetime

from apiflask import APIBlueprint, input, output, abort, pagination_builder
from apiflask.schemas import EmptySchema
from flask import g
from flask.views import MethodView
from sqlalchemy import desc

from labelfun.apis.auth import auth_required
from labelfun.extensions import db
from labelfun.models import UserType, TaskType
from labelfun.models.task import Task
from labelfun.schemas.task import TaskOutSchema, TasksOutSchema, TaskInSchema, \
    TasksQuerySchema, TaskClaimInSchema

task_bp = APIBlueprint('task', __name__)


@task_bp.route('/<int:task_id>', endpoint="task")
class TaskView(MethodView):

    @output(TaskOutSchema)
    @auth_required()
    def get(self, task_id):
        task = Task.query.get_or_404(task_id)
        return task

    @input(TaskClaimInSchema)
    @output(TaskOutSchema, 201)
    @auth_required()
    def post(self, task_id, data):
        task = Task.query.get_or_404(task_id)
        user = g.current_user
        if data['type'] == 'label':
            if task.labeler is not None:
                abort(400, 'TASK_UNDERTAKEN')
            task.labeler = user
        else:  # 'review'
            if task.labeler is None:
                abort(400, 'TASK_NOT_LABELED')
            elif task.reviewer is not None:
                abort(400, 'TASK_UNDERTAKEN')
            task.reviewer = user
        db.session.commit()
        return task

    @output(EmptySchema, 204)
    @auth_required()
    def delete(self, task_id):
        task = Task.query.get(task_id)
        if task is None:
            abort(404)
        if g.current_user.id != task.creator_id and g.current_user.type != UserType.ADMIN:
            abort(403, message="UNAUTHORIZED")
        db.session.delete(task)
        db.session.commit()
        return {}


@task_bp.route('', endpoint='tasks')
class TasksView(MethodView):

    @input(TasksQuerySchema, location='query')
    @output(TasksOutSchema)
    @auth_required()
    def get(self, query):
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
        pagination = tasks.paginate(
            page=query['page'],
            per_page=query['per_page']
        )
        return {
            'tasks': pagination.items,
            'pagination': pagination_builder(pagination)
        }

    @input(TaskInSchema)
    @output(TaskOutSchema, 201)
    @auth_required()
    def post(self, task):
        user = g.current_user

        task.time = datetime.now()
        task.creator = user
        db.session.add(task)
        db.session.commit()

        return task
