from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

# Initialize SQLAlchemy(Database Sample) and Bcrypt(Password Hashing)
db = SQLAlchemy()
bcrypt = Bcrypt()

# Student model for database
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True) # Unique internal ID
    student_id = db.Column(db.String(64), unique=True, nullable=False)  # Login ID
    password_hash = db.Column(db.String(128), nullable=False)  # Hashed password
    blocked = db.Column(db.Boolean, default=False)  # Blocked flag for data cap

    # Set password using Bcrypt hashing
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    # Verify password using Bcrypt
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)