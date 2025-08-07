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

    # register auth routes
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api')

    return app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create a test user if it doesn't exist
        from models.student import Student
        import bcrypt
        
        test_user = Student.query.get('admin')
        if not test_user:
            hashed_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
            test_student = Student(
                id='admin',
                name='Admin User',
                password=hashed_password.decode('utf-8')
            )
            db.session.add(test_student)
            db.session.commit()
            print("Test admin user created: admin/admin123")
    
    app.run(debug=True, port=5000)