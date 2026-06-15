"""
🔐 Admin Authentication Controller
Purpose:
  Manages administrative login and logout flows, including secure password hashing verification,
  brute-force defense audits (IP tracking + global thresholds), session creation (IP + User-Agent binding),
  clearing page caches on authentication state change, and launching security alert emails.
Connections:
  - app/__init__.py: Mapped dynamically using configuration-defined secret endpoint paths.
  - app/security.py: Relies on `check_brute_force`, `check_global_brute_force`, and `record_login_attempt` middleware.
  - app/services.py: Employs `EmailService` to dispatch real-time warning alerts to the administrator's mailbox.
  - app/templates/admin/login.html: Renders the credentials form.
"""
from flask import request, session, redirect, url_for, render_template, current_app
from werkzeug.security import check_password_hash
from flask_wtf.csrf import generate_csrf
from app.extensions import limiter, cache
from app.security import admin_required, check_brute_force, check_global_brute_force, record_login_attempt
from app.services import EmailService
from app.admin import admin_bp


# Connection: Registered dynamically on application load in app/__init__.py (L60) under the configured ADMIN_SECRET_PATH.
# Purpose: Authenticates admin credentials sent from login.html (L22) against ADMIN_PASSWORD, clearing cache on login.
@limiter.limit("5 per minute")
def admin_login():
    """Secret admin login handler — mapped dynamically on application factory load."""
    generate_csrf() # Force CSRF token into session
    error = None

    client_ip = request.remote_addr
    user_agent = request.user_agent.string

    # Brute-force checks (individual IP and distributed locks)
    if check_brute_force(client_ip) or check_global_brute_force():
        error = "Suspicious activity detected. Access temporarily locked."
        EmailService.send_security_alert(client_ip, "BLOCKED (BRUTE-FORCE LOCKOUT)", user_agent)
        return render_template("admin/login.html", error=error), 429

    if request.method == "POST":
        password = request.form.get("password", "")
        admin_pass = current_app.config["ADMIN_PASSWORD"]

        # Enforce password hash in production
        if not current_app.debug and not admin_pass.startswith(("pbkdf2:", "scrypt:")):
            error = "Enforcement failure: Plaintext passwords are prohibited in production."
            EmailService.send_security_alert(client_ip, "PROHIBITED PLAINTEXT PASSWORD CONFIGURATION WARNING", user_agent)
            return render_template("admin/login.html", error=error), 500

        # Compare password (supports both plain and hashed)
        is_valid = False
        if admin_pass.startswith(("pbkdf2:", "scrypt:")):
            is_valid = check_password_hash(admin_pass, password)
        else:
            is_valid = (password == admin_pass)

        if is_valid:
            record_login_attempt(client_ip, success=True)
            session["admin_authenticated"] = True
            session["admin_ip"] = client_ip
            session["admin_user_agent"] = user_agent
            session.permanent = True
            cache.clear()  # Clear cached pages so new content shows immediately
            
            # Send login notification email
            EmailService.send_security_alert(client_ip, "SUCCESSFUL LOGIN", user_agent)
            
            return redirect(url_for("admin.dashboard"))
        else:
            record_login_attempt(client_ip, success=False)
            error = "Invalid password."
            # Send warning alert
            EmailService.send_security_alert(client_ip, "FAILED LOGIN ATTEMPT", user_agent)

    return render_template("admin/login.html", error=error)


@admin_bp.route("/admin/logout", methods=["POST"])
@admin_required
def admin_logout():
    """Clear admin session."""
    session.clear() # Clears bound IP and User-Agent completely
    return redirect("/")
