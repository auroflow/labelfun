from functools import wraps
from apiflask import APIBlueprint, Schema, input, output, abort
from apiflask.fields import String, Email, Integer
from apiflask.validators import Length
from flask import current_app, g, request
from flask.views import MethodView
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired
from passlib.hash import argon2
from labelfun.models.user import User
from labelfun.extensions import db

auth_bp = APIBlueprint('auth', __name__)


class LoginInSchema(Schema):
    grant_type = String(required=True)
    email = Email(required=True)
    password = String(validate=Length(8, 32), required=True)


class LoginOutSchema(Schema):
    id = Integer()
    email = Email()
    name = String()
    type = String()
    access_token = String()
    expires_in = Integer()
    token_type = String()


def generate_token(user):
    expiration = 3600
    s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
    token = s.dumps({'id': user.id}).decode('ascii')
    return token, expiration


@auth_bp.route('/login', endpoint='login')
class Login(MethodView):

    @input(LoginInSchema)
    @output(LoginOutSchema, 201)
    def post(self, data):
        grant_type = data['grant_type']
        email = data['email']
        password = data['password']

        if grant_type is None or grant_type.lower() != 'password':
            abort(400, 'The grant type must be password.')

        user = User.query.filter_by(email=email).first()
        if user is None or not user.check_password(password):
            abort(400, 'incorrect_email_or_password')

        token, expiration = generate_token(user)

        return {
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'type': user.type,
            'access_token': token,
            'expires_in': expiration,
            'token_type': 'Bearer'
        }, {
            'Cache-Control': 'no-store',
            'Pragma': 'no-cache'
        }


def get_token():
    if 'Authorization' in request.headers:
        try:
            token_type, token = request.headers['Authorization'].split(None, 1)
        except ValueError:
            token_type = token = None
    else:
        token_type = token = None

    return token_type, token


def validate_token(token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except (BadSignature, SignatureExpired):
        return False
    user = User.query.get(data['id'])
    if user is None:
        return False
    g.current_user = user
    return True


def auth_required(admin=False):
    def wrapped(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token_type, token = get_token()

            if request.method != 'OPTIONS':
                if token_type is None or token_type.lower() != 'bearer':
                    abort(400, 'The token type must be bearer.')
                if token is None:
                    abort(401, headers={
                        'WWW-Authenticate': 'Bearer'
                    })
                if not validate_token(token):
                    abort(401, '令牌无效或已过期。', headers={
                        'WWW-Authenticate': 'Bearer'
                    })
                if admin and g.current_user.type != 'admin':
                    abort(403, 'Forbidden.')

            return f(*args, **kwargs)
        return decorated
    return wrapped
