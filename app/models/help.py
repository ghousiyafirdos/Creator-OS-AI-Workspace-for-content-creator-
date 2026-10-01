from app import db
from datetime import datetime

class Feedback(db.Model):
    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    rating = db.Column(db.Integer, default=5)
    category = db.Column(db.String(50), default='General')
    comments = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship back to User
    user = db.relationship('User', backref=db.backref('feedback_entries', lazy=True, cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<Feedback User {self.user_id} Rating {self.rating}>'
