import os
from flask import request, redirect, url_for, flash, current_app
from app.extensions import cache
from app.models import Project
from app.security import admin_required, validate_upload, sanitize_input, sanitize_url
from app.admin import admin_bp


@admin_bp.route("/admin/add-project", methods=["POST"])
@admin_required
def add_project():
    """Add a new project to the portfolio."""
    title = sanitize_input(request.form.get("title", ""), 200)
    category = sanitize_input(request.form.get("category", ""), 100)
    project_type = sanitize_input(request.form.get("project_type", ""), 100)
    date_completed = sanitize_input(request.form.get("date_completed", ""), 50)
    image_url = sanitize_url(request.form.get("image_url", ""))
    source_code_link = sanitize_url(request.form.get("source_code_link", ""))
    deployment_link = sanitize_url(request.form.get("deployment_link", ""))
    colab_link = sanitize_url(request.form.get("colab_link", ""))
    notebook_url = sanitize_url(request.form.get("notebook_url", ""))
    description = sanitize_input(request.form.get("description", ""), 2000)
    problem_statement = sanitize_input(request.form.get("problem_statement", ""), 3000)
    solution_approach = sanitize_input(request.form.get("solution_approach", ""), 3000)
    key_metrics = sanitize_input(request.form.get("key_metrics", ""), 2000)
    tags_raw = sanitize_input(request.form.get("tags", ""), 500)
    highlight_tag = sanitize_input(request.form.get("highlight_tag", ""), 100)
    
    # Build structured DS metrics dict
    ds_metrics = {}
    for field in ["accuracy", "f1_score", "precision", "recall", "rmse", "auc_roc"]:
        val = sanitize_input(request.form.get(f"ds_{field}", ""), 50)
        if val:
            ds_metrics[field] = val
    custom_name  = sanitize_input(request.form.get("ds_custom_name",  ""), 80)
    custom_value = sanitize_input(request.form.get("ds_custom_value", ""), 50)
    if custom_name and custom_value:
        ds_metrics[custom_name] = custom_value
 
    if not title or not category:
        flash("❌ Title and Category are required.", "error")
        return redirect(url_for("admin.dashboard"))
 
    # File Upload Verification for Project Preview Image
    project_image_file = request.files.get("project_image_file")
    if project_image_file and project_image_file.filename:
        is_valid, safe_name, error_msg = validate_upload(project_image_file)
        if not is_valid:
            flash(f"❌ Project Image: {error_msg}", "error")
            return redirect(url_for("admin.dashboard"))
        
        img_ext = safe_name.rsplit(".", 1)[-1].lower()
        if img_ext not in {"png", "jpg", "jpeg", "webp", "gif"}:
            flash("❌ Project Image must be PNG, JPG, JPEG, WEBP, or GIF.", "error")
            return redirect(url_for("admin.dashboard"))
            
        upload_path = os.path.join(
            current_app.config["UPLOAD_FOLDER"], "projects", safe_name
        )
        project_image_file.save(upload_path)
        image_url = f"/static/uploads/projects/{safe_name}"
    elif deployment_link and not image_url:
        # Automatic Image Preview via Deployment Link if no image or file is provided
        image_url = f"https://image.thum.io/get/width/800/crop/600/{deployment_link}"
 
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
    
    Project.add(
        title, category, project_type, date_completed, image_url,
        source_code_link, deployment_link, description, problem_statement,
        solution_approach, key_metrics, tags, colab_link=colab_link,
        ds_metrics=ds_metrics, notebook_url=notebook_url, highlight_tag=highlight_tag
    )
    cache.clear()
    flash(f"✅ Project '{title}' added successfully.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/admin/toggle-project/<string:project_id>", methods=["POST"])
@admin_required
def toggle_project(project_id):
    """Toggle project visibility."""
    project = Project.find_by_id(project_id)
    if not project: return redirect(url_for("admin.dashboard"))

    col = Project.get_collection()
    if col is not None:
        new_status = not project.get("visible", True)
        col.update_one({"_id": project["_id"]}, {"$set": {"visible": new_status}})
    cache.clear()

    status = "visible" if new_status else "hidden"
    flash(f"✅ Project '{project['title']}' is now {status}.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/admin/delete-project/<string:project_id>", methods=["POST"])
@admin_required
def delete_project(project_id):
    """Delete a project."""
    project = Project.find_by_id(project_id)
    if project:
        title = project["title"]
        # Delete associated physical image if any
        try:
            image_url = project.get("image_url", "")
            if image_url.startswith("/static/uploads/projects/"):
                filename = image_url.split("/")[-1]
                file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], "projects", filename)
                if os.path.exists(file_path): os.remove(file_path)
        except Exception as e:
            print(f"Error deleting project image file: {e}")

        Project.delete_by_id(project_id)
        cache.clear()
        flash(f"🗑️ Project '{title}' deleted.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/admin/edit-project/<string:project_id>", methods=["POST"])
@admin_required
def edit_project(project_id):
    """Edit an existing project."""
    project = Project.find_by_id(project_id)
    if not project:
        flash("❌ Project not found.", "error")
        return redirect(url_for("admin.dashboard"))

    title = sanitize_input(request.form.get("title", ""), 200)
    category = sanitize_input(request.form.get("category", ""), 100)
    project_type = sanitize_input(request.form.get("project_type", ""), 100)
    date_completed = sanitize_input(request.form.get("date_completed", ""), 50)
    image_url = sanitize_url(request.form.get("image_url", ""))
    source_code_link = sanitize_url(request.form.get("source_code_link", ""))
    deployment_link = sanitize_url(request.form.get("deployment_link", ""))
    colab_link = sanitize_url(request.form.get("colab_link", ""))
    notebook_url = sanitize_url(request.form.get("notebook_url", ""))
    description = sanitize_input(request.form.get("description", ""), 2000)
    problem_statement = sanitize_input(request.form.get("problem_statement", ""), 3000)
    solution_approach = sanitize_input(request.form.get("solution_approach", ""), 3000)
    key_metrics = sanitize_input(request.form.get("key_metrics", ""), 2000)
    tags_raw = sanitize_input(request.form.get("tags", ""), 500)
    highlight_tag = sanitize_input(request.form.get("highlight_tag", ""), 100)
    
    # Build structured DS metrics dict
    ds_metrics = {}
    for field in ["accuracy", "f1_score", "precision", "recall", "rmse", "auc_roc"]:
        val = sanitize_input(request.form.get(f"ds_{field}", ""), 50)
        if val:
            ds_metrics[field] = val
    custom_name  = sanitize_input(request.form.get("ds_custom_name",  ""), 80)
    custom_value = sanitize_input(request.form.get("ds_custom_value", ""), 50)
    if custom_name and custom_value:
        ds_metrics[custom_name] = custom_value
    # If nothing entered, fall back to keeping existing ds_metrics
    if not ds_metrics:
        ds_metrics = project.get("ds_metrics", {})
    
    if not title or not category:
        flash("❌ Title and Category are required.", "error")
        return redirect(url_for("admin.dashboard"))
 
    # File Upload Verification for Project Preview Image (Optional replacement)
    project_image_file = request.files.get("project_image_file")
    if project_image_file and project_image_file.filename:
        is_valid, safe_name, error_msg = validate_upload(project_image_file)
        if not is_valid:
            flash(f"❌ Project Image: {error_msg}", "error")
            return redirect(url_for("admin.dashboard"))
        
        img_ext = safe_name.rsplit(".", 1)[-1].lower()
        if img_ext not in {"png", "jpg", "jpeg", "webp", "gif"}:
            flash("❌ Project Image must be PNG, JPG, JPEG, WEBP, or GIF.", "error")
            return redirect(url_for("admin.dashboard"))
            
        upload_path = os.path.join(
            current_app.config["UPLOAD_FOLDER"], "projects", safe_name
        )
        project_image_file.save(upload_path)
        image_url = f"/static/uploads/projects/{safe_name}"
    elif not image_url:
        # Keep the existing image if no upload and no URL is provided
        image_url = project.get("image_url", "")
 
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
 
    col = Project.get_collection()
    if col is not None:
        col.update_one({"_id": project["_id"]}, {"$set": {
            "title": title,
            "category": category,
            "project_type": project_type,
            "date_completed": date_completed,
            "image_url": image_url,
            "source_code_link": source_code_link,
            "deployment_link": deployment_link,
            "colab_link": colab_link,
            "notebook_url": notebook_url,
            "description": description,
            "problem_statement": problem_statement,
            "solution_approach": solution_approach,
            "key_metrics": key_metrics,
            "ds_metrics": ds_metrics,
            "tags": tags,
            "highlight_tag": highlight_tag,
        }})
        cache.clear()
        flash(f"✅ Project '{title}' updated successfully.", "success")
    else:
        flash("❌ Database error.", "error")
        
    return redirect(url_for("admin.dashboard"))
