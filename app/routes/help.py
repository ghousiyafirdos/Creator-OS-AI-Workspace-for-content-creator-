from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models.help import Feedback

help_bp = Blueprint('help', __name__, url_prefix='/help')

FAQS = [
    {
        "question": "How does the AI Workspace work in CreatorOS?",
        "answer": "CreatorOS provides 6 specialized AI generators (Caption, Script, Hashtag, Bio, Rewrite, SEO). Enter your topic or draft, select options, and click Generate. The system operates online with intelligent offline fallback algorithms."
    },
    {
        "question": "What is the file storage limit in Draft Manager?",
        "answer": "Each creator account is allocated 100 MB of cloud storage for images (PNG, JPG), videos (MP4, MOV), and documents (PDF, DOCX). Storage usage is tracked live on your Draft Manager gauge."
    },
    {
        "question": "How does the 30-Day Recycle Bin work?",
        "answer": "When you delete a draft, it is moved to the Recycle Bin for 30 days. You can restore it anytime within 30 days before permanent automatic purging."
    },
    {
        "question": "How is my Productivity Score calculated?",
        "answer": "Productivity Score (0–100) evaluates your weekly content activity: active AI generations (+4 pts each), published posts (+8 pts each), and a consistency baseline (+20 pts)."
    },
    {
        "question": "Can I customize the CreatorOS appearance?",
        "answer": "CreatorOS uses one consistent appearance across all modules."
    }
]

@help_bp.route('/center')

def center():
    """Help Center hub page rendering FAQs, Contact Form, About Card & Feedback Form."""
    recent_feedback = []
    if current_user.is_authenticated:
        recent_feedback = Feedback.query.filter_by(user_id=current_user.id).order_by(Feedback.created_at.desc()).limit(3).all()
    return render_template('help/center.html', faqs=FAQS, recent_feedback=recent_feedback)

@help_bp.route('/contact', methods=['POST'])

def contact():
    """Processes contact support inquiry."""
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    subject = request.form.get('subject', '').strip()
    message = request.form.get('message', '').strip()

    if not name or not email or not message:
        flash("Please fill in all required contact fields.", "danger")
        return redirect(url_for('help.center'))

    flash("Thank you! Your inquiry has been submitted. Our support team will respond shortly.", "success")
    return redirect(url_for('help.center'))

@help_bp.route('/feedback', methods=['POST'])
@login_required
def submit_feedback():
    """Saves user rating & feedback comments into Feedback table."""
    rating = int(request.form.get('rating', 5))
    category = request.form.get('category', 'General')
    comments = request.form.get('comments', '').strip()

    if not comments:
        flash("Please enter feedback comments before submitting.", "warning")
        return redirect(url_for('help.center'))

    entry = Feedback(
        user_id=current_user.id,
        rating=rating,
        category=category,
        comments=comments
    )
    db.session.add(entry)
    db.session.commit()

    flash("Thank you for your feedback! Your rating helps us improve CreatorOS.", "success")
    return redirect(url_for('help.center'))
