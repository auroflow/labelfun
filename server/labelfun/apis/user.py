from apiflask import APIBlueprint, Schema, input, output, abort
from apiflask.schemas import EmptySchema
from apiflask.fields import String, Email, Integer
from apiflask.validators import Length, Regexp
from flask import g
from flask.views import MethodView
from passlib.hash import argon2

from labelfun.extensions import db
from labelfun.models.user import User
from labelfun.apis.auth import auth_required

user_bp = APIBlueprint('user', __name__)


class RegisterInSchema(Schema):
    name = String(required=True)
    email = Email(required=True)
    password = String(validate=[
        Length(8, 32, error="Password must be between 8 and 32 characters long."),
        Regexp(r"(.*?)[a-zA-Z]", error="Password must contain an alphabet."),
        Regexp(r"(.*?)[0-9]", error="Password must contain a number."),
        Regexp(r"(.*?)[!\"#$%&'()*+,\-./:;<=>?@[\\\]^_`{|}~]",
               error="Password must contain a special character.")
    ], required=True)


class UserOutSchema(Schema):
    id = Integer()
    name = String()
    email = String()
    type = String()


@ user_bp.route('', endpoint='users')
class UsersView(MethodView):

    @ input(RegisterInSchema)
    @ output(EmptySchema, 201)
    def post(self, data):
        name = data['name']
        email = data['email']
        password = data['password']

        user_with_same_email = User.query.filter_by(email=email).first()
        if user_with_same_email is not None:
            abort(400, 'duplicated_email')

        new_user = User(name=name, email=email,
                        pwdhash=argon2.hash(password), type='user')
        db.session.add(new_user)
        db.session.commit()

        return {}, 201


@ user_bp.route('/<int:user_id>', endpoint='user')
class UserView(MethodView):

    @ output(UserOutSchema)
    @ auth_required()
    def get(self, user_id):
        if g.current_user.id != user_id and g.current_user.type != 'admin':
            abort(403)
        if g.current_user.id == user_id:
            return g.current_user

        user = User.query.get(user_id)
        if user is None:
            abort(404, "用户不存在。")
        return user
