import os


def test_testing_config(app):
    assert not app.config['DEBUG']
    assert app.config['TESTING']
    assert app.config['SQLALCHEMY_DATABASE_URI'] == "postgresql://localhost/strivial_test"


def test_development_config(app):
    app.config.from_object('config.DevelopmentConfig')

    assert app.config['DEVELOPMENT']
    assert app.config['DEBUG']
    assert not app.config['TESTING']
    assert app.config['SQLALCHEMY_DATABASE_URI'] == os.environ['DATABASE_URL']


def test_production_config(app):
    app.config.from_object('config.ProductionConfig')

    assert not app.config['DEBUG']
    assert not app.config['TESTING']
    assert app.config['SQLALCHEMY_DATABASE_URI'] == os.environ['DATABASE_URL']