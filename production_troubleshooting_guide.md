# 🛠️ Step-by-Step Production Troubleshooting Guide (Series-Wise)

This guide documents the problems faced during the development and deployment of the Vigneshwaran M Portfolio application, organized in the exact chronological order (series-wise) in which they occurred.

---

## 📅 Step 1: Uploaded Files Vanishing on Redeployment (Ephemeral Disk Loss)

### 🔴 The Problem
Initially, uploaded files (resumes, certificates, projects, and employment documents) were saved locally to the container's disk inside `app/static/uploads/`.
* On platforms like **Render.com**, web applications run in ephemeral Docker containers.
* Every time a new commit is pushed, or the container restarts, the old container is completely destroyed and rebuilt.
* This caused **all uploaded files on the local disk to be deleted permanently**, rendering the admin panel upload features useless.

### ✅ The Resolution
1. **MongoDB GridFS Integration**: We migrated the primary storage engine to **MongoDB GridFS** (`app/storage.py`), which stores files as binary chunks directly in your Atlas database.
2. **Serving and Fallback Logic**: We updated the serving endpoint in `app/__init__.py` to first retrieve files dynamically from GridFS. If they are not found in GridFS, it falls back to checking the local disk.
3. **Disk Saves Made Optional**: Local disk operations are now treated as non-blocking backup mechanisms; if writing to the ephemeral disk fails, the app logs a warning but successfully completes the GridFS database save.

---

## 📅 Step 2: Downloads Endpoint Crashed in Production (Missing Imports)

### 🔴 The Problem
Once files were uploaded to GridFS, visiting the download or preview links (e.g. `/experience/pay-slip/<id>/preview` or `/experience/appointment-letter/<id>/preview`) resulted in a server error (500).
* Looking at the server logs, Python threw a `NameError` inside `app/routes/downloads.py`.
* The handler functions referenced data models like `Resume`, `Certificate`, `AppointmentLetter`, `Incentive`, `OfferLetter`, and `PaySlip` to query database metadata, but **none of these models were imported** at the top of `app/routes/downloads.py`.

### ✅ The Resolution
We imported all necessary model classes at the top of `app/routes/downloads.py`:
```python
from app.models import Resume, Certificate, AppointmentLetter, Incentive, OfferLetter, PaySlip
```
This restored full functionality to the professional document vault preview and download endpoints.

---

## 📅 Step 3: Admin Logouts and IP Shifts (Reverse Proxy Routing)

### 🔴 The Problem
After logging into the admin dashboard on Render, administrators were constantly and randomly logged out and redirected to the home screen.
* The security decorator `@admin_required` implemented strict "Session Binding" by comparing the administrator's IP address (`request.remote_addr`) on every page load against the IP stored at login.
* Because Render hosts route traffic through dynamic load balancers and reverse proxies, the apparent client IP address shifts frequently between page clicks.
* The mismatch between the logged IP and the rotated proxy IP caused the decorator to terminate the session instantly.

### ✅ The Resolution
1. **WSGI Proxy Tracking**: Added Werkzeug's `ProxyFix` middleware to `app/__init__.py` to trust headers set by the Render reverse proxies.
2. **Bypass Environment Variable**: Introduced the `DISABLE_IP_BINDING` configuration inside `app/security.py`. Setting `DISABLE_IP_BINDING=true` in Render skips checking the fluctuating IP but retains the secure browser **User-Agent** binding, preventing session hijacking without breaking the usability.

---

## 📅 Step 4: Certificate Uploads Generating Null Filenames in Database

### 🔴 The Problem
When uploading certificate credentials, PDF documents would successfully upload but would render as broken links on the dashboard.
* The logic inside `app/admin/certificate.py` checked the extension. If it was a PDF, the path skipped or failed to generate the `safe_name` UUID parameter correctly.
* This caused a null/empty filename to be written to MongoDB GridFS and the database certificate collection.

### ✅ The Resolution
We refactored `add_certificate()` in `app/admin/certificate.py` to always generate the `safe_name` parameter at the top of the route using `validate_upload(cert_file)` regardless of the extension type (PDF or image). This ensured filename consistency in GridFS and the database.

---

## 📅 Step 5: Code Connections Obscurity & requirements.txt Comments

### 🔴 The Problem
The codebase was difficult for developers to review, follow, and maintain because the mapping of routes, files, templates, and libraries was documented only in an external `code_connections_report.md` file rather than inline. Additionally, `requirements.txt` was a list of packages without any explanation of why they were installed.

### ✅ The Resolution
1. **Inline Docstrings**: We deleted the external report file and placed detailed descriptive docstrings at the top of every `.py` file outlining its **Purpose**, **Logic**, and **Connections**.
2. **Documented requirements.txt**: Added comments above every dependency package (such as Flask-WTF, Flask-Limiter, Pillow, Bleach) explaining exactly why it is required and where it is imported.

---

## 📅 Step 6: Form Rejections / "CSRF Token Missing" (Multi-Worker Mismatch)

### 🔴 The Problem
When administrators attempted to upload multiple incentive photos or submit other admin forms, the page would reload showing a **"CSRF token missing or incorrect"** error.
* On Render, Gunicorn boots up multiple worker processes.
* Because the `SECRET_KEY` environment variable was left empty on Render's dashboard, `app/config.py` generated fallback keys dynamically using `os.urandom(32).hex()`.
* Every worker process generated a different random secret key. 
* If Worker A rendered the page (delivering a CSRF token signed with Key A) and the subsequent POST request landed on Worker B (expecting Key B), Worker B failed the CSRF verification, blocking the request.

### ✅ The Resolution
We documented that the administrator must define a static `SECRET_KEY` env var in the Render Web Dashboard (e.g. `SECRET_KEY=some_static_random_hash`). When set, Gunicorn workers share the same key, and CSRF tokens validate correctly across all processes.
