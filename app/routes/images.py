from flask import Blueprint, jsonify, redirect, render_template, request, url_for
import logging
import time
import uuid
from pathlib import Path
from flask_login import login_required
from werkzeug.utils import secure_filename

from app.services.gemini_visual import GeminiVisualService

images_bp = Blueprint("images", __name__, url_prefix="/images")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
UPLOAD_DIR = PROJECT_ROOT / "static" / "uploads" / "image_studio"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif", "bmp", "svg"}
MAX_IMAGES_PER_UPLOAD = 20
MAX_FILE_SIZE = 25 * 1024 * 1024


def _allowed(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@images_bp.route("/thumbnails")
@login_required
def thumbnails():
    """Pick Perfect image editor; old thumbnail URL redirects to its branded route."""
    if request.path == "/images/thumbnails":
        return redirect(url_for("pick_perfect"), code=301)
    return render_template("images/image_generator.html")


@images_bp.route("/upload", methods=["POST"])
@login_required
def upload_images():
    """Persist up to ten uploaded images for the Pick Perfect editor."""
    files = request.files.getlist("images")
    if not files:
        return jsonify({"ok": False, "error": "Choose at least one image."}), 400
    if len(files) > MAX_IMAGES_PER_UPLOAD:
        return jsonify({"ok": False, "error": "You can upload a maximum of 20 images at a time."}), 400

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    uploaded = []

    for file in files:
        if not file or not file.filename:
            continue
        if not _allowed(file.filename):
            continue

        file.stream.seek(0, 2)
        size = file.stream.tell()
        file.stream.seek(0)
        if size > MAX_FILE_SIZE:
            return jsonify({"ok": False, "error": f"{file.filename} is larger than 25 MB."}), 400

        original = secure_filename(file.filename) or "image"
        stem = Path(original).stem[:50] or "image"
        ext = Path(original).suffix.lower() or ".jpg"
        filename = f"{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}_{stem}{ext}"
        destination = UPLOAD_DIR / filename
        file.save(destination)
        uploaded.append({
            "name": original,
            "url": f"/static/uploads/image_studio/{filename}",
            "type": "image",
            "createdAt": time.time(),
        })

    if not uploaded:
        return jsonify({"ok": False, "error": "No supported image files were selected."}), 400

    return jsonify({"ok": True, "images": uploaded, "count": len(uploaded)})


@images_bp.route("/library")
@login_required
def image_library():
    """Return the Pick Perfect editor's persisted uploaded/generated images."""
    folders = [
        PROJECT_ROOT / "static" / "uploads" / "image_studio",
        PROJECT_ROOT / "static" / "uploads" / "generated_visuals",
    ]
    items = []
    for folder in folders:
        if not folder.exists():
            continue
        for path in folder.iterdir():
            if path.is_file() and path.suffix.lower().lstrip(".") in ALLOWED_EXTENSIONS:
                items.append({
                    "name": path.name,
                    "url": "/static/uploads/" + folder.name + "/" + path.name,
                    "type": "image",
                    "createdAt": path.stat().st_mtime,
                })
    items.sort(key=lambda x: x["createdAt"], reverse=True)
    return jsonify({"ok": True, "images": items[:50]})


@images_bp.route("/library/delete", methods=["POST"])
@login_required
def delete_library_image():
    """Delete one image from the Images & Thumbnails library."""
    data = request.get_json(silent=True) or {}
    raw_url = str(data.get("url") or "").strip()
    filename = Path(raw_url.split("?", 1)[0]).name
    if not filename or filename in {".", ".."} or ".." in filename:
        return jsonify({"ok": False, "error": "Invalid image."}), 400

    allowed_folders = [
        PROJECT_ROOT / "static" / "uploads" / "image_studio",
        PROJECT_ROOT / "static" / "uploads" / "generated_visuals",
    ]
    for folder in allowed_folders:
        target = folder / filename
        if target.exists() and target.is_file():
            try:
                target.unlink()
                return jsonify({"ok": True})
            except OSError:
                return jsonify({"ok": False, "error": "Image could not be removed."}), 500
    return jsonify({"ok": False, "error": "Image not found."}), 404


@images_bp.route("/generate", methods=["POST"])
@login_required
def generate_visual():
    """Generate a real image with the configured Gemini image model."""
    data = request.get_json(silent=True) or {}
    thumbnail_title = (data.get("thumbnail_title") or "").strip()

    if not thumbnail_title:
        return jsonify({"ok": False, "error": "Enter a topic first."}), 400

    try:
        image_url, model = GeminiVisualService.generate(
            thumbnail_title=thumbnail_title,
        )
        return jsonify({
            "ok": True,
            "image_url": image_url,
            "model": model,
            "message": "Visual generated with Gemini.",
        })
    except Exception as exc:
        logger.exception("Images & Thumbnails Gemini generation failed")
        raw = str(exc).strip().lower()
        if "api key is missing" in raw:
            message = "Image generation is not configured yet."
        elif "paid gemini" in raw or "quota" in raw or "resource_exhausted" in raw:
            message = "AI image generation is unavailable for the current Gemini API access."
        elif "invalid" in raw or "permission" in raw or "unauthenticated" in raw:
            message = "The Gemini image service is not authorized for this project."
        elif "not available" in raw or "not_found" in raw:
            message = "The configured Gemini image model is not available for this project."
        elif "busy" in raw or "temporarily" in raw or "unavailable" in raw:
            message = "The AI image service is temporarily busy. Please try again."
        elif "timeout" in raw or "deadline" in raw:
            message = "The AI image service took too long to respond. Please try again."
        else:
            message = "The thumbnail could not be generated. Please try again."
        return jsonify({"ok": False, "error": message}), 502
