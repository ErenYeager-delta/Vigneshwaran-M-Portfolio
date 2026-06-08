import os
from flask import request, redirect, url_for, flash, current_app
from app.extensions import limiter, cache
from app.models import Resume
from app.security import admin_required, validate_upload, get_safe_upload_path
from app.admin import admin_bp


@admin_bp.route("/admin/upload-resume", methods=["POST"])
@admin_required
@limiter.limit("10 per hour")
def upload_resume():
    """Upload new resume — auto-deactivates old ones of the same type."""
    file = request.files.get("resume_file")
    resume_type = request.form.get("resume_type", "it")
    if resume_type not in ("it", "sales"):
        resume_type = "it"

    is_valid, safe_name, error = validate_upload(file, {"pdf"})

    if not is_valid:
        flash(f"❌ {error}", "error")
        return redirect(url_for("admin.dashboard"))

    # Read file data for hash check
    file_data = file.read()
    file_hash = Resume.compute_hash(file_data)

    # Check for duplicate
    col = Resume.get_collection()
    if col is not None and col.find_one({"file_hash": file_hash}):
        flash("⚠️ This exact file has already been uploaded.", "warning")
        return redirect(url_for("admin.dashboard"))

    # Save file
    upload_path = get_safe_upload_path("resumes", safe_name)
    with open(upload_path, "wb") as f:
        f.write(file_data)

    # Add to MongoDB (auto-deactivates others of same type)
    Resume.add(safe_name, file.filename, file_hash, resume_type)
    cache.clear()

    type_name = "IT Section" if resume_type == "it" else "Sales & Marketing"
    flash(f"✅ {type_name} Resume '{file.filename}' uploaded and activated.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/admin/toggle-resume/<string:resume_id>", methods=["POST"])
@admin_required
def toggle_resume(resume_id):
    """Toggle resume active status."""
    resume = Resume.find_by_id(resume_id)
    if not resume:
        flash("❌ Resume not found.", "error")
        return redirect(url_for("admin.dashboard"))

    # If we're activating this one, deactivate all others of the same type first
    is_active = resume.get("is_active", False)
    if not is_active:
        Resume.deactivate_all(resume.get("resume_type", "it"))
    
    col = Resume.get_collection()
    if col is not None:
        col.update_one({"_id": resume["_id"]}, {"$set": {"is_active": not is_active}})
    cache.clear()
    
    status = "activated" if not is_active else "deactivated"
    flash(f"✅ Resume '{resume['original_name']}' {status}.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/admin/delete-resume/<string:resume_id>", methods=["POST"])
@admin_required
def delete_resume(resume_id):
    """Permanently delete a resume file and record."""
    resume = Resume.find_by_id(resume_id)
    if not resume:
        flash("❌ Resume not found.", "error")
        return redirect(url_for("admin.dashboard"))
    
    name = resume["original_name"]
    
    # Delete physical file
    try:
        file_path = get_safe_upload_path("resumes", resume["filename"])
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Error deleting file: {e}")

    Resume.delete_by_id(resume_id)
    cache.clear()
    
    flash(f"🗑️ Resume '{name}' deleted.", "success")
    return redirect(url_for("admin.dashboard"))
