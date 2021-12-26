import json
import math
from datetime import datetime
from pprint import pprint

from apiflask import APIBlueprint, input, output, abort
from flask import g, current_app
from flask.views import MethodView
from qiniu import Auth, urlsafe_base64_encode, BucketManager

from labelfun.apis.auth import auth_required
from labelfun.extensions import db
from labelfun.models import UserType, JobStatus, TaskType
from labelfun.models.task import Task, Entity
from labelfun.schemas.task import GetTokenInSchema, GetTokenOutSchema, \
    EntityOutSchema, LabelInSchema, ReviewInSchema, EntityPatchSchema, \
    TaskOutSchema

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
        bucket_name = current_app.config['QINIU_BUCKET_NAME']
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
            key = str(task_id) + urlsafe_base64_encode("&".join([
                path,
                str(datetime.now())]))
            thumb_key = str(task_id) + urlsafe_base64_encode("&".join([
                path,
                str(datetime.now())]) + '-thumb')

            if task.type != TaskType.VIDEO_SEG:
                ops = 'imageView2/1/w/100/h/100/format/webp/q/75|saveas/' + urlsafe_base64_encode(
                    bucket_name + ':' + thumb_key)
                body = '{' \
                       '"key":$(key),' \
                       '"duration":null,' \
                       '"metadata":{' \
                       '"size_bytes":$(fsize),' \
                       '"mime_type":$(mimeType),' \
                       '"width":$(imageInfo.width),' \
                       '"height":$(imageInfo.height),' \
                       '"num_channels":3' \
                       '}}'
            else:
                ops = 'vsample/jpg/interval/' + str(
                    interval) + '/pattern/' + urlsafe_base64_encode(
                    key + '-$(count)') + ';'
                ops += 'vsample/jpg/s/x100/interval/' + str(
                    interval) + '/pattern/' + urlsafe_base64_encode(
                    thumb_key + '-$(count)')
                body = '{' \
                       '"key":$(key),' \
                       '"duration":$(avinfo.video.duration),' \
                       '"metadata":{' \
                       '"size_bytes":$(fsize),' \
                       '"mime_type":$(mimeType),' \
                       '"frame_width":$(avinfo.video.width),' \
                       '"frame_height":$(avinfo.video.height),' \
                       '"frame_rate":$(avinfo.video.r_frame_rate),' \
                       '"total_frame_count":$(avinfo.video.nb_frames),' \
                       '"duration":$(avinfo.video.duration),' \
                       '"encoding_str":$(avinfo.video.codec_name)' \
                       '}}'

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
        key = data['key']
        entity: Entity = Entity.query.filter_by(key=key).first_or_404()
        if g.current_user != entity.task.creator and g.current_user.type != UserType.ADMIN:
            abort(403)
        entity.uploaded = True
        entity.meta_data = json.dumps(data['metadata'])
        if 'duration' in data and data['duration']:
            entity.frame_count = max(math.floor(
                data['duration'] / entity.task.interval) - 1, 1)
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
            if entity.status == JobStatus.UNREVIEWED:
                task.labeled_count -= 1
            entity.status = JobStatus.UNLABELED
        else:
            entity.annotation = annotation
            if entity.status == JobStatus.UNLABELED:
                task.labeled_count += 1
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
        if entity.status not in [JobStatus.UNREVIEWED, JobStatus.REVIEWED]:
            abort(400, 'ENTITY_IS_NOT_UNREVIEWED')
        if task.status != JobStatus.UNREVIEWED:
            abort(400, 'TASK_STATUS_IS_NOT_UNREVIEWED')

        review = data['review']
        if review == 'correct':
            entity.review = True
        else:  # 'incorrect'
            entity.review = False
        if entity.status == JobStatus.UNREVIEWED:
            task.reviewed_count += 1
        entity.status = JobStatus.REVIEWED
        db.session.commit()
        return entity

    @output(TaskOutSchema)
    @auth_required()
    def delete(self, entity_id):
        """Delete an entity."""
        entity = Entity.query.get_or_404(entity_id)
        user = g.current_user
        task = entity.task
        task_id = task.id
        if user.type != UserType.ADMIN and user != task.creator:
            abort(403)
        if task.published:
            abort(400, 'TASK_IS_PUBLISHED')

        if entity.uploaded:
            access_key = current_app.config['QINIU_ACCESS_KEY']
            secret_key = current_app.config['QINIU_SECRET_KEY']
            q = Auth(access_key, secret_key)
            bucket = BucketManager(q)
            bucket_name = current_app.config['QINIU_BUCKET_NAME']

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
        db.session.commit()
        return Task.query.get(task_id)
