import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

class Config:
    """CreatorOS Application Configuration."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "creatoros_super_secret_key_2026_bca")
    
    # Database Configuration (MySQL support with SQLite fallback)
    MYSQL_USER = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_DB = os.environ.get("MYSQL_DB", "creatoros_db")
    
    # Defaults to SQLite if MySQL is not configured/available locally
    USE_MYSQL = os.environ.get("USE_MYSQL", "false").lower() == "true"
    
    if USE_MYSQL:
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"
    else:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR / 'database' / 'creatoros.db'}"
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload settings - 100 MB Limit as specified in requirements
    UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'pdf', 'docx', 'txt', 'csv'}

    # Application branding
    APP_NAME = "CreatorOS"
    APP_TITLE = "CreatorOS – AI Workspace for Content Creators"
    VERSION = "1.0.0"

