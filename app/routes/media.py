from flask import Blueprint, render_template
from flask_login import login_required

media_bp = Blueprint("media", __name__, url_prefix="/media")

@media_bp.route("/assets")
@login_required
def assets():
    """Integrated Media & Assets Library inside the main CreatorOS shell."""
    return render_template("media/asset_library.html")
