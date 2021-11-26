import os
import sys

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# SQLite URI compatible
WIN = sys.platform.startswith('win')
if WIN:
    sqlite_prefix = 'sqlite:///'
else:
    sqlite_prefix = 'sqlite:////'


class BaseConfig:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev key')


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = sqlite_prefix + \
        'E:\\Users\\imbiansl\\Desktop\\database.db'


class ProductionConfig(BaseConfig):
    pass


class TestingConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = sqlite_prefix + ':memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}
