from datetime import datetime

from apiflask import APIBlueprint, input, output, abort
from flask import g, current_app
from flask.views import MethodView
from qiniu import Auth, urlsafe_base64_encode

from labelfun.apis.auth import auth_required
from labelfun.extensions import db
from labelfun.models import UserType, JobStatus, TaskType
from labelfun.models.entity import Entity
from labelfun.models.task import Task
from labelfun.schemas.entity import GetTokenInSchema, GetTokenOutSchema, \
    EntityOutSchema, LabelInSchema, ReviewInSchema

entity_bp = APIBlueprint('entity', __name__)


@entity_bp.route('', endpoint='entities')
class EntitiesView(MethodView):

    @input(GetTokenInSchema)
    @output(GetTokenOutSchema, 201)
    @auth_required()
    def post(self, data):
        """Request an upload token."""
        access_key = current_app.config['QINIU_ACCESS_KEY']
        secret_key = current_app.config['QINIU_SECRET_KEY']

        q = Auth(access_key, secret_key)
        bucket_name = 'taijian'
        credentials = list()
        task_id = data['task_id']
        paths = data['paths']

        task = Task.query.get(task_id)
        if task is None:
            abort(404, 'NO_SUCH_TASK')
        if task.creator_id != g.current_user.id and g.current_user.type != UserType.ADMIN:
            abort(403)
        if task.published:
            # Images/videos cannot be added to published tasks
            abort(400, 'TASK_PUBLISHED')
        if task.labeler_id is not None:
            abort(400, "TASK_UNDERTAKEN")

        # restrict upload types
        mime_limit = 'image/*' if task.type != TaskType.VIDEO_SEG else 'video/*'

        ops = 'imageView2/1/w/100/h/100/format/webp/q/75'
        for path in paths:
            key = urlsafe_base64_encode("&".join([str(task_id),
                                                  path,
                                                  str(datetime.now())]))
            thumb_key = urlsafe_base64_encode(key + '-thumb')
            policy = {
                "persistentOps": ops + "|saveas/" + urlsafe_base64_encode(
                    bucket_name + ':' + thumb_key),
                "mimeLimit": mime_limit
            }
            token = q.upload_token(bucket_name, key, policy=policy)

            entity = Entity(key=key, thumb_key=thumb_key,
                            type=task.type, status=JobStatus.UNLABELED)
            entity.task = task
            db.session.add(entity)
            db.session.commit()
            credentials.append(
                dict(id=entity.id, path=path, key=key, token=token))

        return dict(credentials=credentials)


@entity_bp.route('/<int:entity_id>', endpoint='entity')
class EntityView(MethodView):

    @output(EntityOutSchema)
    @auth_required()
    def get(self, entity_id):
        """Gets an entity."""
        entity = Entity.query.get_or_404(entity_id)
        return entity

    @input(LabelInSchema)
    @output(EntityOutSchema)
    @auth_required()
    def post(self, entity_id, data):
        """Label an entity."""
        entity = Entity.query.get_or_404(entity_id)
        user = g.current_user
        task = entity.task
        if user.type != UserType.ADMIN and user != task.labeler:
            abort(403)
        if entity.status not in [JobStatus.UNLABELED, JobStatus.UNREVIEWED]:
            abort(400, 'ENTITY_IS_NOT_UNLABELED_NOR_UNREVIEWED')
        if task.status != JobStatus.UNLABELED:
            abort(400, 'TASK_STATUS_IS_NOT_UNLABELED')

        annotation = data.get('annotation')
        if not annotation:
            entity.annotation = None
            entity.status = JobStatus.UNLABELED
        else:
            entity.annotation = annotation
            entity.status = JobStatus.UNREVIEWED

        db.session.commit()
        return entity

    @input(ReviewInSchema)
    @output(EntityOutSchema)
    @auth_required()
    def put(self, entity_id, data):
        """Review an entity."""
        entity = Entity.query.get_or_404(entity_id)
        user = g.current_user
        task = entity.task
        if user.type != UserType.ADMIN and user != task.reviewer:
            abort(403)
        if entity.status != JobStatus.UNREVIEWED:
            abort(400, 'ENTITY_IS_NOT_UNREVIEWED')
        if task.status != JobStatus.UNREVIEWED:
            abort(400, 'TASK_STATUS_IS_NOT_UNREVIEWED')

        review = data['review']
        if review == 'correct':
            entity.status = JobStatus.DONE
        else:  # 'incorrect'
            entity.status = JobStatus.UNLABELED
            entity.annotation = None
        db.session.commit()
        return entity
