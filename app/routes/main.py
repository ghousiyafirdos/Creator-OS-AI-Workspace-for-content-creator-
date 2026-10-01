from flask import Blueprint, jsonify, redirect, url_for, render_template, request
from datetime import datetime
from flask_login import login_required, current_user
from app.services.translation_service import translate_many
from app.models.ai import AIHistory
from app.models.draft import Draft
from app.models.planner import PlannerItem

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
@login_required
def index():
    """Authenticated users land on the CreatorOS Dashboard."""
    return dashboard()

@main_bp.route("/dashboard")
@login_required
def dashboard():
    """CreatorOS Dashboard page with live user activity."""
    now = datetime.now()
    ai_count = AIHistory.query.filter_by(user_id=current_user.id).count()
    published_count = PlannerItem.query.filter_by(user_id=current_user.id, status='published').count()
    scheduled_count = PlannerItem.query.filter_by(user_id=current_user.id, status='scheduled').count()
    total_planned = PlannerItem.query.filter_by(user_id=current_user.id).count()
    active_draft_count = Draft.query.filter_by(user_id=current_user.id, is_deleted=False).count()
    draft_items = Draft.query.filter_by(user_id=current_user.id, is_deleted=False).order_by(Draft.updated_at.desc()).limit(4).all()
    upcoming = PlannerItem.query.filter(
        PlannerItem.user_id == current_user.id,
        PlannerItem.status == 'scheduled',
        PlannerItem.scheduled_time >= now
    ).order_by(PlannerItem.scheduled_time.asc()).limit(4).all()

    # Data used by the clickable Activity checklist on the dashboard.
    recent_ai = AIHistory.query.filter_by(user_id=current_user.id).order_by(AIHistory.created_at.desc()).limit(8).all()
    recent_scheduled = PlannerItem.query.filter_by(user_id=current_user.id, status='scheduled').order_by(PlannerItem.scheduled_time.asc()).limit(8).all()
    recent_published = PlannerItem.query.filter_by(user_id=current_user.id, status='published').order_by(PlannerItem.scheduled_time.desc()).limit(8).all()
    recent_drafts = Draft.query.filter_by(user_id=current_user.id, is_deleted=False).order_by(Draft.updated_at.desc()).limit(8).all()

    if 5 <= now.hour < 12:
        greeting = "Good morning"
    elif 12 <= now.hour < 17:
        greeting = "Good afternoon"
    elif 17 <= now.hour < 21:
        greeting = "Good evening"
    else:
        greeting = "Good night"

    activity_data = {
        "ai": [{"title": f"{x.tool_type.title()} generation", "meta": x.created_at.strftime("%b %d, %I:%M %p")} for x in recent_ai],
        "scheduled": [{"title": x.title, "meta": f"{x.scheduled_time.strftime('%b %d, %I:%M %p')} · {x.platform}"} for x in recent_scheduled],
        "drafts": [{"title": x.title, "meta": x.updated_at.strftime("%b %d, %I:%M %p") if x.updated_at else "Recently updated"} for x in recent_drafts],
        "published": [{"title": x.title, "meta": f"{x.scheduled_time.strftime('%b %d, %I:%M %p')} · {x.platform}"} for x in recent_published]
    }

    return render_template(
        "dashboard.html",
        current_date=now.strftime("%A, %B %d, %Y"),
        greeting=greeting,
        ai_count=ai_count,
        published_count=published_count,
        scheduled_count=scheduled_count,
        total_planned=total_planned,
        draft_items=draft_items,
        active_draft_count=active_draft_count,
        upcoming=upcoming,
        activity_data=activity_data
    )

@main_bp.route("/api/health")
def health():
    return jsonify({
        "status": "healthy",
        "system": "CreatorOS",
        "timestamp": datetime.now().isoformat()
    })


@main_bp.route("/api/translate-ui", methods=["POST"])
@login_required
def translate_ui():
    """Translate fixed UI labels missing from the built-in language dictionary."""
    data = request.get_json() or {}
    language = data.get("language") or current_user.language or "English"
    texts = data.get("texts") or []
    if not isinstance(texts, list):
        return jsonify({"translations": {}}), 400
    return jsonify({"translations": translate_many(texts[:80], language)})
