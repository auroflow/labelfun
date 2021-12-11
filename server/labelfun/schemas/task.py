import json

from apiflask import PaginationSchema
from marshmallow import Schema, EXCLUDE, post_load, validates_schema, \
    ValidationError, post_dump
from marshmallow.fields import String, List, Integer, Nested, Function, \
    DateTime, Boolean, Method, Float
from marshmallow.validate import OneOf, Range, Length

import labelfun.schemas.user as lsu
from labelfun.models import TaskType, JobStatus
from labelfun.models.task import Task


class EntityOutSummarySchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = Integer()
    key = String()
    path = String()
    thumb_key = String()
    type = Function(lambda obj: TaskType(obj.type).name.lower())
    status = Function(lambda obj: JobStatus(obj.status).name.lower())
    task_id = Integer()


class ImageSegmentationSchema(Schema):
    label = String(required=True)
    bbox = List(Float, required=True, validate=[Length(min=4, max=4)])


class VideoSegmentationSchema(Schema):
    pass


class EntityOutSchema(EntityOutSummarySchema):
    annotation = String()
    frames = List(String)

    @post_dump
    def load_annotation(self, data, many, *kwargs):
        print('data:', data)
        print('type:', type(data))
        if 'annotation' in data and data['annotation']:
            data['annotation'] = json.loads(data['annotation'])
        else:
            data['annotation'] = []
        return data


# Task creation #
class TaskInSchema(Schema):
    name = String(required=True)
    type = String(required=True, validate=[
        OneOf(choices=['image_cls', 'image_seg', 'video_seg'],
              error="Type must be one of image_cls, image_seg and video_seg.")
    ])
    labels = List(String, required=True)

    @post_load
    def to_model(self, data, **kwargs):
        data['type'] = eval('TaskType.' + data['type'].upper())
        return Task(**data)


class TaskModifyInSchema(Schema):
    name = String()
    type = String(allow_none=True, validate=[
        OneOf(choices=['image_cls', 'image_seg', 'video_seg'],
              error="Type must be one of image_cls, image_seg and video_seg.")
    ])
    labels = List(String)
    published = Boolean()


class TaskOutSummarySchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = Integer()
    time = DateTime()
    name = String()
    type = Function(lambda obj: TaskType(obj.type).name.lower())
    creator = Nested(lsu.UserQueryOutSchema)
    labeler = Nested(lsu.UserQueryOutSchema)
    reviewer = Nested(lsu.UserQueryOutSchema)
    entity_count = Function(lambda obj: len(obj.entities))
    labeled_count = Integer()
    reviewed_count = Integer()
    labels = Function(lambda obj: obj.labels.split(','))
    status = Function(lambda obj: JobStatus(obj.status).name.lower())
    published = Boolean()
    label_done = Function(lambda obj: len(obj.entities) == obj.labeled_count)
    review_done = Function(lambda obj: len(obj.entities) == obj.reviewed_count)
    progress = Method('get_progress')

    def get_progress(self, obj: Task):
        if not obj.published:
            return 'unpublished'
        if obj.status == JobStatus.UNLABELED:
            if obj.labeler is None:
                return 'unlabeled'
            else:
                return 'labeling'
        if obj.status == JobStatus.UNREVIEWED:
            if obj.reviewer is None:
                return 'unreviewed'
            else:
                return 'reviewing'
        return 'done'


class TasksQuerySchema(Schema):
    type = String(allow_none=True,
                  validate=[OneOf(['unlabeled', 'unreviewed', 'done'])])
    creator = Integer(allow_none=True)
    labeler = Integer(allow_none=True)
    reviewer = Integer(allow_none=True)
    page = Integer(load_default=1)
    per_page = Integer(load_default=100, validate=[Range(max=100)])
    order = String(load_default='desc',
                   validate=[OneOf(['desc', 'asc'])])


class TasksOutSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    tasks = List(Nested(TaskOutSummarySchema))
    pagination = Nested(PaginationSchema)


class TaskOutSchema(TaskOutSummarySchema):
    class Meta:
        unknown = EXCLUDE

    entities = List(Nested(EntityOutSchema))


class TaskProcessInSchema(Schema):
    type = String(required=True, validate=[OneOf(['label', 'review'])])


class GetTokenInSchema(Schema):
    task_id = Integer(required=True)
    paths = List(String, required=True)


class TokenOutSchema(Schema):
    id = Integer()
    path = String()
    token = String()
    key = String()


class GetTokenOutSchema(Schema):
    credentials = List(Nested(TokenOutSchema))
    task = Nested(TaskOutSchema)


class LabelInSchema(Schema):
    labels = List(String)
    boxes = List(Nested(ImageSegmentationSchema))
    objects = List(Nested(VideoSegmentationSchema))

    @validates_schema
    def validate_fields(self, data, **kwargs):
        count = 0
        if 'labels' in data:
            count += 1
            data['type'] = 'labels'
        if 'boxes' in data:
            count += 1
            data['type'] = 'boxes'
        if 'objects' in data:
            count += 1
            data['type'] = 'objects'
        if count != 1:
            raise ValidationError(
                "Exactly one of labels, annotation and objects is required.")

    @post_load
    def parse_annotation(self, item, many, **kwargs):
        item['annotation'] = json.dumps(item[item['type']])

        del item[item['type']]
        return item


class ReviewInSchema(Schema):
    review = String(required=True, validate=[OneOf(['correct', 'incorrect'])])
