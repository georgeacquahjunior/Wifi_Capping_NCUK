from .student_db import db

class MergedUsageLogs(db.Model):
    __tablename__ = 'merged_usage_logs'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), db.ForeignKey('students.student_id', ondelete='CASCADE'), nullable=False)
    date_allocated = db.Column(db.Date, nullable=False)
    data_allocated = db.Column(db.Numeric(10, 2), nullable=False)  # GB allocated
    acctinputoctets = db.Column(db.BigInteger)  # Bytes in (from radacct)
    acctoutputoctets = db.Column(db.BigInteger)  # Bytes out (from radacct)
    capped_status = db.Column(db.Boolean, default=False)

    # These columns are computed in the database, not in SQLAlchemy, so we read them only.
    data_used = db.Column(db.Numeric(10, 3))        # GB used (computed in PostgreSQL)
    data_left = db.Column(db.Numeric(10, 2))        # GB left (computed in PostgreSQL)
    percentage_used = db.Column(db.Numeric(5, 2))   # % used (computed in PostgreSQL)
