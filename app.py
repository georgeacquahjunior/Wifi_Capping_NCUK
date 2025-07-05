# this is a Flask application that uses SQLAlchemy for database management and Flask-CORS for handling CORS requests.
# It initializes the app, configures the database, and registers a blueprint for authentication routes.

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    db.init_app(app)

    # register auth
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    # register log_usage
    from routes.usage import usage_bp
    app.register_blueprint(usage_bp, url_prefix='/usage') # /log_usage becomes /usage/log_usage

    # register auth
    from routes.check_limit import check_limit_bp
    app.register_blueprint(check_limit_bp)

    from routes.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')  # /admin/usage becomes /admin/usage


    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
