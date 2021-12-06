from marshmallow import Schema, EXCLUDE
from marshmallow.fields import Integer, String, Function, List, Nested

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


class EntityOutSchema(EntityOutSummarySchema):
    annotation = String()
