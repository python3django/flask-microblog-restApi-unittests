import os
from flask import Flask
from .database import db
from flask_login import LoginManager


login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Please log in to access this page.'


def create_app():
    app = Flask(__name__)
    app.config.from_object(os.environ['APP_SETTINGS'])

    db.init_app(app)
    with app.test_request_context():
        db.create_all()

    login.init_app(app)

    """
    if app.debug:
        try:
            from flask_debugtoolbar import DebugToolbarExtension
            toolbar = DebugToolbarExtension(app)
        except:
            pass
    """

    import app.main.views as main
    app.register_blueprint(main.bp)

    import app.api.views as api
    app.register_blueprint(api.bp)

    import app.auth.routes as auth
    app.register_blueprint(auth.bp)

    return app
