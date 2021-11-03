from flask import current_app
from flask_login import LoginManager, UserMixin
'''
Functionality for API authentication.

You must initialize `login_manager` on app start!
`login_manager.init_app()`
'''
login_manager = LoginManager()


@login_manager.request_loader
def load_user(request):
    """
    Verify that the 'Authorization' header equals our secret key.
    Returns an empty `UserMixin` on success.

    Docs: https://flask-login.readthedocs.io/en/latest/#installation
    Example: http://gouthamanbalaraman.com/blog/minimal-flask-login-example.html
    """
    token = request.headers.get('Authorization')
    return UserMixin() if token == current_app.config['SECRET_KEY'] else None
