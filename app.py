# backend/app.py

from flask import Flask
from flask_cors import CORS
from config import Config
from models.student_db import db, Student
from routes.students_routes import student_bp


app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
db.init_app(app)

app.register_blueprint(student_bp)


if __name__ == "__main__":
    app.run(debug=True)
