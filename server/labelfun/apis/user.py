from apiflask import APIBlueprint, input, output, abort
from apiflask.schemas import EmptySchema
from flask import g
from flask.views import MethodView

from labelfun.extensions import db
from labelfun.models import User
from labelfun.apis.auth import auth_required
from labelfun.schemas import UserCreateInSchema, UserEditInSchema, UserQueryOutSchema
user_bp = APIBlueprint('user', __name__)


@user_bp.route('', endpoint='users')
class UsersView(MethodView):

    @input(UserCreateInSchema)
    @output(UserQueryOutSchema, 201)
    def post(self, data):
        name = data['name']
        email = data['email']
        password = data['password']

        user_with_same_email = User.query.filter_by(email=email).first()
        if user_with_same_email is not None:
            abort(400, 'DUPLICATED_EMAIL')

        new_user = User(name=name, email=email,
                        password=password, type='user')
        db.session.add(new_user)
        db.session.commit()
        return {
            'id': User.query.filter_by(email=email).first().id,
            'name': name,
            'email': email,
            'type': 'user'
        }


@user_bp.route('/<int:user_id>', endpoint='user')
class UserView(MethodView):

    @output(UserQueryOutSchema)
    @auth_required()
    def get(self, user_id):
        if g.current_user.id != user_id and g.current_user.type != 'admin':
            abort(403)
        if g.current_user.id == user_id:
            return g.current_user

        user = User.query.get(user_id)
        if user is None:
            abort(404)
        return user

    @input(UserEditInSchema)
    @output(UserQueryOutSchema)
    @auth_required()
    def patch(self, user_id, data):
        # non-admin users cannot change info of other users
        if g.current_user.id != user_id and g.current_user.type != 'admin':
            abort(403, 'UNAUTHORIZED')

        user = User.query.get(user_id)
        if user is None:
            abort(404)

        name = data.get('name')
        email = data.get('email')
        old_password = data.get('old_password')
        new_password = data.get('new_password')

        if email is not None and email != '':
            user_with_same_email = User.query.filter_by(email=email).first()
            if user_with_same_email is not None and user_with_same_email.id != user_id:
                abort(400, 'DUPLICATED_EMAIL')

        # non-admin users cannot change info without old_password
        if g.current_user.type != 'admin':
            if old_password is None or old_password == '':
                abort(403, 'OLD_PASSWORD_REQUIRED')
            if not user.check_password(old_password):
                abort(403, 'INCORRECT_PASSWORD')

        if name is not None and name != '':
            user.name = name
        if email is not None and email != '':
            user.email = email
        if new_password is not None and new_password != '':
            user.set_password(new_password)
        user_type = user.type
        db.session.commit()
        return {
            'id': user_id,
            'name': name,
            'email': email,
            'type': user_type
        }
