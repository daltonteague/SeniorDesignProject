import os
basedir = os.path.abspath(os.path.dirname(__file__))

production_uri = 'postgresql://postgres:dbpw@localhost:5434/prod_db'
development_uri = 'postgresql://postgres:dbpw@localhost:5432/loadtest_db'
test_uri = 'postgresql://postgres:dbpw@localhost:5433/testing_db'


class Config(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = production_uri


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = development_uri


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = test_uri
