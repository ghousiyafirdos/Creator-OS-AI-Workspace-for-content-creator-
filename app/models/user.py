from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    profile_pic = db.Column(db.String(255), default='default_avatar.png')
    role = db.Column(db.String(20), default='creator')
    language = db.Column(db.String(20), default='English')
    theme = db.Column(db.String(20), default='light')
    date_of_birth = db.Column(db.Date, nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    gender = db.Column(db.String(30), nullable=True)
    location = db.Column(db.String(120), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    instagram = db.Column(db.String(120), nullable=True)
    youtube = db.Column(db.String(120), nullable=True)
    linkedin = db.Column(db.String(120), nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
