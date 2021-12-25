import os
import sys

from flask.cli import load_dotenv

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

load_dotenv()

# SQLite URI compatible
WIN = sys.platform.startswith('win')
if WIN:
    sqlite_prefix = 'sqlite:///'
else:
    sqlite_prefix = 'sqlite:////'


class BaseConfig:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev key')
    QINIU_ACCESS_KEY = os.getenv('QINIU_ACCESS_KEY', 'access key')
    QINIU_SECRET_KEY = os.getenv('QINIU_SECRET_KEY', 'secret key')
    QINIU_BUCKET_NAME = os.getenv('QINIU_BUCKET_NAME')
    QINIU_BUCKET_DOMAIN = os.getenv('QINIU_BUCKET_DOMAIN')


class DevelopmentConfig(BaseConfig):
    DEV_SQLALCHEMY_DATABASE_URI = sqlite_prefix + \
                                  'E:\\Users\\imbiansl\\Desktop\\labelfun\\database.db'
    SQLALCHEMY_DATABASE_URI = os.getenv('LABELFUN_DATABASE_URL')
    INVITATION_CODE = '123456'
    INVITATION_CODE_ADMIN = 'abcdef'
    EXPORT_DIRECTORY = 'E:\\Users\\imbiansl\\Desktop\\export\\'


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv('LABELFUN_DATABASE_URL')
    INVITATION_CODE = os.getenv('INVITATION_CODE')
    INVITATION_CODE_ADMIN = os.getenv('INVITATION_CODE_ADMIN')
    EXPORT_DIRECTORY = os.getenv('EXPORT_DIRECTORY')


class TestingConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = sqlite_prefix + 'E:\\Users\\imbiansl\\Desktop' \
                                              '\\labelfun\\database.db '
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}
