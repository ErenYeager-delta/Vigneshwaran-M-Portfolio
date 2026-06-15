# 🛠️ Production Hosting & Troubleshooting Guide

This guide details the technical challenges, hosting issues, and production bugs identified in this application, along with how they were resolved to make the portfolio robust, secure, and production-ready on cloud environments like **Render.com**.

---

## 🔒 1. CSRF Token Mismatches (Gunicorn Multi-Worker Config)

### 🔴 The Problem
When the application is deployed on cloud servers (like Render), it uses **Gunicorn** to run multiple concurrent processes (workers) to handle requests.
* If the `SECRET_KEY` environment variable is not defined, `app/config.py` generates a fallback key dynamically using `os.urandom(32).hex()`.
* Because each worker process boots up separately, **every worker generates a different random secret key**.
* If a visitor loads the page on Worker A (getting a CSRF token signed by Key A) and submits a form (e.g. uploading an incentive, certification, or project), the request might land on Worker B.
* Since Worker B uses Key B, it cannot decrypt the session cookie or validate the CSRF token. This causes Flask-WTF to continuously reject submissions with a **"CSRF token missing or incorrect"** error.

### ✅ The Fix
1. Make sure to **never** rely on random fallback keys in production.
2. In the Render Dashboard (or your cloud host), define a static environment variable:
   * **Key**: `SECRET_KEY`
   * **Value**: A long secure random string (e.g. `7f8a9b2c3d4e5f6a7b8c9d0e1f2a3b4c`).
3. This guarantees that all running Gunicorn processes share the same key to sign and validate CSRF tokens and session cookies.

---

## 🌐 2. Admin Session Terminations (Reverse Proxy IP Shifts)

### 🔴 The Problem
The `@admin_required` decorator checks that the visitor's IP address and User-Agent match the values stored when they successfully logged in (Session Binding).
* In production environments, client requests pass through a load balancer or reverse proxy.
* As load balancers shift traffic or route requests across networks, the perceived IP address of the admin (`request.remote_addr`) fluctuates.
* The moment the proxy rotates and the remote address shifts, `@admin_required` detects an IP mismatch, automatically clears the session, and redirects the administrator to the homepage.

### ✅ The Fix
1. Added proxy compatibility to the application WSGI server in `app/__init__.py` using Werkzeug's `ProxyFix` middleware to trust standard forward headers (`X-Forwarded-For`, `X-Forwarded-Proto`, etc.).
2. Integrated a toggle variable `DISABLE_IP_BINDING` in `app/security.py` that checks the environment:
   * **Variable**: `DISABLE_IP_BINDING=true`
   * If enabled, the security middleware bypasses the fluctuating IP binding check but retains the **User-Agent** signature verification to prevent session hijacking without breaking usability behind proxies.

---

## 📦 3. Data Loss on Ephemeral Cloud Containers (GridFS Migration)

### 🔴 The Problem
Cloud hosts like Render use ephemeral filesystems. Every time the application redeploys or restarts, the container is destroyed and recreated from the Git repository.
* Any uploaded files (resumes, project images, certificates, appointment letters, pay slips, incentives) saved solely to the local `app/static/uploads/` directory are **permanently wiped out**.

### ✅ The Fix
1. Configured MongoDB GridFS (`app/storage.py`) as the primary file storage system.
2. All file uploads are saved as binary chunks directly inside the Atlas MongoDB database.
3. The serve endpoint in `app/__init__.py` first checks MongoDB GridFS to serve the file binaries dynamically. If not present in GridFS, it falls back to checking the local disk.
4. Saving to the local disk is kept strictly as a fallback backup; if the disk write fails due to read-only container nodes, it logs a warning but continues executing normally.

---

## 💥 4. Downloads Blueprint Imports Crash

### 🔴 The Problem
In [app/routes/downloads.py](file:///d:/Projects/Vigneshwaran-M-Portfolio-main/Vigneshwaran-M-Portfolio-main/app/routes/downloads.py), download and preview endpoints were invoked by visitors to retrieve assets (such as pay slips, resumes, or appointment letters).
* However, the python models mapping these files (`Resume`, `Certificate`, `AppointmentLetter`, `Incentive`, `OfferLetter`, `PaySlip`) were not imported inside the file.
* This caused any download request to throw a `NameError` in Python, crashing the endpoint in production.

### ✅ The Fix
1. Imported all necessary database models into `app/routes/downloads.py`.
2. Verified that all download schemas and methods are correctly accessible.

---

## 🎨 5. Certificate Upload Null Filenames

### 🔴 The Problem
In [app/admin/certificate.py](file:///d:/Projects/Vigneshwaran-M-Portfolio-main/Vigneshwaran-M-Portfolio-main/app/admin/certificate.py), uploading non-image formats (like PDF certificate credentials) caused issues where the `safe_name` was skipped or not generated correctly depending on the path taken, resulting in database entries missing filenames or showing null pointers.

### ✅ The Fix
1. Refactored the `add_certificate` route to always generate `safe_name` via `validate_upload(cert_file)` regardless of whether the file extension is a PDF or an image, maintaining naming integrity across GridFS and MongoDB.
