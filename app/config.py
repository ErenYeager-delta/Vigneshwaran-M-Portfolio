import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    """Base configuration — shared across all environments."""

    # --- Core Flask ---
    SECRET_KEY = os.getenv("SECRET_KEY", os.urandom(32).hex())
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)

    # --- Security: Session Cookies ---
    SESSION_COOKIE_HTTPONLY = True    # JS cannot access session cookie
    SESSION_COOKIE_SAMESITE = "Lax"  # Prevents CSRF via cross-site requests
    SESSION_COOKIE_NAME = "__vp_sess"  # Non-default name hides framework identity

    # --- Security: File Uploads ---
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    UPLOAD_FOLDER = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "static", "uploads"
    )
    ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "webp"}

    # --- Caching ---
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300

    # --- Admin ---
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
    ADMIN_SECRET_PATH = os.getenv("ADMIN_SECRET_PATH", "/vignesh-secret-2025")

    # --- EmailJS (preserved from original) ---
    EMAILJS_SERVICE_ID = os.getenv("EMAILJS_SERVICE_ID")
    EMAILJS_TEMPLATE_ID = os.getenv("EMAILJS_TEMPLATE_ID")
    EMAILJS_PUBLIC_KEY = os.getenv("EMAILJS_PUBLIC_KEY")
    EMAILJS_PRIVATE_KEY = os.getenv("EMAILJS_PRIVATE_KEY")

    # --- MongoDB (preserved from original) ---
    MONGO_URI = os.getenv("MONGO_URI")

    # --- Rate Limiting ---
    RATELIMIT_DEFAULT = "200/hour"
    RATELIMIT_STORAGE_URI = "memory://"


class DevConfig(BaseConfig):
    """Development configuration."""
    DEBUG = True
    SESSION_COOKIE_SECURE = False  # Allow HTTP in dev


class ProdConfig(BaseConfig):
    """Production configuration — hardened."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True   # HTTPS only
    PREFERRED_URL_SCHEME = "https"


config_map = {
    "development": DevConfig,
    "production": ProdConfig,
    "default": DevConfig,
}
