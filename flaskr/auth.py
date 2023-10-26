# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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
