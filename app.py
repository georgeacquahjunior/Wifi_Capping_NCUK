# backend/app.py

from flask import Flask
from flask_cors import CORS
from config import Config
from models.student_db import db, Student
from models.admin_db import db, Admin
from routes.students_routes import student_bp
from routes.admin_routes import admin_bp
import os

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
db.init_app(app)

app.register_blueprint(student_bp)
app.register_blueprint(admin_bp)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render provides PORT env var
    app.run(host="0.0.0.0", port=port)
