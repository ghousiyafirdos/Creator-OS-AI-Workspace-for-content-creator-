import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user, login_user
from werkzeug.utils import secure_filename
from datetime import datetime
from app import db
from app.models.user import User
from app.models.settings import Settings

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

ALLOWED_AVATARS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

@profile_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Profile Settings route for editing name, profile picture, language, and account settings."""
    user_settings = Settings.query.filter_by(user_id=current_user.id).first()
    if not user_settings:
        user_settings = Settings(user_id=current_user.id)
        db.session.add(user_settings)
        db.session.commit()

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        language = request.form.get('language', 'English')
        if language not in {
            'English','Hindi','Bengali','Marathi','Telugu','Tamil','Kannada','Malayalam',
            'Gujarati','Punjabi','Urdu','Odia','Assamese','Spanish','French','German',
            'Dutch','Portuguese','Italian','Chinese','Japanese','Korean','Arabic','Russian'
        }:
            language = 'English'

        dob_raw = request.form.get('date_of_birth', '').strip()
        try:
            date_of_birth = datetime.strptime(dob_raw, '%Y-%m-%d').date() if dob_raw else None
        except ValueError:
            date_of_birth = None
        current_user.date_of_birth = date_of_birth
        current_user.phone = request.form.get('phone', '').strip() or None
        current_user.gender = request.form.get('gender', '').strip() or None
        current_user.location = request.form.get('location', '').strip() or None
        current_user.bio = request.form.get('bio', '').strip() or None
        current_user.instagram = request.form.get('instagram', '').strip() or None
        current_user.youtube = request.form.get('youtube', '').strip() or None
        new_email = request.form.get('email', '').strip().lower()
        if new_email and new_email != (current_user.email or '').lower():
            existing = User.query.filter(User.email.ilike(new_email), User.id != current_user.id).first()
            if existing:
                flash('That email address is already in use.', 'warning')
                return redirect(url_for('profile.settings'))
            current_user.email = new_email
        new_password = request.form.get('new_password', '').strip()

        if full_name:
            current_user.full_name = full_name
        current_user.language = language
        user_settings.default_language = language

        # Profile Picture Upload
        avatar_file = request.files.get('profile_pic')
        if avatar_file and avatar_file.filename != '':
            ext = avatar_file.filename.rsplit('.', 1)[-1].lower() if '.' in avatar_file else ''
            if ext in ALLOWED_AVATARS:
                filename = secure_filename(f"avatar_user_{current_user.id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.{ext}")
                save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                avatar_file.save(save_path)
                current_user.profile_pic = f"uploads/{filename}"

        # Password Update
        if new_password:
            if len(new_password) >= 8:
                current_user.set_password(new_password)
                flash("Password updated successfully!", "info")
            else:
                flash("Password must be at least 8 characters long.", "warning")

        db.session.commit()
        flash("Profile & Settings updated successfully!", "success")
        return redirect(url_for('profile.settings'))

    return render_template('profile/settings.html', settings=user_settings)

@profile_bp.route('/upload-photo', methods=['POST'])
@login_required
def upload_photo():
    """AJAX profile-photo upload used by the camera button. Returns JSON so the page never loses the selected file."""
    avatar_file = request.files.get('profile_pic')
    if not avatar_file or not avatar_file.filename:
        return {"success": False, "error": "No image was selected."}, 400

    ext = avatar_file.filename.rsplit('.', 1)[-1].lower() if '.' in avatar_file.filename else ''
    if ext not in ALLOWED_AVATARS or not (avatar_file.mimetype or '').startswith('image/'):
        return {"success": False, "error": "Please choose a valid PNG, JPG, JPEG, GIF, or WEBP image."}, 400

    filename = secure_filename(f"avatar_user_{current_user.id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}.{ext}")
    save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    avatar_file.save(save_path)
    current_user.profile_pic = f"uploads/{filename}"
    db.session.commit()

    # The sidebar avatar uses a normal multipart form so the upload cannot be lost when the
    # file picker closes. Keep JSON support for any existing AJAX clients.
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept',''):
        return {"success": True, "url": url_for('static', filename=current_user.profile_pic), "path": current_user.profile_pic}
    return redirect(request.form.get('return_to') or url_for('profile.settings'))

@profile_bp.route('/demo-user')
def demo_user():
    """One-click instant login for Demo Creator account."""
    demo_email = 'demo@creatoros.ai'
    user = User.query.filter_by(email=demo_email).first()

    if not user:
        user = User(
            full_name='Demo Creator',
            email=demo_email,
            role='creator',
            is_verified=True,
            language='English',
            theme='light'
        )
        user.set_password('DemoCreator@2026')
        db.session.add(user)
        db.session.commit()

    login_user(user)
    flash("Welcome! Logged in as Demo Creator.", "success")
    return redirect(url_for('main.index'))
