from marshmallow import Schema, EXCLUDE
from marshmallow.fields import Integer, String, Function, List, Nested
from marshmallow.validate import OneOf

from labelfun.models import JobStatus, TaskType


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


class EntityOutSummarySchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = Integer()
    key = String()
    thumb_key = String()
    type = Function(lambda obj: TaskType(obj.type).name.lower())
    status = Function(lambda obj: JobStatus(obj.status).name.lower())
    task_id = Integer()


class EntityOutSchema(EntityOutSummarySchema):
    annotation = String(dump_default="")
    frames = List(String)


class LabelInSchema(Schema):
    annotation = String(required=True)


class ReviewInSchema(Schema):
    review = String(required=True, validate=[OneOf(['correct', 'incorrect'])])
