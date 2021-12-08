from apiflask import APIBlueprint
from flask import request

from labelfun.apis.auth import auth_bp
from labelfun.apis.entity import entity_bp
from labelfun.apis.task import task_bp
from labelfun.apis.user import user_bp

api_bp = APIBlueprint('api', __name__)

api_bp.register_blueprint(auth_bp, url_prefix='/auth')
api_bp.register_blueprint(user_bp, url_prefix='/users')
api_bp.register_blueprint(entity_bp, url_prefix='/media')
api_bp.register_blueprint(task_bp, url_prefix='/tasks')


@api_bp.post('')
def hello():
    return request.data
