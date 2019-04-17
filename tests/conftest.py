import sys
sys.path.insert(0, '../strivial/')

import pytest
from strivial import create_app
from strivial.database import db

'''
Create and configure a new app instance for each test
'''
@pytest.fixture
def app():
    # create the app using the test config
    app = create_app(test_config=True)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()