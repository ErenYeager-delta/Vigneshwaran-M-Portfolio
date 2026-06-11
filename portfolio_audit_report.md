# 🛡️ Portfolio Audit Report — Warning & Critical Issues

> Audited: `Vigneshwaran-M-Portfolio` (Flask + MongoDB + Render)
> Repo: [GitHub](https://github.com/ErenYeager-delta/Vigneshwaran-M-Portfolio)

---

## 🔴 CRITICAL — Immediate Action Required

### 1. Live Credentials in `.env` File (Local Disk)

> [!CAUTION]
> Your [.env](file:///c:/Users/1771v/Downloads/Vigneshwaran-M-Portfolio-main/Vigneshwaran-M-Portfolio-main/.env) file contains **real production secrets** in plaintext:

| Secret | Exposed Value |
|---|---|
| MongoDB Atlas URI | Full connection string with username `1972banumathi_db_user` and password `1972Banumathi` |
| EmailJS Service ID | `service_ospo2ec` |
| EmailJS Template ID | `template_fjq3l44` |
| EmailJS Public Key | `KF70fTzyyxd3aje3B` |
| EmailJS Private Key | `YrZyLnrk1rIxRc-xJYthz` |
| Flask SECRET_KEY | Full 64-char hex key |
| Admin Password Hash | Full scrypt hash |

**Status**: ✅ `.env` is in `.gitignore` and was **never committed** to Git history — so these are NOT exposed on GitHub. However, if this folder is ever zipped/shared, all secrets leak.

**Recommendation**:
- Rotate the MongoDB password immediately if this folder has been shared
- Rotate EmailJS keys on [emailjs.com dashboard](https://dashboard.emailjs.com)
- Generate a new `SECRET_KEY` and `ADMIN_PASSWORD`

---

### 2. Admin Secret Path Hardcoded in `robots.txt`

> [!CAUTION]
> [public.py:L116](file:///c:/Users/1771v/Downloads/Vigneshwaran-M-Portfolio-main/Vigneshwaran-M-Portfolio-main/app/routes/public.py#L116) explicitly advertises your hidden admin login URL:

```python
"Disallow: /vignesh-secret-2025\n"
```

Any attacker can read `/robots.txt` and discover the admin panel URL. The `Disallow` directive is a **signal to crawlers**, not a security measure — it actually reveals the path.

**Also exposed in**: [render.yaml:L22](file:///c:/Users/1771v/Downloads/Vigneshwaran-M-Portfolio-main/Vigneshwaran-M-Portfolio-main/render.yaml#L22) (committed to public GitHub)

```yaml
- key: ADMIN_SECRET_PATH
  value: /vignesh-secret-2025
```

**Fix**: Remove the `Disallow` line from `robots.txt`, and move `ADMIN_SECRET_PATH` to Render's secret environment variables (don't put the actual value in `render.yaml`).

---

### 3. Personal Email as Git Author

> [!WARNING]
> Your Git commits use a **personal email** (`1972banumathi@gmail.com`) as the author. This is visible on GitHub in your commit history.

**Fix**: Change your Git author to a professional email:
```bash
git config user.email "your-professional@email.com"
```

---

## 🟠 HIGH — Security Weaknesses

### 4. CORS Allows All Origins (`*`)

In [\_\_init\_\_.py:L34-L38](file:///c:/Users/1771v/Downloads/Vigneshwaran-M-Portfolio-main/Vigneshwaran-M-Portfolio-main/app/__init__.py#L34-L38):

```python
CORS(app, resources={
    r"/send-otp": {"origins": "*"},
    r"/verify-otp": {"origins": "*"},
    r"/ping": {"origins": "*"},
})
```

Setting `origins: "*"` means **any website** can call your OTP endpoints. An attacker could build a phishing site that sends OTPs through your EmailJS account.

**Fix**: Restrict to your actual domain:
```python
CORS(app, resources={
    r"/send-otp": {"origins": "https://vigneshwaranm.onrender.com"},
    r"/verify-otp": {"origins": "https://vigneshwaranm.onrender.com"},
    r"/ping": {"origins": "*"},  # ping is OK to be open
})
```

---

### 5. `/submit-brief` Endpoint Missing Rate Limiting

In [api.py:L88-L89](file:///c:/Users/1771v/Downloads/Vigneshwaran-M-Portfolio-main/Vigneshwaran-M-Portfolio-main/app/routes/api.py#L88-L89):

```python
@api_bp.route("/submit-brief", methods=["POST"])
def submit_brief():
```

Unlike `/send-otp` (3/min) and `/verify-otp` (5/min), this route has **no rate limiting**. An attacker can spam thousands of project briefs, flooding your MongoDB and EmailJS quota.

**Fix**: Add `@limiter.limit("3 per minute")` decorator.

---

### 6. `/submit-brief` Missing Input Sanitization

In [api.py:L93-L95](file:///c:/Users/1771v/Downloads/Vigneshwaran-M-Portfolio-main/Vigneshwaran-M-Portfolio-main/app/routes/api.py#L93-L95), `name`, `email`, and `message` are used raw without `sanitize_input()`:

```python
name = data.get("name")       # ← raw
email = data.get("email")     # ← raw, no email format validation
message = data.get("message") # ← raw, no length limit
```

This allows XSS payloads, excessively long inputs, and invalid emails to reach your database and EmailJS.

**Fix**: Apply `sanitize_input()` and email validation like you do in `verify_otp`.

---

### 7. OTP Store is In-Memory (Not Persistent)

In [services.py:L10](file:///c:/Users/1771v/Downloads/Vigneshwaran-M-Portfolio-main/Vigneshwaran-M-Portfolio-main/app/services.py#L10):

```python
_store = {}
```

The OTP store uses a class-level dictionary. If gunicorn runs with **multiple workers**, each worker has its own `_store` — the OTP generated in Worker A won't be found when the user verifies in Worker B.

**Impact**: OTP verification will randomly fail in production with `>1` worker.

**Fix**: Move OTP storage to MongoDB or Redis instead of in-process memory.

---

### 8. `send_brief_email` Unconditionally Uses Private Key (Crashes if None)

In [services.py:L99](file:///c:/Users/1771v/Downloads/Vigneshwaran-M-Portfolio-main/Vigneshwaran-M-Portfolio-main/app/services.py#L99):

```python
"accessToken": current_app.config["EMAILJS_PRIVATE_KEY"],
```

Unlike `send_otp_email` (which conditionally adds the key), `send_brief_email` always includes `EMAILJS_PRIVATE_KEY`. If the key is `None`, the API call may fail silently or throw.

**Fix**: Use the same conditional pattern as in `send_otp_email`.

---

## 🟡 MEDIUM — Code Quality & Robustness

### 9. Bare `except` Blocks Swallow Errors

In [\_\_init\_\_.py:L89](file:///c:/Users/1771v/Downloads/Vigneshwaran-M-Portfolio-main/Vigneshwaran-M-Portfolio-main/app/__init__.py#L89) and [L93](file:///c:/Users/1771v/Downloads/Vigneshwaran-M-Portfolio-main/Vigneshwaran-M-Portfolio-main/app/__init__.py#L93):

```python
except:
    return value  # Return as is if parsing fails
```

Bare `except:` catches SystemExit, KeyboardInterrupt, etc. Use `except (ValueError, TypeError):` instead.

---

### 10. GitHub Actions Keep-Alive Fires Every 14 Minutes

In [keep-alive.yml:L5](file:///c:/Users/1771v/Downloads/Vigneshwaran-M-Portfolio-main/Vigneshwaran-M-Portfolio-main/.github/workflows/keep-alive.yml#L5):

```yaml
- cron: '*/14 * * * *'
```

This fires **~103 times/day** (~3,086 times/month). GitHub Actions free tier allows 2,000 minutes/month. Each run consumes at least 1 minute of runner time, so this will **exceed your free quota** and potentially get throttled.

**Fix**: Change to `*/30` (every 30 min) or use an external service like UptimeRobot (free, no GitHub minutes cost).

---

### 11. `ProjectBrief` and `VerifiedUser` Share the Same Collection

In [models.py:L216-L218](file:///c:/Users/1771v/Downloads/Vigneshwaran-M-Portfolio-main/Vigneshwaran-M-Portfolio-main/app/models.py#L216-L218):

```python
class ProjectBrief(MongoModel):
    database_name = "otpDB"
    collection_name = "verified_users"  # ← Same as VerifiedUser!
```

Both `ProjectBrief` and `VerifiedUser` write to the **same** `verified_users` collection. Project briefs include a `"type": "direct_message"` field to differentiate, but this is fragile and can cause data confusion.

**Fix**: Use a separate collection like `project_briefs`.

---

### 12. No IDOR Protection on Download Routes

All download routes in [downloads.py](file:///c:/Users/1771v/Downloads/Vigneshwaran-M-Portfolio-main/Vigneshwaran-M-Portfolio-main/app/routes/downloads.py) accept raw MongoDB ObjectIds with **no authentication**:

```
/certificate/<cert_id>/download
/experience/appointment-letter/<letter_id>/preview
/experience/pay-slip/<slip_id>/preview
```

Anyone who guesses or brute-forces a valid ObjectId can download **appointment letters, pay slips, incentive documents, and offer letters** — sensitive personal documents.

**Fix**: Add authentication checks (e.g., OTP-verified session) for sensitive document routes, or at minimum validate that the document's `is_active` flag is `True`.

---

### 13. Admin Login Allows Plaintext Password in Development

In [auth.py:L36-L40](file:///c:/Users/1771v/Downloads/Vigneshwaran-M-Portfolio-main/Vigneshwaran-M-Portfolio-main/app/admin/auth.py#L36-L40):

```python
if admin_pass.startswith(("pbkdf2:", "scrypt:")):
    is_valid = check_password_hash(admin_pass, password)
else:
    is_valid = (password == admin_pass)
```

While production enforces hashed passwords, in `debug=True` mode, a plaintext password comparison is allowed. If someone accidentally runs with `FLASK_ENV=development` on a public server, the admin password could be a weak plaintext string.

---

### 14. `print()` Statements in Production Code

Throughout [api.py](file:///c:/Users/1771v/Downloads/Vigneshwaran-M-Portfolio-main/Vigneshwaran-M-Portfolio-main/app/routes/api.py) (lines 39, 45, 49, 84, 116):

```python
print(f"✅ OTP sent to {email} successfully.")
print(f"❌ EmailJS Error: {error_detail}")
```

These leak emails and error details to stdout/server logs. Use `current_app.logger` instead, and avoid logging PII.

---

## 🔵 LOW — Best Practices

### 15. `__pycache__` Directory Present in Working Copy
The `__pycache__/` directories exist locally. While they're `.gitignore`d, consider running `find . -name __pycache__ -exec rm -rf {} +` to clean them.

### 16. `Procfile` and `render.yaml` Serve the Same Purpose
Both define how to start the app. Render uses `render.yaml`; Procfile is for Heroku. If you're only deploying to Render, the `Procfile` is unnecessary (though harmless).

### 17. No `requirements.txt` Version Pinning
All dependencies use `>=` minimum versions with no upper bounds. A future breaking change in Flask, pymongo, etc. could silently break your build. Consider using `pip freeze > requirements.txt` for exact pinning.

---

## Summary

| Severity | Count | Key Issues |
|---|---|---|
| 🔴 Critical | 3 | Credentials in .env, admin path in robots.txt, personal email in Git |
| 🟠 High | 5 | CORS wildcard, missing rate limiting, OTP in-memory, unsanitized input, EmailJS key crash |
| 🟡 Medium | 6 | Bare except, GitHub Actions quota, shared collection, IDOR on downloads, plaintext admin, print statements |
| 🔵 Low | 3 | Pycache cleanup, duplicate Procfile, unpinned deps |

