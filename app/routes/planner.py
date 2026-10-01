from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models.planner import PlannerItem

planner_bp = Blueprint('planner', __name__, url_prefix='/planner')

@planner_bp.route('/calendar')
@login_required
def calendar():
    """Main Content Planner view rendering calendar grid and filterable post list."""
    status_filter = request.args.get('status', 'all')
    
    # Update expired scheduled items to 'missed' status
    items_to_check = PlannerItem.query.filter_by(user_id=current_user.id, status='scheduled').all()
    for item in items_to_check:
        item.update_status_if_missed()

    query = PlannerItem.query.filter_by(user_id=current_user.id)
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)

    items = query.order_by(PlannerItem.scheduled_time.asc()).all()

    # Calculate status count badges
    counts = {
        'all': PlannerItem.query.filter_by(user_id=current_user.id).count(),
        'draft': PlannerItem.query.filter_by(user_id=current_user.id, status='draft').count(),
        'scheduled': PlannerItem.query.filter_by(user_id=current_user.id, status='scheduled').count(),
        'published': PlannerItem.query.filter_by(user_id=current_user.id, status='published').count(),
        'missed': PlannerItem.query.filter_by(user_id=current_user.id, status='missed').count(),
    }

    return render_template('planner/calendar.html', 
                           items=items, 
                           counts=counts, 
                           status_filter=status_filter)

@planner_bp.route('/schedule', methods=['POST'])
@login_required
def schedule_post():
    """Schedule a new social media post or save as draft."""
    title = request.form.get('title', '').strip()
    caption = request.form.get('caption', '').strip()
    platform = request.form.get('platform', 'Instagram')
    date_str = request.form.get('scheduled_date', '')
    time_str = request.form.get('scheduled_time', '12:00')
    as_draft = request.form.get('as_draft', 'false').lower() == 'true'
    reminder = request.form.get('reminder', 'false').lower() == 'true'

    if not title or not date_str:
        flash("Title and scheduled date are required.", "danger")
        return redirect(url_for('planner.calendar'))

    try:
        combined_dt_str = f"{date_str} {time_str}"
        scheduled_dt = datetime.strptime(combined_dt_str, "%Y-%m-%d %H:%M")
    except ValueError:
        flash("Invalid date or time format.", "danger")
        return redirect(url_for('planner.calendar'))

    status = 'draft' if as_draft else ('scheduled' if scheduled_dt > datetime.utcnow() else 'published')

    item = PlannerItem(
        user_id=current_user.id,
        title=title,
        caption=caption,
        platform=platform,
        scheduled_time=scheduled_dt,
        status=status,
        reminder_sent=reminder
    )
    db.session.add(item)
    db.session.commit()

    flash(f"Post '{title}' successfully added to Planner as {status.upper()}!", "success")
    return redirect(url_for('planner.calendar'))

@planner_bp.route('/status/<int:item_id>', methods=['POST'])
@login_required
def update_status(item_id):
    """Updates status for a planned post item (draft, scheduled, published)."""
    item = PlannerItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    new_status = request.form.get('new_status') or (request.json.get('new_status') if request.json else None)

    if new_status in ['draft', 'scheduled', 'published', 'missed']:
        item.status = new_status
        db.session.commit()
        if request.is_json:
            return jsonify({'success': True, 'status': new_status})
        flash(f"Post status updated to {new_status.upper()}.", "success")
    
    return redirect(url_for('planner.calendar'))

@planner_bp.route('/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    """Deletes a planned post entry."""
    item = PlannerItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    flash(f"Content Calendar: '{item.title}' was deleted.", "info")
    return redirect(url_for('planner.calendar'))

@planner_bp.route('/api/sync-calendar', methods=['POST'])
@login_required
def sync_calendar():
    """Synchronize the browser calendar with Planner so Calendar and Analytics use the same records."""
    data = request.get_json() or {}
    events = data.get('events') or []
    if not isinstance(events, list):
        return jsonify({'success': False, 'error': 'Invalid calendar data.'}), 400

    incoming_uids = set()
    for event in events:
        if not isinstance(event, dict) or event.get('isFestival'):
            continue
        uid = str(event.get('id') or '').strip()
        title = str(event.get('title') or '').strip()[:200]
        date_str = str(event.get('date') or '').strip()
        time_str = str(event.get('time') or '00:00').strip()
        platform = str(event.get('platform') or 'Instagram')[:50]
        notes = str(event.get('notes') or '')
        status = event.get('status') if event.get('status') in {'draft','scheduled','published','missed'} else ('missed' if event.get('status') == 'finished' else 'scheduled')
        if not uid or not title or not date_str:
            continue
        try:
            dt = datetime.strptime(f'{date_str} {time_str}', '%Y-%m-%d %H:%M')
        except ValueError:
            continue
        incoming_uids.add(uid)
        item = PlannerItem.query.filter_by(user_id=current_user.id, calendar_uid=uid).first()
        if item is None:
            item = PlannerItem(user_id=current_user.id, calendar_uid=uid, title=title, caption=notes, platform=platform, scheduled_time=dt, status=status)
            db.session.add(item)
        else:
            item.title=title; item.caption=notes; item.platform=platform; item.scheduled_time=dt; item.status=status

    # Remove only records created/synced by this calendar, not posts created through the normal Planner form.
    synced_items = PlannerItem.query.filter(PlannerItem.user_id == current_user.id, PlannerItem.calendar_uid.isnot(None)).all()
    for item in synced_items:
        if item.calendar_uid not in incoming_uids:
            db.session.delete(item)
    db.session.commit()
    return jsonify({'success': True, 'synced': len(incoming_uids)})

@planner_bp.route('/api/events')
@login_required
def get_events():
    """Returns JSON payload of scheduled items for calendar grid integration."""
    items = PlannerItem.query.filter_by(user_id=current_user.id).all()
    events = [item.to_dict() for item in items]
    return jsonify(events)
