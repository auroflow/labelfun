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
    QINIU_BUCKET_NAME = 'taijian'
    QINIU_BUCKET_DOMAIN = 'http://r3ncixdy0.hd-bkt.clouddn.com/'
    EXPORT_DIRECTORY = 'E:\\Users\\imbiansl\\Desktop\\export\\'


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = sqlite_prefix + \
                              'E:\\Users\\imbiansl\\Desktop\\labelfun\\database.db'


class ProductionConfig(BaseConfig):
    pass


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
