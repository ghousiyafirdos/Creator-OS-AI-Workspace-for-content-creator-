from app import db
from datetime import datetime

class PlannerItem(db.Model):
    __tablename__ = 'planner'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    caption = db.Column(db.Text)
    platform = db.Column(db.String(50), default='Instagram')
    scheduled_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='scheduled')  # 'draft', 'scheduled', 'published', 'missed'
    calendar_uid = db.Column(db.String(100), nullable=True, index=True)
    reminder_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship back to User
    user = db.relationship('User', backref=db.backref('planner_items', lazy=True, cascade='all, delete-orphan'))

    def update_status_if_missed(self):
        """Auto-evaluates status: if scheduled_time passed and still marked scheduled, flag as missed."""
        if self.status == 'scheduled' and datetime.utcnow() > self.scheduled_time:
            self.status = 'missed'
            db.session.commit()

    def to_dict(self):
        self.update_status_if_missed()
        return {
            'id': self.id,
            'title': self.title,
            'caption': self.caption,
            'platform': self.platform,
            'scheduled_time': self.scheduled_time.strftime('%Y-%m-%d %H:%M'),
            'date_str': self.scheduled_time.strftime('%Y-%m-%d'),
            'time_str': self.scheduled_time.strftime('%H:%M'),
            'status': self.status,
            'reminder_sent': self.reminder_sent,
            'created_at': self.created_at.strftime('%Y-%m-%d')
        }

    def __repr__(self):
        return f'<PlannerItem {self.title} - {self.status}>'
