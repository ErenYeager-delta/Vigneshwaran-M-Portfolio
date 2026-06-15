"""
⚙️ Flask Application Factory & Initialization
Purpose:
  Initializes and configures the Flask application, loads environment variables,
  registers global blueprints, sets up WSGI ProxyFix middleware for production (Render/HTTPS),
  configures cross-origin requests (CORS), error handlers, and server-side Jinja templates.
Connections:
  - run.py: Imports and invokes create_app() to run the web server.
  - app/config.py: Supplies BaseConfig/ProdConfig/DevConfig mapping environments.
  - app/extensions.py: Instantiates rate limiting, cache, and CSRF protection.
  - app/security.py: Hook for setting secure HTTP response headers and path validation.
  - app/routes/* & app/admin/*: Registers public, API, downloads, and admin blueprints.
"""

import os
from flask import Flask
from flask_cors import CORS

from app.config import config_map
from app.extensions import cache, csrf, limiter
from app.security import init_security_headers


def create_app(config_name=None):
    """Create and configure the Flask application."""

    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(
        __name__,
        instance_relative_config=True,
        static_folder="static",
        template_folder="templates",
    )

    # ── Proxy Configuration for Render / HTTPS ───────────────────────────
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    # ── Load Config ──────────────────────────────────────────────────────
    app.config.from_object(config_map.get(config_name, config_map["default"]))

    # ── Initialize Extensions ────────────────────────────────────────────
    cache.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    CORS(app, resources={
        r"/send-otp": {"origins": "*"},
        r"/verify-otp": {"origins": "*"},
        r"/ping": {"origins": "*"},
    })

    # ── Security Headers ─────────────────────────────────────────────────
    init_security_headers(app)

    # ── Exempt API routes from CSRF (they use JSON, not forms) ───────────
    from app.routes.api import api_bp
    csrf.exempt(api_bp)

    # ── Register Blueprints ──────────────────────────────────────────────
    from app.routes.public import public_bp
    from app.admin import admin_bp
    from app.routes.downloads import downloads_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(downloads_bp)

    # Register dynamic secret admin login path (obscured defense)
    from app.admin.auth import admin_login
    secret_path = app.config.get("ADMIN_SECRET_PATH", "/vignesh-secret-2025")
    app.add_url_rule(
        secret_path,
        "admin.admin_login",
        admin_login,
        methods=["GET", "POST"]
    )

    # ── Serve Uploaded Files from GridFS with local fallback ────────────────
    @app.route("/static/uploads/<string:folder>/<string:filename>")
    def serve_uploaded_file(folder, filename):
        from flask import abort, send_from_directory
        from app.routes.downloads import serve_gridfs_file_response
        
        # 1. Try serving from GridFS
        response = serve_gridfs_file_response(filename, as_attachment=False)
        if response:
            return response
            
        # 2. Fallback to local disk if exists
        upload_base = app.config["UPLOAD_FOLDER"]
        file_path = os.path.join(upload_base, folder, filename)
        if os.path.exists(file_path):
            return send_from_directory(os.path.join(upload_base, folder), filename)
            
        abort(404)

    # ── Create Upload Directories ────────────────────────────────────────
    upload_base = app.config["UPLOAD_FOLDER"]
    for subdir in ("resumes", "certificates", "projects", "appointment_letters", "incentives", "offer_letters", "pay_slips"):
        path = os.path.join(upload_base, subdir)
        os.makedirs(path, exist_ok=True)

    # ── Ensure instance folder exists ────────────────────────────────────
    os.makedirs(app.instance_path, exist_ok=True)



    # ── Custom Jinja Filters ─────────────────────────────────────────────
    @app.template_filter('safe_date')
    def safe_date(value, format='%b %d, %Y'):
        if not value:
            return "N/A"
        if isinstance(value, str):
            try:
                # Try parsing standard SQLite/ISO format
                from datetime import datetime
                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                return dt.strftime(format)
            except:
                return value # Return as is if parsing fails
        try:
            return value.strftime(format)
        except:
            return str(value)

    # ── Custom Error Pages (no stack traces leaked) ──────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return {"error": "Not found"}, 404

    @app.errorhandler(500)
    def internal_error(e):
        return {"error": "Internal server error"}, 500

    @app.errorhandler(429)
    def rate_limited(e):
        return {"error": "Too many requests. Please slow down."}, 429

    return app
