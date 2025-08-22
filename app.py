# backend/app.py

from flask import Flask
from flask_cors import CORS
from config import Config
from models.student_db import db
from models.merged_usage_log_db import db
from routes.students_routes import student_bp
from routes.admin_routes import admin_bp
from routes.usage_logs_routes import dashboard_bp
import os

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
db.init_app(app)

app.register_blueprint(student_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(dashboard_bp)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render provides PORT env var
    app.run(host="0.0.0.0", port=port)
