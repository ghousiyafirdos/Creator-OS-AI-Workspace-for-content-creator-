import os
from flask import Flask, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__, 
                template_folder='../templates', 
                static_folder='../static')
    app.config.from_object(config_class)

    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER'].parent / 'database', exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register Blueprints & Models
    from app.models.user import User
    from app.models.ai import AIHistory, ChatHistory
    from app.models.planner import PlannerItem
    from app.models.analytics import Analytics
    from app.models.draft import Draft
    from app.models.help import Feedback
    from app.models.settings import Settings
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.ai import ai_bp
    from app.routes.planner import planner_bp
    from app.routes.analytics import analytics_bp
    from app.routes.drafts import drafts_bp
    from app.routes.help import help_bp
    from app.routes.profile import profile_bp
    from app.routes.admin import admin_bp
    from app.routes.images import images_bp
    from app.routes.media import media_bp
    from app.routes.video_editor import video_editor_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(planner_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(drafts_bp)
    app.register_blueprint(help_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(images_bp)
    # Canonical branded route for the Pick Perfect module.
    app.add_url_rule(
        "/pick-perfect",
        endpoint="pick_perfect",
        view_func=app.view_functions["images.thumbnails"],
    )
    app.register_blueprint(media_bp)
    app.register_blueprint(video_editor_bp)

    # Public-facing module URLs use the current CreatorOS names. Existing
    # endpoint URLs remain supported and are redirected to these canonical paths.
    canonical_routes = {
        "/launchpad": app.view_functions["main.dashboard"],
        "/idea-flow": app.view_functions["ai.workspace"],
        "/media-bloom": app.view_functions["media.assets"],
        "/clip-nest": app.view_functions["video_editor.editor"],
        "/day-canvas": app.view_functions["planner.calendar"],
        "/craft-nest": app.view_functions["drafts.manager"],
        "/growth-lens": app.view_functions["analytics.dashboard"],
        "/pick-perfect": app.view_functions["images.thumbnails"],
        "/nexus": app.view_functions["ai.chatbot"],
        "/persona": app.view_functions["profile.settings"],
    }
    for path, view in canonical_routes.items():
        endpoint = "brand_" + path.strip("/").replace("-", "_")
        if path not in {rule.rule for rule in app.url_map.iter_rules()}:
            app.add_url_rule(path, endpoint=endpoint, view_func=view, methods=["GET", "POST"] if path == "/persona" else ["GET"])

    legacy_to_brand = {
        "/": "/launchpad", "/dashboard": "/launchpad",
        "/ai/workspace": "/idea-flow", "/media/assets": "/media-bloom",
        "/video-editor": "/clip-nest", "/video-editor/": "/clip-nest",
        "/planner/calendar": "/day-canvas", "/drafts/manager": "/craft-nest",
        "/analytics/dashboard": "/growth-lens", "/images/thumbnails": "/pick-perfect",
        "/ai/chatbot": "/nexus", "/profile/settings": "/persona",
    }
    @app.before_request
    def redirect_legacy_module_urls():
        target = legacy_to_brand.get(request.path)
        if target and request.method in ("GET", "HEAD"):
            return redirect(target + (("?" + request.query_string.decode("utf-8")) if request.query_string else ""), code=302)

    # Inject global variables into Jinja context
    @app.context_processor
    def inject_globals():
        return {
            'app_name': app.config['APP_NAME'],
            'app_title': app.config['APP_TITLE'],
            'app_version': app.config['VERSION']
        }

    with app.app_context():
        db.create_all()
        # Lightweight schema migration for existing CreatorOS installations.
        # db.create_all() does not add new columns to an existing SQLite/MySQL table.
        from sqlalchemy import inspect, text
        user_columns = {c['name'] for c in inspect(db.engine).get_columns('users')}
        new_user_columns = {
            'date_of_birth': 'DATE', 'phone': 'VARCHAR(30)', 'gender': 'VARCHAR(30)',
            'location': 'VARCHAR(120)', 'bio': 'TEXT',
            'instagram': 'VARCHAR(120)', 'youtube': 'VARCHAR(120)', 'linkedin': 'VARCHAR(120)'
        }
        for column, sql_type in new_user_columns.items():
            if column not in user_columns:
                db.session.execute(text(f'ALTER TABLE users ADD COLUMN {column} {sql_type}'))
        planner_columns = {c['name'] for c in inspect(db.engine).get_columns('planner')}
        if 'calendar_uid' not in planner_columns:
            db.session.execute(text('ALTER TABLE planner ADD COLUMN calendar_uid VARCHAR(100)'))
        analytics_columns = {c['name'] for c in inspect(db.engine).get_columns('analytics')}
        if 'previous_productivity_score' not in analytics_columns:
            db.session.execute(text('ALTER TABLE analytics ADD COLUMN previous_productivity_score INTEGER DEFAULT 0'))
        db.session.commit()

    return app
