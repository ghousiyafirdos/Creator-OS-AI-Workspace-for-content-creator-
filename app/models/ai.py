from app import db
from datetime import datetime

class AIHistory(db.Model):
    __tablename__ = 'ai_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    tool_type = db.Column(db.String(50), nullable=False)  # caption, script, hashtag, bio, rewrite, seo
    prompt = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    tokens_used = db.Column(db.Integer, default=0)
    is_favorite = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship back to User
    user = db.relationship('User', backref=db.backref('ai_records', lazy=True, cascade='all, delete-orphan'))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'tool_type': self.tool_type,
            'prompt': self.prompt,
            'response': self.response,
            'tokens_used': self.tokens_used,
            'is_favorite': self.is_favorite,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    def __repr__(self):
        return f'<AIHistory {self.tool_type} - User {self.user_id}>'


class ChatHistory(db.Model):
    __tablename__ = 'chat_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('chat_records', lazy=True, cascade='all, delete-orphan'))
