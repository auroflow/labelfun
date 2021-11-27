from flask import request
from apiflask import APIBlueprint
from labelfun.apis.auth import auth_bp
from labelfun.apis.media import media_bp
from labelfun.apis.task import task_bp
from labelfun.apis.user import user_bp

api_bp = APIBlueprint('api', __name__)


api_bp.register_blueprint(auth_bp, url_prefix='/auth')
api_bp.register_blueprint(user_bp, url_prefix='/users')
api_bp.register_blueprint(media_bp, url_prefix='/media')
api_bp.register_blueprint(task_bp, url_prefix='/tasks')


@api_bp.post('')
def hello():
    print(request.data)
    return request.data
