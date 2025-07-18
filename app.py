# backend/app.py

from flask import Flask
from flask_cors import CORS
from config import Config
from models.student import db, Student
from routes.auth import auth_bp

app = Flask(__name__)
app.config.from_object(Config)

CORS(app)
db.init_app(app)

app.register_blueprint(auth_bp)


if __name__ == "__main__":
    app.run(debug=True)
