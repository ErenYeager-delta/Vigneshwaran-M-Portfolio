"""
🛡️ Security middleware & helpers.
Centralizes all anti-hacking defenses in one module.
"""

import os
import uuid
import bleach
from datetime import datetime, timezone, timedelta
from functools import wraps
from flask import request, session, redirect, url_for, abort, current_app
from werkzeug.utils import secure_filename


# ─── Security Headers Middleware ────────────────────────────────────────────

def init_security_headers(app):
    """Register an after_request hook that injects hardened HTTP headers."""

    @app.after_request
    def set_security_headers(response):
        # Prevent MIME-type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # XSS filter (legacy browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Content Security Policy — whitelist only trusted CDNs
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com; "
            "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
            "img-src 'self' data: blob: https: https://www.transparenttextures.com; "
            "connect-src 'self' https://api.emailjs.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "worker-src 'self' blob:; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp

        # HSTS in production
        if not current_app.debug:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

        # Remove server identity header
        response.headers.pop("Server", None)

        return response


# ─── Admin Session Protection ───────────────────────────────────────────────

def admin_required(f):
    """
    Decorator: redirects to home if not authenticated as admin.
    Performs Session Binding validation (IP + User-Agent) to block session hijacking.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_authenticated"):
            return redirect("/")
        
        # Session Binding check (revokes session instantly on change)
        bound_ip = session.get("admin_ip")
        bound_ua = session.get("admin_user_agent")
        
        if bound_ip != request.remote_addr or bound_ua != request.user_agent.string:
            session.clear()
            return redirect("/")
            
        return f(*args, **kwargs)
    return decorated


# ─── Brute-Force Protection ─────────────────────────────────────────────────

def check_brute_force(ip_address, max_attempts=5, lockout_minutes=15):
    """
    Returns True if the IP is currently locked out.
    Checks recent failed attempts within the lockout window.
    """
    from app.models import AdminLoginAttempt
    
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=lockout_minutes)
    col = AdminLoginAttempt.get_collection()
    if col is None: return False

    recent_failures = col.count_documents({
        "ip_address": ip_address,
        "success": False,
        "attempted_at": {"$gte": cutoff}
    })

    return recent_failures >= max_attempts


def check_global_brute_force(max_attempts=15, lockout_minutes=10):
    """
    Returns True if there is a distributed brute-force attack (many failed attempts across all IPs).
    """
    from app.models import AdminLoginAttempt
    
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=lockout_minutes)
    col = AdminLoginAttempt.get_collection()
    if col is None: return False

    recent_failures = col.count_documents({
        "success": False,
        "attempted_at": {"$gte": cutoff}
    })

    return recent_failures >= max_attempts


def record_login_attempt(ip_address, success):
    """Record a login attempt in the database."""
    from app.models import AdminLoginAttempt
    AdminLoginAttempt.record(ip_address, success)


# ─── File Upload Validation ─────────────────────────────────────────────────

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/webp",
    "image/gif",
}

def validate_upload(file_storage, allowed_extensions=None):
    """
    Validates an uploaded file:
    1. Checks that a file was actually provided
    2. Validates file extension against whitelist
    3. Validates MIME type
    4. Generates a UUID-based safe filename

    Returns: (is_valid: bool, safe_filename: str | None, error: str | None)
    """
    if not file_storage or file_storage.filename == "":
        return False, None, "No file selected."

    original = file_storage.filename
    ext = original.rsplit(".", 1)[-1].lower() if "." in original else ""

    if allowed_extensions is None:
        allowed_extensions = current_app.config.get(
            "ALLOWED_EXTENSIONS", {"pdf", "png", "jpg", "jpeg", "webp"}
        )

    if ext not in allowed_extensions:
        return False, None, f"File type '.{ext}' not allowed. Use: {', '.join(allowed_extensions)}"

    # MIME type check
    content_type = file_storage.content_type or ""
    if content_type not in ALLOWED_MIME_TYPES:
        return False, None, f"Invalid file content type: {content_type}"

    # Generate UUID filename to prevent path traversal
    safe_name = f"{uuid.uuid4().hex}.{ext}"

    return True, safe_name, None


# ─── Input Sanitization ─────────────────────────────────────────────────────

def sanitize_input(text, max_length=500):
    """
    Strips HTML tags and limits length.
    Uses bleach for robust sanitization.
    """
    if not text:
        return ""
    cleaned = bleach.clean(str(text), tags=[], strip=True)
    return cleaned[:max_length].strip()


def sanitize_url(url, max_length=500):
    """Validates and sanitizes a URL."""
    if not url:
        return "#"
    url = str(url).strip()[:max_length]
    # Only allow http, https, and relative URLs
    if url.startswith(("http://", "https://", "/")):
        return bleach.clean(url, tags=[], strip=True)
    return "#"
