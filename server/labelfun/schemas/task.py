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


# Retrieving images/videos
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
    uploaded = Boolean()
    frame_count = Integer()
    review = Boolean()


class EntityOutSchema(EntityOutSummarySchema):
    annotation = String()
    frames = List(String)

    @post_dump
    def load_annotation(self, data, many, *kwargs):
        if 'annotation' in data and data['annotation']:
            data['annotation'] = json.loads(data['annotation'])
        else:
            data['annotation'] = []
        return data


# Task creation and modification
class TaskInSchema(Schema):
    name = String(required=True)
    type = String(required=True, validate=[
        OneOf(choices=['image_cls', 'image_seg', 'video_seg'],
              error="Type must be one of image_cls, image_seg and video_seg.")
    ])
    labels = List(String, required=True)
    interval = Float(allow_none=True)

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


# Requesting for a task
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
    interval = Float()

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


class TaskOutSchema(TaskOutSummarySchema):
    class Meta:
        unknown = EXCLUDE

    entities = List(Nested(EntityOutSummarySchema))


# Tasks query
class TasksQuerySchema(Schema):
    type = String(allow_none=True,
                  validate=[OneOf(['unlabeled', 'unreviewed', 'done'])])
    creator = Integer(allow_none=True)
    labeler = Integer(allow_none=True)
    reviewer = Integer(allow_none=True)
    page = Integer(load_default=1)
    per_page = Integer(load_default=1000, validate=[Range(max=1000)])
    order = String(load_default='desc',
                   validate=[OneOf(['desc', 'asc'])])


class TasksOutSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    tasks = List(Nested(TaskOutSummarySchema))
    pagination = Nested(PaginationSchema)


# Request token for uploading images/videos
class GetTokenInSchema(Schema):
    task_id = Integer(required=True)
    paths = List(String, required=True)
    interval = Integer(allow_none=True)


class TokenOutSchema(Schema):
    id = Integer()
    path = String()
    token = String()
    key = String()


class GetTokenOutSchema(Schema):
    credentials = List(Nested(TokenOutSchema))
    task = Nested(TaskOutSchema)


# Confirm the completion of uploading files
class MetadataSchema(Schema):
    size_bytes = Integer(required=True)
    mime_type = String(required=True)
    # For images
    width = Integer()
    height = Integer()
    num_channels = Integer()
    # For videos
    frame_width = Integer()
    frame_height = Integer()
    frame_rate = String()
    total_frame_count = Integer()
    duration = Float()
    encoding_str = String()

    @validates_schema
    def validate(self, data, **kwargs):
        if data['mime_type'].startswith('image'):
            if 'width' not in data:
                raise ValidationError("width required for an image.")
            if 'height' not in data:
                raise ValidationError("height required for an image.")
            if 'num_channels' not in data:
                raise ValidationError("num_channels required for an image.")
        elif data['mime_type'].startswith('video'):
            if 'frame_width' not in data:
                raise ValidationError("frame_width required for a video.")
            if 'frame_height' not in data:
                raise ValidationError("frame_height required for a video.")
            if 'frame_rate' not in data:
                raise ValidationError("frame_rate required for a video.")
            if 'total_frame_count' not in data:
                raise ValidationError("total_frame_count required for a video.")
            if 'duration' not in data:
                raise ValidationError("duration required for a video.")
            if 'encoding_str' not in data:
                raise ValidationError("encoding_str required for a video.")
        else:
            raise ValidationError(
                'The value of the mime_type field is not accepted.')

    @post_load
    def parse(self, data, many, **kwargs):
        if 'duration' in data:
            data['duration'] = float(data['duration'])
        if 'frame_rate' in data:
            data['frame_rate'] = eval(data['frame_rate'])
        return data


class EntityPatchSchema(Schema):
    key = String(required=True)
    duration = Float(allow_none=True)
    metadata = Nested(MetadataSchema)


# Claim or complete a task
class TaskProcessInSchema(Schema):
    type = String(required=True, validate=[OneOf(['label', 'review'])])


# Label
class ImageSegmentationSchema(Schema):
    label = String(required=True)
    bbox = List(Float, required=True, validate=[Length(min=4, max=4)])


class TrajectorySchema(Schema):
    frame_number = Integer(required=True)
    bbox = List(Float, required=True, validate=[Length(min=4, max=4)])


class VideoSegmentationSchema(Schema):
    label = String(required=True)
    trajectory = List(Nested(TrajectorySchema), required=True)


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


# Review
class ReviewInSchema(Schema):
    review = String(required=True, validate=[OneOf(['correct', 'incorrect'])])


# Export
class ExportInSchema(Schema):
    export_type = String(required=True)
