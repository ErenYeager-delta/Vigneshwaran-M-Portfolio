from flask import request, redirect, url_for, flash
from app.extensions import cache
from app.models import Platform
from app.security import admin_required, sanitize_input, sanitize_url
from app.admin import admin_bp


@admin_bp.route("/admin/add-platform", methods=["POST"])
@admin_required
def add_platform():
    """Add a social platform link."""
    name = sanitize_input(request.form.get("name", ""), 100)
    url = sanitize_url(request.form.get("url", ""))
    
    icon_map = {
        "github": "fab fa-github", "linkedin": "fab fa-linkedin",
        "instagram": "fab fa-instagram", "twitter": "fab fa-twitter",
        "x": "fab fa-x-twitter", "facebook": "fab fa-facebook",
        "youtube": "fab fa-youtube", "whatsapp": "fab fa-whatsapp",
        "discord": "fab fa-discord", "telegram": "fab fa-telegram",
        "mail": "fas fa-envelope", "email": "fas fa-envelope",
        "website": "fas fa-globe", "link": "fas fa-link"
    }
    icon_class = icon_map.get(name.lower(), "fas fa-link")

    if not name or not url:
        flash("❌ Name and URL are required.", "error")
        return redirect(url_for("admin.dashboard"))

    Platform.add(name, url, icon_class)
    cache.clear()

    flash(f"✅ Platform '{name}' added.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/admin/toggle-platform/<string:platform_id>", methods=["POST"])
@admin_required
def toggle_platform(platform_id):
    """Toggle platform visibility."""
    platform = Platform.find_by_id(platform_id)
    if not platform: return redirect(url_for("admin.dashboard"))

    col = Platform.get_collection()
    if col is not None:
        new_status = not platform.get("visible", True)
        col.update_one({"_id": platform["_id"]}, {"$set": {"visible": new_status}})
    cache.clear()

    status = "visible" if new_status else "hidden"
    flash(f"✅ '{platform['name']}' is now {status}.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/admin/delete-platform/<string:platform_id>", methods=["POST"])
@admin_required
def delete_platform(platform_id):
    """Permanently delete a platform link."""
    platform = Platform.find_by_id(platform_id)
    if platform:
        name = platform["name"]
        Platform.delete_by_id(platform_id)
        cache.clear()
        flash(f"🗑️ Platform '{name}' deleted.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/admin/edit-platform/<string:platform_id>", methods=["POST"])
@admin_required
def edit_platform(platform_id):
    """Edit an existing platform link."""
    platform = Platform.find_by_id(platform_id)
    if not platform:
        flash("❌ Platform not found.", "error")
        return redirect(url_for("admin.dashboard"))

    name = sanitize_input(request.form.get("name", ""), 100)
    url  = sanitize_url(request.form.get("url",  ""))

    icon_map = {
        "github": "fab fa-github", "linkedin": "fab fa-linkedin",
        "instagram": "fab fa-instagram", "twitter": "fab fa-twitter",
        "x": "fab fa-x-twitter", "facebook": "fab fa-facebook",
        "youtube": "fab fa-youtube", "whatsapp": "fab fa-whatsapp",
        "discord": "fab fa-discord", "telegram": "fab fa-telegram",
        "mail": "fas fa-envelope", "email": "fas fa-envelope",
        "website": "fas fa-globe", "link": "fas fa-link"
    }
    icon_class = icon_map.get(name.lower(), "fas fa-link")

    if not name or not url:
        flash("❌ Name and URL are required.", "error")
        return redirect(url_for("admin.dashboard"))

    col = Platform.get_collection()
    if col is not None:
        col.update_one({"_id": platform["_id"]}, {"$set": {
            "name":       name,
            "url":        url,
            "icon_class": icon_class,
        }})
        cache.clear()
        flash(f"✅ Platform '{name}' updated successfully.", "success")
    else:
        flash("❌ Database error.", "error")

    return redirect(url_for("admin.dashboard"))
