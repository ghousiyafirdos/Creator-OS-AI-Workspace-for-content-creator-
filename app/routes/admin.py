from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.ai import AIHistory
from app.models.draft import Draft
from app.models.help import Feedback

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """Admin Dashboard showing platform-wide statistics, users management, and feedback logs."""
    total_users = User.query.count()
    total_ai_generations = AIHistory.query.count()
    total_drafts = Draft.query.filter_by(is_deleted=False).count()
    total_storage_mb = round(sum(d.file_size_mb for d in Draft.query.filter_by(is_deleted=False).all() if d.file_size_mb), 2)
    
    users = User.query.order_by(User.created_at.desc()).all()
    feedback_reports = Feedback.query.order_by(Feedback.created_at.desc()).all()

    return render_template('admin/dashboard.html',
                           total_users=total_users,
                           total_ai_generations=total_ai_generations,
                           total_drafts=total_drafts,
                           total_storage_mb=total_storage_mb,
                           users=users,
                           feedback_reports=feedback_reports)

@admin_bp.route('/toggle-role/<int:user_id>', methods=['POST'])
@login_required
def toggle_role(user_id):
    """Elevates or demotes a user's role (creator <-> admin)."""
    user = User.query.get_or_404(user_id)
    user.role = 'admin' if user.role == 'creator' else 'creator'
    db.session.commit()
    flash(f"User '{user.full_name}' role updated to {user.role.upper()}.", "success")
    return redirect(url_for('admin.dashboard'))
