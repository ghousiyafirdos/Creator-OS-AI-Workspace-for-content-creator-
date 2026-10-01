import os
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from datetime import datetime
from werkzeug.utils import secure_filename
from app import db
from app.models.draft import Draft

drafts_bp = Blueprint('drafts', __name__, url_prefix='/drafts')

ALLOWED_IMAGE = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_VIDEO = {'mp4', 'mov', 'avi', 'mkv'}
ALLOWED_DOC = {'pdf', 'docx', 'doc', 'txt', 'csv', 'xlsx'}

def get_file_category(filename):
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    if ext in ALLOWED_IMAGE:
        return 'image'
    elif ext in ALLOWED_VIDEO:
        return 'video'
    elif ext in ALLOWED_DOC:
        return 'document'
    return 'text'

@drafts_bp.route('/manager')
@login_required
def manager():
    """Main Draft Manager page displaying drafts, search/filter tools, and file cards."""
    file_filter = request.args.get('type', 'all')
    search_query = request.args.get('search', '').strip()
    favorites_only = request.args.get('favorites', 'false').lower() == 'true'

    query = Draft.query.filter_by(user_id=current_user.id, is_deleted=False)

    if file_filter != 'all':
        query = query.filter_by(file_type=file_filter)

    if favorites_only:
        query = query.filter_by(is_favorite=True)

    if search_query:
        query = query.filter(
            (Draft.title.ilike(f'%{search_query}%')) | 
            (Draft.content.ilike(f'%{search_query}%'))
        )

    drafts = query.order_by(Draft.updated_at.desc()).all()
    return render_template('drafts/manager.html', 
                           drafts=drafts, 
                           file_filter=file_filter,
                           search_query=search_query,
                           favorites_only=favorites_only)

@drafts_bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    """Handles file uploads and saves them as drafts."""
    title = request.form.get('title', '').strip() or 'Untitled Draft'
    content = request.form.get('content', '').strip()
    uploaded_file = request.files.get('file')

    file_path = None
    file_type = 'text'
    file_size_mb = 0.0

    if uploaded_file and uploaded_file.filename != '':
        filename = secure_filename(uploaded_file.filename)
        file_category = get_file_category(filename)
        
        # Calculate file size in MB
        uploaded_file.seek(0, os.SEEK_END)
        size_bytes = uploaded_file.tell()
        uploaded_file.seek(0)
        file_size_mb = round(size_bytes / (1024 * 1024), 2)

        # Check 100 MB Storage Limit
        current_storage = Draft.get_user_storage_mb(current_user.id)
        if (current_storage + file_size_mb) > 100.0:
            flash(f"Upload rejected: Exceeds 100 MB storage limit! Current storage: {current_storage} MB", "danger")
            return redirect(url_for('drafts.manager'))

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f_")
        stored_filename = timestamp + filename
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], stored_filename)
        uploaded_file.save(save_path)

        # The file is stored on disk and its relative path is persisted in the
        # database. This makes uploaded drafts survive browser/app restarts.
        file_path = f"uploads/{stored_filename}"
        file_type = file_category
        if title == 'Untitled Draft':
            title = filename

    draft = Draft(
        user_id=current_user.id,
        title=title,
        content=content,
        file_path=file_path,
        file_type=file_type,
        file_size_mb=file_size_mb
    )
    db.session.add(draft)
    db.session.commit()

    flash(f"Draft '{title}' saved successfully!", "success")
    return redirect(url_for('drafts.manager'))

@drafts_bp.route('/auto-save', methods=['POST'])
@login_required
def auto_save():
    """AJAX endpoint for real-time auto-saving text drafts."""
    data = request.get_json() or {}
    draft_id = data.get('draft_id')
    title = data.get('title', '').strip() or 'Untitled Draft'
    content = data.get('content', '').strip()

    if draft_id:
        draft = Draft.query.filter_by(id=draft_id, user_id=current_user.id).first()
        if draft:
            draft.title = title
            draft.content = content
            db.session.commit()
            return jsonify({'success': True, 'draft_id': draft.id, 'saved_at': datetime.utcnow().strftime('%H:%M:%S')})

    # Create new auto-saved draft
    new_draft = Draft(
        user_id=current_user.id,
        title=title,
        content=content,
        file_type='text'
    )
    db.session.add(new_draft)
    db.session.commit()
    return jsonify({'success': True, 'draft_id': new_draft.id, 'saved_at': datetime.utcnow().strftime('%H:%M:%S')})

@drafts_bp.route('/favorite/<int:draft_id>', methods=['POST'])
@login_required
def toggle_favorite(draft_id):
    """Toggles favorite status for a draft."""
    draft = Draft.query.filter_by(id=draft_id, user_id=current_user.id).first_or_404()
    draft.is_favorite = not draft.is_favorite
    db.session.commit()
    return jsonify({'success': True, 'is_favorite': draft.is_favorite})

@drafts_bp.route('/delete/<int:draft_id>', methods=['POST'])
@login_required
def soft_delete(draft_id):
    """Moves a draft to the Recycle Bin (Soft Delete)."""
    draft = Draft.query.filter_by(id=draft_id, user_id=current_user.id).first_or_404()
    draft.is_deleted = True
    draft.deleted_at = datetime.utcnow()
    db.session.commit()
    flash(f"Draft Manager: '{draft.title}' was deleted and moved to the Recycle Bin.", "warning")
    return redirect(url_for('drafts.manager'))

@drafts_bp.route('/recycle-bin')
@login_required
def recycle_bin():
    """Recycle Bin page listing soft-deleted files with 30-day restoration countdown."""
    deleted_drafts = Draft.query.filter_by(user_id=current_user.id, is_deleted=True).order_by(Draft.deleted_at.desc()).all()
    return render_template('drafts/recycle_bin.html', drafts=deleted_drafts)

@drafts_bp.route('/restore/<int:draft_id>', methods=['POST'])
@login_required
def restore_draft(draft_id):
    """Restores a soft-deleted draft from the Recycle Bin."""
    draft = Draft.query.filter_by(id=draft_id, user_id=current_user.id).first_or_404()
    draft.is_deleted = False
    draft.deleted_at = None
    db.session.commit()
    flash(f"Draft '{draft.title}' restored to Draft Manager!", "success")
    return redirect(url_for('drafts.recycle_bin'))

@drafts_bp.route('/purge/<int:draft_id>', methods=['POST'])
@login_required
def purge_draft(draft_id):
    """Permanently deletes a draft and its associated file from disk."""
    draft = Draft.query.filter_by(id=draft_id, user_id=current_user.id).first_or_404()
    
    # Remove file from disk if present
    if draft.file_path:
        full_path = os.path.join(current_app.static_folder, draft.file_path)
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
            except OSError:
                pass

    db.session.delete(draft)
    db.session.commit()
    flash(f"Draft Manager: '{draft.title}' was permanently deleted.", "info")
    return redirect(url_for('drafts.recycle_bin'))
