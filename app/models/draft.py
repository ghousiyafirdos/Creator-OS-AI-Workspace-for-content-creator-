from app import db
from datetime import datetime, timedelta

class Draft(db.Model):
    __tablename__ = 'drafts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    file_path = db.Column(db.String(255))
    file_type = db.Column(db.String(50), default='text')  # 'image', 'video', 'document', 'text'
    file_size_mb = db.Column(db.Float, default=0.0)
    is_favorite = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship back to User
    user = db.relationship('User', backref=db.backref('draft_items', lazy=True, cascade='all, delete-orphan'))

    @classmethod
    def get_user_storage_mb(cls, user_id):
        """Calculates total active storage used in MB for user."""
        items = cls.query.filter_by(user_id=user_id, is_deleted=False).all()
        total = sum(item.file_size_mb for item in items if item.file_size_mb)
        return round(total, 2)

    def days_remaining_in_bin(self):
        """Calculates days left before automatic 30-day purge."""
        if not self.is_deleted or not self.deleted_at:
            return 30
        expiry = self.deleted_at + timedelta(days=30)
        remaining = (expiry - datetime.utcnow()).days
        return max(0, remaining)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'file_size_mb': self.file_size_mb,
            'is_favorite': self.is_favorite,
            'is_deleted': self.is_deleted,
            'days_remaining': self.days_remaining_in_bin(),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M')
        }

    def __repr__(self):
        return f'<Draft {self.title} - {self.file_type}>'
