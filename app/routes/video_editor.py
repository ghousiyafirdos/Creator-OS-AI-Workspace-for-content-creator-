from flask import Blueprint, render_template
from flask_login import login_required

video_editor_bp = Blueprint("video_editor", __name__, url_prefix="/video-editor")

@video_editor_bp.route("/")
@login_required
def editor():
    """Integrated Video Editor inside the shared CreatorOS shell."""
    return render_template("video_editor.html")
