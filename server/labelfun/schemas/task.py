from apiflask import PaginationSchema
from marshmallow import Schema, EXCLUDE, post_load
from marshmallow.fields import String, List, Integer, Nested, Function, \
    DateTime, Boolean
from marshmallow.validate import OneOf, Range

from labelfun.models import TaskType, JobStatus
from labelfun.models.task import Task
from labelfun.schemas.entity import EntityOutSummarySchema
from labelfun.schemas.user import UserQueryOutSchema


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
    creator = Nested(UserQueryOutSchema)
    entity_count = Function(lambda obj: len(obj.entities))
    labeled_count = Integer()
    reviewed_count = Integer()
    labels = Function(lambda obj: obj.labels.split(','))
    status = Function(lambda obj: JobStatus(obj.status).name.lower())
    published = Boolean()
    label_done = Function(lambda obj: len(obj.entities) == obj.labeled_count)
    review_done = Function(lambda obj: len(obj.entities) == obj.reviewed_count)


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

    labeler = Nested(UserQueryOutSchema, allow_none=True)
    reviewer = Nested(UserQueryOutSchema, allow_none=True)
    entities = List(Nested(EntityOutSummarySchema))


class TaskProcessInSchema(Schema):
    type = String(required=True, validate=[OneOf(['label', 'review'])])
