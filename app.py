from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wifi_capping.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class UsageRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bytes_used = db.Column(db.BigInteger, default=0)
    session_start = db.Column(db.DateTime, default=datetime.utcnow)
    session_end = db.Column(db.DateTime)
    ip_address = db.Column(db.String(45))
    
    user = db.relationship('User', backref=db.backref('usage_records', lazy=True))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('user_dashboard.html')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
    
    # Get usage statistics
    total_users = User.query.count()
    total_sessions = UsageRecord.query.count()
    total_bytes = db.session.query(db.func.sum(UsageRecord.bytes_used)).scalar() or 0
    
    # Recent usage data for charts
    recent_usage = db.session.query(
        db.func.date(UsageRecord.session_start).label('date'),
        db.func.sum(UsageRecord.bytes_used).label('total_bytes')
    ).filter(
        UsageRecord.session_start >= datetime.now() - timedelta(days=30)
    ).group_by(db.func.date(UsageRecord.session_start)).all()
    
    return render_template('admin_dashboard.html', 
                         total_users=total_users,
                         total_sessions=total_sessions, 
                         total_bytes=total_bytes,
                         recent_usage=recent_usage)

@app.route('/admin/usage_reports')
@login_required
def usage_reports():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
    
    # Get detailed usage reports
    users_usage = db.session.query(
        User.username,
        db.func.sum(UsageRecord.bytes_used).label('total_bytes'),
        db.func.count(UsageRecord.id).label('session_count'),
        db.func.max(UsageRecord.session_start).label('last_activity')
    ).join(UsageRecord).group_by(User.id).all()
    
    # Add status calculation
    users_with_status = []
    for user in users_usage:
        user_dict = {
            'username': user.username,
            'total_bytes': user.total_bytes or 0,
            'session_count': user.session_count or 0,
            'last_activity': user.last_activity
        }
        
        if user.last_activity:
            days_ago = (datetime.utcnow() - user.last_activity).days
            if days_ago <= 1:
                user_dict['status'] = 'Active'
                user_dict['status_class'] = 'success'
            elif days_ago <= 7:
                user_dict['status'] = 'Recent'
                user_dict['status_class'] = 'warning'
            else:
                user_dict['status'] = 'Inactive'
                user_dict['status_class'] = 'danger'
        else:
            user_dict['status'] = 'No Activity'
            user_dict['status_class'] = 'danger'
            
        users_with_status.append(user_dict)
    
    return render_template('usage_reports.html', users_usage=users_with_status)

@app.route('/api/usage_data')
@login_required
def usage_data_api():
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    # Return JSON data for charts
    daily_usage = db.session.query(
        db.func.date(UsageRecord.session_start).label('date'),
        db.func.sum(UsageRecord.bytes_used).label('bytes'),
        db.func.count(UsageRecord.id).label('sessions')
    ).filter(
        UsageRecord.session_start >= datetime.now() - timedelta(days=30)
    ).group_by(db.func.date(UsageRecord.session_start)).all()
    
    data = {
        'dates': [str(record.date) for record in daily_usage],
        'bytes': [int(record.bytes or 0) for record in daily_usage],
        'sessions': [int(record.sessions) for record in daily_usage]
    }
    
    return jsonify(data)

def create_admin_user():
    """Create default admin user if none exists"""
    admin = User.query.filter_by(is_admin=True).first()
    if not admin:
        admin = User(username='admin', is_admin=True)
        admin.set_password('admin123')  # Change this in production
        db.session.add(admin)
        db.session.commit()
        print("Default admin user created: admin/admin123")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin_user()
        
        # Add some sample data for demonstration
        if UsageRecord.query.count() == 0:
            # Create sample users and usage data
            user1 = User(username='user1')
            user1.set_password('password')
            user2 = User(username='user2') 
            user2.set_password('password')
            
            db.session.add(user1)
            db.session.add(user2)
            db.session.commit()
            
            # Add sample usage records
            import random
            for i in range(50):
                usage = UsageRecord(
                    user_id=random.choice([user1.id, user2.id]),
                    bytes_used=random.randint(1000000, 1000000000),  # 1MB to 1GB
                    session_start=datetime.now() - timedelta(days=random.randint(0, 30)),
                    ip_address=f"192.168.1.{random.randint(100, 200)}"
                )
                db.session.add(usage)
            db.session.commit()
    
    app.run(debug=True, host='0.0.0.0', port=5001)