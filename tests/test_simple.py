import os
import tempfile
import pytest
import pathlib
from flaskr import create_app
from flaskr import db


@pytest.fixture
def client():
    # Create temporary files for SQLite database and logging
    db_fd, db_path = tempfile.mkstemp()
    log_fd, log_path = tempfile.mkstemp()

    # TODO: SET UP A .FLASKENV FOR TESTING
    app = create_app({
        'SECRET_KEY': 'Test',
        'DATABASE_PATH': pathlib.Path(db_path),
        'LOG_PATH': pathlib.Path(log_path),
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + db_path,
    })

    with app.test_client() as client:
        with app.app_context():
            db.drop_all()
            db.create_all()
        yield client

    os.close(db_fd)
    os.unlink(db_path)


def test_traffic(client):
    """Start with a blank database."""
    res = client.post('/api/v1/traffic', json={
        'url': '/',
        'ip_address': '1234',
        'user_agent': 'Pytest',
    }, headers={'Authorization': 'Test'})
    assert res.status == '200 OK'


def test_users(client):
    res = client.get('/api/v1/data/users', query_string={
        'start_date': '2020-04-01',
        'end_date': '2020-05-01',
        'classification': 'BOT',
    }, headers={'Authorization': 'Test'})
    assert res.status == '200 OK'
    assert res.data == b'[]\n'
