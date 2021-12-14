import math
from datetime import datetime
from pprint import pprint

from apiflask import APIBlueprint, input, output, abort
from apiflask.schemas import EmptySchema
from flask import g, current_app
from flask.views import MethodView
from qiniu import Auth, urlsafe_base64_encode, BucketManager

from labelfun.apis.auth import auth_required
from labelfun.extensions import db
from labelfun.models import UserType, JobStatus, TaskType
from labelfun.models.task import Task, Entity
from labelfun.schemas.task import GetTokenInSchema, GetTokenOutSchema, \
    EntityOutSchema, LabelInSchema, ReviewInSchema, EntityPatchSchema

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
        interval = task.interval

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

        ops = 'imageView2/1/w/100/h/100/format/webp/q/75' if task.type != TaskType.VIDEO_SEG else ''
        for path in paths:
            key = urlsafe_base64_encode("&".join([str(task_id),
                                                  path,
                                                  str(datetime.now())]))
            thumb_key = urlsafe_base64_encode(key + '-thumb')

            if task.type != TaskType.VIDEO_SEG:
                ops = 'imageView2/1/w/100/h/100/format/webp/q/75|saveas/' + urlsafe_base64_encode(
                    bucket_name + ':' + thumb_key)
                body = '{"key":$(key),"duration":null}'
            else:
                ops = 'vsample/jpg/interval/' + str(
                    interval) + '/pattern/' + urlsafe_base64_encode(
                    key + '-$(count)') + ';'
                ops += 'vsample/jpg/s/x100/interval/' + str(
                    interval) + '/pattern/' + urlsafe_base64_encode(
                    thumb_key + '-$(count)')
                body = '{"key":$(key),"duration":$(avinfo.format.duration)}'

            policy = {
                "persistentOps": ops,
                "mimeLimit": mime_limit,
                "returnBody": body,
            }
            print(f'Policy for {path}:')
            pprint(policy)
            token = q.upload_token(bucket_name, key, policy=policy)

            entity = Entity(key=key, thumb_key=thumb_key, path=path,
                            type=task.type, status=JobStatus.UNLABELED)
            entity.task = task
            db.session.add(entity)
            db.session.commit()
            credentials.append(
                dict(id=entity.id, path=path, key=key, token=token))

        return dict(credentials=credentials, task=task)

    @input(EntityPatchSchema)
    @output(EntityOutSchema)
    @auth_required()
    def patch(self, data):
        """Confirm that the entity is uploaded."""
        print(f'Received ({data["key"]}, {data["duration"]})')
        key = data['key']
        entity: Entity = Entity.query.filter_by(key=key).first_or_404()
        if g.current_user != entity.task.creator and g.current_user.type != UserType.ADMIN:
            abort(403)
        entity.uploaded = True
        if 'duration' in data and data['duration']:
            entity.frame_count = math.floor(
                data['duration'] / entity.task.interval)
        print(entity.frame_count, "frames in total.")
        db.session.commit()
        return entity


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

        tipe = data['type']
        if (task.type == TaskType.IMAGE_CLS and tipe != 'labels') or (
                task.type == TaskType.IMAGE_SEG and tipe != 'boxes') or (
                task.type == TaskType.VIDEO_SEG and tipe != 'objects'):
            abort(400, 'INCOMPATIBLE_ANNOTATION')

        annotation = data.get('annotation')
        print('annotation:', annotation)
        if not annotation or annotation == '[]':
            entity.annotation = None
            entity.status = JobStatus.UNLABELED
        else:
            schema = LabelInSchema()
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

    @output(EmptySchema, 204)
    def delete(self, entity_id):
        """Delete an entity."""
        entity = Entity.query.get_or_404(entity_id)
        user = g.current_user
        task = entity.task
        if user.type != UserType.ADMIN and user != task.reviewer:
            abort(403)
        if task.published:
            abort(400, 'TASK_IS_PUBLISHED')

        if entity.uploaded:
            access_key = current_app.config['QINIU_ACCESS_KEY']
            secret_key = current_app.config['QINIU_SECRET_KEY']
            q = Auth(access_key, secret_key)
            bucket = BucketManager(q)
            bucket_name = 'taijian'
            bucket.delete(bucket_name, entity.key)
            if task.type != TaskType.VIDEO_SEG:
                bucket.delete(bucket_name, entity.thumb_key)
            else:
                for i in range(1, entity.frame_count + 1):
                    bucket.delete(bucket_name, entity.key + f'-{i:06d}')
                    bucket.delete(bucket_name, entity.thumb_key + f'-{i:06d}')
        db.session.delete(entity)
        db.session.commit()
        return {}
