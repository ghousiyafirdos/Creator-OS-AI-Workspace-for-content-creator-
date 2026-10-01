from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func
from app import db
from app.models.ai import AIHistory
from app.models.planner import PlannerItem
from app.models.analytics import Analytics

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')

@analytics_bp.route('/dashboard')
@login_required
def dashboard():
    """Analytics Dashboard displaying KPI cards, Chart.js trends, and Productivity Score."""
    current_month = datetime.utcnow().strftime("%Y-%m")

    # Aggregate AI Generations count for current user
    ai_count = AIHistory.query.filter_by(user_id=current_user.id).count()

    # Aggregate Published Posts count for current user
    published_count = PlannerItem.query.filter_by(user_id=current_user.id, status='published').count()
    scheduled_count = PlannerItem.query.filter_by(user_id=current_user.id, status='scheduled').count()

    # Find Most Used AI Tool
    most_used_query = db.session.query(
        AIHistory.tool_type, func.count(AIHistory.tool_type).label('count')
    ).filter_by(user_id=current_user.id).group_by(AIHistory.tool_type).order_by(func.count(AIHistory.tool_type).desc()).first()

    most_used_tool = most_used_query[0].capitalize() + " Generator" if most_used_query else "Caption Generator"

    # Get or create Analytics entry for current month
    analytics_record = Analytics.query.filter_by(user_id=current_user.id, month_year=current_month).first()
    if not analytics_record:
        analytics_record = Analytics(
            user_id=current_user.id,
            month_year=current_month,
            ai_generations_count=ai_count,
            posts_published=published_count,
            followers_count=12400 + (published_count * 150),
            likes_count=84200 + (published_count * 1200),
            views_count=340500 + (published_count * 5400),
            most_used_tool=most_used_tool
        )
        db.session.add(analytics_record)
    else:
        analytics_record.ai_generations_count = ai_count
        analytics_record.posts_published = published_count
        analytics_record.most_used_tool = most_used_tool
        analytics_record.followers_count = 12400 + (published_count * 150)
        analytics_record.likes_count = 84200 + (published_count * 1200)
        analytics_record.views_count = 340500 + (published_count * 5400)
    
    db.session.commit()

    # Score is based on current activity, so creating, publishing, unpublishing, or deleting
    # activity changes it in both directions instead of leaving a permanent 20-point floor.
    productivity_score = min(100, max(0, (ai_count * 5) + (published_count * 10) + (scheduled_count * 3)))

    # Breakdown of AI Tool Usage for chart
    tool_counts = {
        'Caption': AIHistory.query.filter_by(user_id=current_user.id, tool_type='caption').count(),
        'Script': AIHistory.query.filter_by(user_id=current_user.id, tool_type='script').count(),
        'Hashtag': AIHistory.query.filter_by(user_id=current_user.id, tool_type='hashtag').count(),
        'Bio': AIHistory.query.filter_by(user_id=current_user.id, tool_type='bio').count(),
        'Rewrite': AIHistory.query.filter_by(user_id=current_user.id, tool_type='rewrite').count(),
        'SEO': AIHistory.query.filter_by(user_id=current_user.id, tool_type='seo').count(),
    }

    # Keep the last displayed score so the dashboard can clearly show movement.
    previous_score = int(analytics_record.previous_productivity_score or 0)
    if analytics_record.previous_productivity_score == 0 and productivity_score == 0:
        previous_score = 0
    analytics_record.previous_productivity_score = productivity_score
    db.session.commit()
    # Real daily activity for the last seven days (AI generations + planner items).
    today = datetime.utcnow().date()
    weekly_labels, weekly_activity = [], []
    for offset in range(6, -1, -1):
        day = today - timedelta(days=offset)
        start = datetime.combine(day, datetime.min.time())
        end = start + timedelta(days=1)
        weekly_labels.append(day.strftime('%a'))
        ai_day = AIHistory.query.filter(AIHistory.user_id == current_user.id, AIHistory.created_at >= start, AIHistory.created_at < end).count()
        plan_day = PlannerItem.query.filter(PlannerItem.user_id == current_user.id, PlannerItem.created_at >= start, PlannerItem.created_at < end).count()
        weekly_activity.append(ai_day + plan_day)

    recent_activity = []
    recent_ai = AIHistory.query.filter_by(user_id=current_user.id).order_by(AIHistory.created_at.desc()).limit(5).all()
    recent_plans = PlannerItem.query.filter_by(user_id=current_user.id).order_by(PlannerItem.created_at.desc()).limit(5).all()
    for row in recent_ai:
        recent_activity.append({'dt': row.created_at, 'title': f'Created {row.tool_type.capitalize()} content', 'when': row.created_at.strftime('%d %b · %I:%M %p'), 'icon': 'bi-stars', 'color': 'pink', 'url': '/ai/history'})
    for row in recent_plans:
        recent_activity.append({'dt': row.created_at, 'title': f'{row.status.capitalize()}: {row.title}', 'when': row.created_at.strftime('%d %b · %I:%M %p'), 'icon': 'bi-calendar3', 'color': 'teal', 'url': '/planner/calendar'})
    recent_activity.sort(key=lambda x: x['dt'] or datetime.min, reverse=True)
    recent_activity = recent_activity[:4]
    for row in recent_activity:
        row.pop('dt', None)

    module_activity = [
        {'name':'Idea Flow','count':ai_count,'percent':min(100, ai_count*8),'icon':'bi-stars','color':'violet'},
        {'name':'Pixel','count':0,'percent':0,'icon':'bi-image','color':'pink'},
        {'name':'Motion','count':0,'percent':0,'icon':'bi-play-fill','color':'orange'},
        {'name':'Ink','count':published_count,'percent':min(100, published_count*12),'icon':'bi-file-earmark-text','color':'teal'},
        {'name':'Tempo','count':scheduled_count,'percent':min(100, scheduled_count*18),'icon':'bi-calendar3','color':'blue'},
    ]
    max_count = max([x['count'] for x in module_activity] or [1]) or 1
    for item in module_activity:
        item['percent'] = max(4, int(item['count'] / max_count * 100)) if item['count'] else 0

    return render_template('analytics/dashboard.html',
                           analytics=analytics_record,
                           productivity_score=productivity_score,
                           previous_score=previous_score,
                           score_delta=productivity_score-previous_score,
                           tool_counts=tool_counts,
                           scheduled_count=scheduled_count,
                           weekly_labels=weekly_labels,
                           weekly_activity=weekly_activity,
                           module_activity=module_activity,
                           recent_activity=recent_activity)

@analytics_bp.route('/api/data')
@login_required
def get_analytics_data():
    """Returns JSON payload formatted for Chart.js charts."""
    months = ['Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul']
    views_data = [45000, 78000, 120000, 195000, 260000, 340500]
    likes_data = [12000, 22000, 38000, 54000, 69000, 84200]
    followers_data = [2400, 4100, 6800, 8900, 10500, 12400]

    tool_types = ['Caption', 'Script', 'Hashtag', 'Bio', 'Rewrite', 'SEO']
    tool_counts = [
        AIHistory.query.filter_by(user_id=current_user.id, tool_type=tt.lower()).count() or 1
        for tt in tool_types
    ]

    scheduled_count = PlannerItem.query.filter_by(user_id=current_user.id, status='scheduled').count()
    ai_count = AIHistory.query.filter_by(user_id=current_user.id).count()
    published_count = PlannerItem.query.filter_by(user_id=current_user.id, status='published').count()
    productivity_score = min(100, max(0, (ai_count * 5) + (published_count * 10) + (scheduled_count * 3)))
    previous_record = Analytics.query.filter_by(user_id=current_user.id, month_year=datetime.utcnow().strftime('%Y-%m')).first()
    previous_score = int(previous_record.previous_productivity_score or 0) if previous_record else productivity_score

    return jsonify({
        'productivity_score': productivity_score,
        'previous_score': previous_score,
        'score_delta': productivity_score - previous_score,
        'ai_generations': ai_count,
        'published': published_count,
        'scheduled': scheduled_count,
        'months': months,
        'views': views_data,
        'likes': likes_data,
        'followers': followers_data,
        'tool_labels': tool_types,
        'tool_counts': tool_counts
    })
