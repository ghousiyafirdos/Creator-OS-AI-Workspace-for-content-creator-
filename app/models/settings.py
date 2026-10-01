from app import db

class Settings(db.Model):
    __tablename__ = 'settings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    dark_mode = db.Column(db.Boolean, default=False)
    auto_save = db.Column(db.Boolean, default=True)
    notifications_enabled = db.Column(db.Boolean, default=True)
    default_language = db.Column(db.String(20), default='English')
    storage_used_bytes = db.Column(db.BigInteger, default=0)
    storage_limit_bytes = db.Column(db.BigInteger, default=104857600)  # 100 MB Limit

    # Relationship back to User
    user = db.relationship('User', backref=db.backref('user_settings', uselist=False, cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<Settings User {self.user_id} Lang {self.default_language}>'
