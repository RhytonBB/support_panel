from . import db
from flask_login import UserMixin
from datetime import datetime
import uuid

class SupportOperator(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

class SupportRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(16), nullable=False, default='new')
    session_token = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    operator_id = db.Column(db.Integer, db.ForeignKey('support_operator.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    accepted_at = db.Column(db.DateTime, nullable=True)
    closed_at = db.Column(db.DateTime, nullable=True)

class SupportMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('support_request.id'), nullable=False)
    sender_role = db.Column(db.String(16), nullable=False)
    text = db.Column(db.Text, nullable=True)
    media = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
