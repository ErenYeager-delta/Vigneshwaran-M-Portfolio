"""
🎓 Certificate Administration Controller
Purpose:
  Provides CRUD operations for certification entities, supporting file uploads (PDF & images),
  automated GridFS migration, local filesystem backups, tag parsing, and visibility toggling.
Connections:
  - app/models.py: Interfaces with `Certificate` class schema logic for database operations.
  - app/security.py: Invokes `@admin_required`, `validate_upload`, `sanitize_input`, `sanitize_url`, and `get_safe_upload_path`.
  - app/storage.py: Utilizes `save_file` and `delete_file` helper methods for GridFS management.
  - app/templates/admin/dashboard.html: Renders lists of certifications and provides operational forms.
"""
import os
from flask import request, redirect, url_for, flash, current_app
from app.extensions import limiter, cache
from app.models import Certificate
from app.security import admin_required, validate_upload, sanitize_input, sanitize_url, get_safe_upload_path
from app.admin import admin_bp


@admin_bp.route("/admin/add-certificate", methods=["POST"])
@admin_required
@limiter.limit("10 per hour")
def add_certificate():
    """Add a new certification entry."""
    title = sanitize_input(request.form.get("title", ""), 200)
    issuer = sanitize_input(request.form.get("issuer", ""), 200)
    date_issued = sanitize_input(request.form.get("date_issued", ""), 50)
    description = sanitize_input(request.form.get("description", ""), 1000)
    link = sanitize_url(request.form.get("link", "#"))
    tags_raw = sanitize_input(request.form.get("tags", ""), 500)
    preview_image_url = sanitize_url(request.form.get("preview_image_url", ""))
    if preview_image_url == "#":
        preview_image_url = ""

    if not title or not issuer:
        flash("❌ Title and Issuer are required.", "error")
        return redirect(url_for("admin.dashboard"))

    # Parse tags (comma-separated)
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()]

    # Handle optional file upload
    safe_name = None
    preview_image = None
    cert_file = request.files.get("cert_file")
    if cert_file and cert_file.filename:
        is_valid, safe_name, error = validate_upload(cert_file)
        if not is_valid:
            flash(f"❌ {error}", "error")
            return redirect(url_for("admin.dashboard"))

        # Save file data to GridFS & disk
        from app.storage import save_file
        cert_data = cert_file.read()
        save_file(cert_data, safe_name, content_type=cert_file.content_type)

        ext = safe_name.rsplit(".", 1)[-1].lower()
        if ext == 'pdf':
            # PDF requires either a companion image file or a preview URL
            cert_image_file = request.files.get("cert_image_file")
            has_image_file = cert_image_file and cert_image_file.filename
            has_image_url  = bool(preview_image_url)

            if not has_image_file and not has_image_url:
                flash("❌ A PDF certificate needs a display image. Upload one or paste an Image URL.", "error")
                return redirect(url_for("admin.dashboard"))

            try:
                upload_path = get_safe_upload_path("certificates", safe_name)
                with open(upload_path, "wb") as f:
                    f.write(cert_data)
            except Exception as e:
                print(f"Local backup PDF save skipped: {e}")

            if has_image_file:
                # Validate and save companion image
                is_valid_img, safe_img_name, error_img = validate_upload(cert_image_file)
                if not is_valid_img:
                    flash(f"❌ Certificate Picture: {error_img}", "error")
                    return redirect(url_for("admin.dashboard"))

                img_ext = safe_img_name.rsplit(".", 1)[-1].lower()
                if img_ext not in {'png', 'jpg', 'jpeg', 'webp'}:
                    flash("❌ The picture must be an image format (PNG, JPG, JPEG, WEBP).", "error")
                    return redirect(url_for("admin.dashboard"))

                img_data = cert_image_file.read()
                save_file(img_data, safe_img_name, content_type=cert_image_file.content_type)
                try:
                    upload_img_path = get_safe_upload_path("certificates", safe_img_name)
                    with open(upload_img_path, "wb") as f:
                        f.write(img_data)
                except Exception as e:
                    print(f"Local backup image save skipped: {e}")
                preview_image = safe_img_name
            else:
                # Use the external URL as the preview image
                preview_image = preview_image_url
        else:
            try:
                upload_path = get_safe_upload_path("certificates", safe_name)
                with open(upload_path, "wb") as f:
                    f.write(cert_data)
            except Exception as e:
                print(f"Local backup image certificate save skipped: {e}")
            # Use URL as preview if provided, otherwise the image itself is the preview
            preview_image = preview_image_url if preview_image_url else safe_name
    else:
        # No file — use URL if provided (URL-only certificate card)
        if preview_image_url:
            preview_image = preview_image_url

    Certificate.add(title, issuer, date_issued, description, link, safe_name, tags, preview_image)
    cache.clear()

    flash(f"✅ Certificate '{title}' added.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/admin/toggle-certificate/<string:cert_id>", methods=["POST"])
@admin_required
def toggle_certificate(cert_id):
    """Toggle certificate visibility."""
    cert = Certificate.find_by_id(cert_id)
    if not cert: return redirect(url_for("admin.dashboard"))

    col = Certificate.get_collection()
    if col is not None:
        new_status = not cert.get("is_active", True)
        col.update_one({"_id": cert["_id"]}, {"$set": {"is_active": new_status}})
    cache.clear()

    status = "shown" if new_status else "hidden"
    flash(f"✅ '{cert['title']}' is now {status}.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/admin/delete-certificate/<string:cert_id>", methods=["POST"])
@admin_required
def delete_certificate(cert_id):
    """Permanently delete a certificate."""
    cert = Certificate.find_by_id(cert_id)
    if cert:
        title = cert["title"]
        # Delete associated GridFS and physical files
        from app.storage import delete_file
        try:
            if cert.get("filename"):
                delete_file(cert["filename"])
                file_path = get_safe_upload_path("certificates", cert["filename"])
                if os.path.exists(file_path): os.remove(file_path)
            if cert.get("preview_image") and not cert["preview_image"].startswith(("http://", "https://")):
                delete_file(cert["preview_image"])
                img_path = get_safe_upload_path("certificates", cert["preview_image"])
                if os.path.exists(img_path) and img_path != file_path: os.remove(img_path)
        except Exception as e:
            print(f"Error deleting cert files: {e}")

        Certificate.delete_by_id(cert_id)
        cache.clear()
        flash(f"🗑️ Certificate '{title}' deleted.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/admin/edit-certificate/<string:cert_id>", methods=["POST"])
@admin_required
def edit_certificate(cert_id):
    """Edit an existing certificate's metadata and optionally replace the file."""
    cert = Certificate.find_by_id(cert_id)
    if not cert:
        flash("❌ Certificate not found.", "error")
        return redirect(url_for("admin.dashboard"))

    title       = sanitize_input(request.form.get("title",       ""), 200)
    issuer      = sanitize_input(request.form.get("issuer",      ""), 200)
    date_issued = sanitize_input(request.form.get("date_issued", ""), 50)
    description = sanitize_input(request.form.get("description", ""), 1000)
    link        = sanitize_url(request.form.get("link", "#"))
    tags_raw    = sanitize_input(request.form.get("tags",        ""), 500)
    preview_image_url = sanitize_url(request.form.get("preview_image_url", ""))
    if preview_image_url == "#":
        preview_image_url = ""

    if not title or not issuer:
        flash("❌ Title and Issuer are required.", "error")
        return redirect(url_for("admin.dashboard"))

    tags = [t.strip() for t in tags_raw.split(",") if t.strip()]

    # ── Optional file replacement ─────────────────────────────────────────────
    new_filename     = cert.get("filename")       # keep existing by default
    new_preview_img  = cert.get("preview_image")  # keep existing by default

    cert_file = request.files.get("cert_file")
    if cert_file and cert_file.filename:
        is_valid, safe_name, error = validate_upload(cert_file)
        if not is_valid:
            flash(f"❌ {error}", "error")
            return redirect(url_for("admin.dashboard"))

        ext = safe_name.rsplit(".", 1)[-1].lower()
        upload_path = get_safe_upload_path("certificates", safe_name)

        if ext == "pdf":
            # PDF requires a companion image file OR a preview URL
            cert_image_file = request.files.get("cert_image_file")
            has_image_file  = cert_image_file and cert_image_file.filename
            has_image_url   = bool(preview_image_url)

            if not has_image_file and not has_image_url:
                flash("❌ A PDF certificate needs a display image. Upload one or paste an Image URL.", "error")
                return redirect(url_for("admin.dashboard"))

            # Save PDF file to GridFS & disk
            from app.storage import save_file
            cert_data = cert_file.read()
            save_file(cert_data, safe_name, content_type=cert_file.content_type)
            try:
                cert_file_path = get_safe_upload_path("certificates", safe_name)
                with open(cert_file_path, "wb") as f:
                    f.write(cert_data)
            except Exception as e:
                print(f"Local backup PDF edit save skipped: {e}")
            new_filename = safe_name

            if has_image_file:
                is_valid_img, safe_img_name, error_img = validate_upload(cert_image_file)
                if not is_valid_img:
                    flash(f"❌ Certificate Picture: {error_img}", "error")
                    return redirect(url_for("admin.dashboard"))

                img_ext = safe_img_name.rsplit(".", 1)[-1].lower()
                if img_ext not in {"png", "jpg", "jpeg", "webp"}:
                    flash("❌ The picture must be an image format (PNG, JPG, JPEG, WEBP).", "error")
                    return redirect(url_for("admin.dashboard"))

                img_data = cert_image_file.read()
                save_file(img_data, safe_img_name, content_type=cert_image_file.content_type)
                try:
                    img_upload_path = get_safe_upload_path("certificates", safe_img_name)
                    with open(img_upload_path, "wb") as f:
                        f.write(img_data)
                except Exception as e:
                    print(f"Local backup companion image edit save skipped: {e}")
                new_preview_img = safe_img_name
            else:
                # Use external URL as preview
                new_preview_img = preview_image_url
        else:
            # Direct image file — it IS the preview
            from app.storage import save_file
            cert_data = cert_file.read()
            save_file(cert_data, safe_name, content_type=cert_file.content_type)
            try:
                upload_path = get_safe_upload_path("certificates", safe_name)
                with open(upload_path, "wb") as f:
                    f.write(cert_data)
            except Exception as e:
                print(f"Local backup direct image certificate edit save skipped: {e}")
            new_filename    = safe_name
            new_preview_img = preview_image_url if preview_image_url else safe_name
    elif preview_image_url:
        # No new file — but admin pasted a URL to replace the current preview
        new_preview_img = preview_image_url

    col = Certificate.get_collection()
    if col is not None:
        col.update_one({"_id": cert["_id"]}, {"$set": {
            "title":         title,
            "issuer":        issuer,
            "date_issued":   date_issued,
            "description":   description,
            "link":          link,
            "tags":          tags,
            "filename":      new_filename,
            "preview_image": new_preview_img,
        }})
        cache.clear()
        flash(f"✅ Certificate '{title}' updated successfully.", "success")
    else:
        flash("❌ Database error.", "error")

    return redirect(url_for("admin.dashboard"))
