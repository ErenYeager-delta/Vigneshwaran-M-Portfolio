"""
⚙️ Configuration Management Module
Purpose:
  Declares the application's configuration classes, loading key secrets and environment settings
  (such as admin password, paths, rate limit rules, EmailJS tokens, and MongoDB Atlas URIs)
  from the environment via python-dotenv. Establishes session cookie attributes (Secure, HttpOnly, SameSite) for production.
Connections:
  - app/__init__.py: Imports config_map to initialize the Flask application factory.
  - run.py: Loads configurations through environment initialization.
"""
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
    # Connection: Verified against bcrypt hashes during admin authentication requests.
    # Key Source: Configured in the local .env file or host environment variables.
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
    
    # Connection: Injected dynamically in app/__init__.py (L60) to register the admin login route rule.
    # Key Source: Configured in the local .env file to obscure the admin path from scanners.
    ADMIN_SECRET_PATH = os.getenv("ADMIN_SECRET_PATH", "/vignesh-secret-2025")

    # --- EmailJS (preserved from original) ---
    # Connection: Used in app/services.py (EmailService) to dispatch verification OTP and brief notifications.
    # Key Source: Retrieve from EmailJS Dashboard -> Email Services -> Service ID.
    EMAILJS_SERVICE_ID = os.getenv("EMAILJS_SERVICE_ID")
    
    # Connection: Used in app/services.py (EmailService) to set email templates for notifications.
    # Key Source: Retrieve from EmailJS Dashboard -> Email Templates -> Template ID.
    EMAILJS_TEMPLATE_ID = os.getenv("EMAILJS_TEMPLATE_ID")
    
    # Connection: Used in app/services.py (EmailService) to authorize basic public requests.
    # Key Source: Retrieve from EmailJS Dashboard -> Account -> API Keys -> Public Key.
    EMAILJS_PUBLIC_KEY = os.getenv("EMAILJS_PUBLIC_KEY")
    
    # Connection: Used in app/services.py (EmailService) to authorize server-to-server email dispatches.
    # Key Source: Retrieve from EmailJS Dashboard -> Account -> API Keys -> Private Key.
    EMAILJS_PRIVATE_KEY = os.getenv("EMAILJS_PRIVATE_KEY")

    # --- MongoDB (preserved from original) ---
    # Connection: Used across app/models.py to connect to PyMongo collections (Projects, CertifiedUser, Resumes, etc.).
    # Key Source: Retrieve from MongoDB Atlas console -> Connect -> Drivers -> Connection String.
    MONGO_URI = os.getenv("MONGO_URI")

    # --- Rate Limiting ---
    # Connection: Used by Flask-Limiter in app/__init__.py and app/routes/api.py routes.
    # Key Source: Hardcoded defaults, storage fallback to in-memory store.
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
