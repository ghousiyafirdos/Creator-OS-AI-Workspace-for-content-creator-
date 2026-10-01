from app import db
from datetime import datetime

class Analytics(db.Model):
    __tablename__ = 'analytics'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    month_year = db.Column(db.String(7), nullable=False)  # e.g., "2026-07"
    ai_generations_count = db.Column(db.Integer, default=0)
    posts_published = db.Column(db.Integer, default=0)
    followers_count = db.Column(db.Integer, default=12400)
    likes_count = db.Column(db.Integer, default=84200)
    views_count = db.Column(db.Integer, default=340500)
    most_used_tool = db.Column(db.String(50), default='Caption Generator')
    previous_productivity_score = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship back to User
    user = db.relationship('User', backref=db.backref('analytics_records', lazy=True, cascade='all, delete-orphan'))

    def calculate_productivity_score(self):
        """
        Calculates dynamic Productivity Score (0 - 100):
        - AI Generations factor: min(40, ai_generations_count * 4)
        - Published Posts factor: min(40, posts_published * 8)
        - Consistency Base: 20
        """
        ai_score = min(50, self.ai_generations_count * 5)
        post_score = min(50, self.posts_published * 10)
        total_score = ai_score + post_score
        return min(100, max(0, total_score))

    def to_dict(self):
        return {
            'id': self.id,
            'month_year': self.month_year,
            'ai_generations': self.ai_generations_count,
            'posts_published': self.posts_published,
            'followers': self.followers_count,
            'likes': self.likes_count,
            'views': self.views_count,
            'most_used_tool': self.most_used_tool,
            'productivity_score': self.calculate_productivity_score()
        }

    def __repr__(self):
        return f'<Analytics User {self.user_id} Month {self.month_year}>'
