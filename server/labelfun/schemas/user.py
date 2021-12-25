from apiflask import Schema
from apiflask.fields import String, Email, Integer
from apiflask.validators import Length, Regexp
from marshmallow.fields import Function

from labelfun.models import UserType


#  Authorization  #
class LoginInSchema(Schema):
    grant_type = String(required=True)
    email = Email(required=True)
    password = String(required=True, validate=Length(
        8, 32, error="Password must be between 8 and 32 characters long."))


class LoginOutSchema(Schema):
    id = Integer()
    email = Email()
    name = String()
    type = String()
    access_token = String()
    expires_in = Integer()
    token_type = String()


#  User  #

class UserCreateInSchema(Schema):
    name = String(required=True)
    email = Email(required=True)
    password = String(required=True, validate=[
        Length(8, 32,
               error="Password must be between 8 and 32 characters long."),
        Regexp(r"(.*?)[a-zA-Z]", error="Password must contain an alphabet."),
        Regexp(r"(.*?)[0-9]", error="Password must contain a number."),
        Regexp(r"(.*?)[!\"#$%&'()*+,\-./:;<=>?@[\\\]^_`{|}~]",
               error="Password must contain a special character.")
    ])
    invitation = String(required=True)


class UserEditInSchema(Schema):
    name = String()
    email = Email()
    old_password = String()
    new_password = String(allow_none=True, validate=[
        Length(8, 32,
               error="Password must be between 8 and 32 characters long."),
        Regexp(r"(.*?)[a-zA-Z]", error="Password must contain an alphabet."),
        Regexp(r"(.*?)[0-9]", error="Password must contain a number."),
        Regexp(r"(.*?)[!\"#$%&'()*+,\-./:;<=>?@[\\\]^_`{|}~]",
               error="Password must contain a special character.")
    ])


class UserQueryOutSchema(Schema):
    id = Integer()
    name = String()
    email = String()
    type = Function(lambda obj: UserType(obj.type).name.lower())
