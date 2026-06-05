import os
import json
from flask import request, redirect, url_for, flash, current_app, render_template
from app.extensions import limiter, cache
from app.models import AppointmentLetter, Incentive, OfferLetter, PaySlip, CompanyExperience
from app.security import admin_required, validate_upload
from app.admin import admin_bp


@admin_bp.route("/admin/upload-appointment-letter", methods=["POST"])
@admin_required
@limiter.limit("10 per hour")
def upload_appointment_letter():
    """Upload a new appointment letter (PDF) for a specific company."""
    file = request.files.get("letter_file")
    company = request.form.get("company")

    comp_obj = CompanyExperience.find_by_slug(company)
    if not comp_obj:
        flash("❌ Invalid company selected.", "error")
        return redirect(url_for("admin.dashboard"))

    is_valid, safe_name, error = validate_upload(file, {"pdf"})
    if not is_valid:
        flash(f"❌ {error}", "error")
        return redirect(url_for("admin.dashboard"))

    file_data = file.read()
    upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], "appointment_letters", safe_name)
    
    with open(upload_path, "wb") as f:
        f.write(file_data)

    AppointmentLetter.add(safe_name, file.filename, company)
    cache.clear()

    company_name = comp_obj["name"]
    flash(f"✅ Appointment letter uploaded for {company_name}.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/admin/delete-appointment-letter/<string:letter_id>", methods=["POST"])
@admin_required
def delete_appointment_letter(letter_id):
    """Delete an appointment letter file and database entry."""
    letter = AppointmentLetter.find_by_id(letter_id)
    if not letter:
        flash("❌ Appointment letter not found.", "error")
        return redirect(url_for("admin.dashboard"))

    filename = letter["filename"]
    try:
        file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], "appointment_letters", filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Error deleting file: {e}")

    AppointmentLetter.delete_by_id(letter_id)
    cache.clear()

    flash(f"🗑️ Appointment letter deleted.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/admin/upload-incentive", methods=["POST"])
@admin_required
@limiter.limit("20 per hour")
def upload_incentive():
    """Upload a new incentive certificate/receipt image for a specific company."""
    file = request.files.get("incentive_file")
    company = request.form.get("company")
    order = request.form.get("order", 0)

    comp_obj = CompanyExperience.find_by_slug(company)
    if not comp_obj:
        flash("❌ Invalid company selected.", "error")
        return redirect(url_for("admin.dashboard"))

    is_valid, safe_name, error = validate_upload(file, {"png", "jpg", "jpeg", "webp"})
    if not is_valid:
        flash(f"❌ {error}", "error")
        return redirect(url_for("admin.dashboard"))

    file_data = file.read()
    upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], "incentives", safe_name)
    
    with open(upload_path, "wb") as f:
        f.write(file_data)

    Incentive.add(safe_name, file.filename, company, order)
    cache.clear()

    company_name = comp_obj["name"]
    flash(f"✅ Incentive image uploaded for {company_name} with display order {order}.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/admin/delete-incentive/<string:inc_id>", methods=["POST"])
@admin_required
def delete_incentive(inc_id):
    """Delete an incentive document image file and database entry."""
    incentive = Incentive.find_by_id(inc_id)
    if not incentive:
        flash("❌ Incentive not found.", "error")
        return redirect(url_for("admin.dashboard"))

    filename = incentive["filename"]
    try:
        file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], "incentives", filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Error deleting file: {e}")

    Incentive.delete_by_id(inc_id)
    cache.clear()

    flash(f"🗑️ Incentive document deleted.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/admin/upload-offer-letter", methods=["POST"])
@admin_required
@limiter.limit("10 per hour")
def upload_offer_letter():
    """Upload a new offer letter (PDF) for a specific company."""
    file = request.files.get("offer_file")
    company = request.form.get("company")

    comp_obj = CompanyExperience.find_by_slug(company)
    if not comp_obj:
        flash("❌ Invalid company selected.", "error")
        return redirect(url_for("admin.dashboard"))

    is_valid, safe_name, error = validate_upload(file, {"pdf"})
    if not is_valid:
        flash(f"❌ {error}", "error")
        return redirect(url_for("admin.dashboard"))

    file_data = file.read()
    upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], "offer_letters", safe_name)
    
    with open(upload_path, "wb") as f:
        f.write(file_data)

    OfferLetter.add(safe_name, file.filename, company)
    cache.clear()

    company_name = comp_obj["name"]
    flash(f"✅ Offer letter uploaded for {company_name}.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/admin/delete-offer-letter/<string:letter_id>", methods=["POST"])
@admin_required
def delete_offer_letter(letter_id):
    """Delete an offer letter file and database entry."""
    letter = OfferLetter.find_by_id(letter_id)
    if not letter:
        flash("❌ Offer letter not found.", "error")
        return redirect(url_for("admin.dashboard"))

    filename = letter["filename"]
    try:
        file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], "offer_letters", filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Error deleting file: {e}")

    OfferLetter.delete_by_id(letter_id)
    cache.clear()

    flash(f"🗑️ Offer letter deleted.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/admin/upload-pay-slip", methods=["POST"])
@admin_required
@limiter.limit("15 per hour")
def upload_pay_slip():
    """Upload a new pay slip (PDF) for a specific company."""
    file = request.files.get("slip_file")
    company = request.form.get("company")

    comp_obj = CompanyExperience.find_by_slug(company)
    if not comp_obj:
        flash("❌ Invalid company selected.", "error")
        return redirect(url_for("admin.dashboard"))

    is_valid, safe_name, error = validate_upload(file, {"pdf"})
    if not is_valid:
        flash(f"❌ {error}", "error")
        return redirect(url_for("admin.dashboard"))

    file_data = file.read()
    upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], "pay_slips", safe_name)
    
    with open(upload_path, "wb") as f:
        f.write(file_data)

    PaySlip.add(safe_name, file.filename, company)
    cache.clear()

    company_name = comp_obj["name"]
    flash(f"✅ Pay slip uploaded for {company_name}.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/admin/delete-pay-slip/<string:slip_id>", methods=["POST"])
@admin_required
def delete_pay_slip(slip_id):
    """Delete a pay slip file and database entry."""
    slip = PaySlip.find_by_id(slip_id)
    if not slip:
        flash("❌ Pay slip not found.", "error")
        return redirect(url_for("admin.dashboard"))

    filename = slip["filename"]
    try:
        file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], "pay_slips", filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Error deleting file: {e}")

    PaySlip.delete_by_id(slip_id)
    cache.clear()

    flash(f"🗑️ Pay slip deleted.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/admin/experience/add", methods=["POST"])
@admin_required
def add_company_experience():
    """Create a new company experience with basic placeholder details."""
    name = request.form.get("name")
    slug = request.form.get("slug")
    role_title = request.form.get("role_title")
    duration = request.form.get("duration")
    location = request.form.get("location")
    metric_type = request.form.get("metric_type", "units")
    sort_order = request.form.get("sort_order", 1)

    if not name or not slug or not role_title:
        flash("❌ Name, slug, and role title are required.", "error")
        return redirect(url_for("admin.dashboard"))

    slug = slug.strip().lower().replace(" ", "-")

    description = "Managed regional pharmaceutical operations and portfolio targets."
    bullets = [
        "Collaborated with clinical staff and medical professionals to increase customer engagement.",
        "Demonstrated product benefits to doctor preferences to maximize revenue sales."
    ]
    skills = ["Sales Operations", "Marketing Strategy", "Client Presentations"]

    comp = CompanyExperience.add(
        name=name,
        slug=slug,
        role_title=role_title,
        duration=duration,
        location=location,
        description=description,
        bullets=bullets,
        skills=skills,
        metric_type=metric_type,
        sort_order=int(sort_order)
    )

    if not comp:
        flash("❌ Slug already exists or error occurred.", "error")
    else:
        flash(f"✅ Company '{name}' created successfully! You can now edit its analytics details.", "success")
        cache.clear()

    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/admin/experience/delete/<string:company_id>", methods=["POST"])
@admin_required
def delete_company_experience(company_id):
    """Delete a company experience record and associated files/documents."""
    comp = CompanyExperience.find_by_id(company_id)
    if not comp:
        flash("❌ Company not found.", "error")
        return redirect(url_for("admin.dashboard"))

    slug = comp["slug"]

    # Delete associated files
    col_app = AppointmentLetter.get_collection()
    if col_app is not None:
        letters = list(col_app.find({"company": slug}))
        for l in letters:
            try:
                os.remove(os.path.join(current_app.config["UPLOAD_FOLDER"], "appointment_letters", l["filename"]))
            except Exception: pass
        col_app.delete_many({"company": slug})

    col_off = OfferLetter.get_collection()
    if col_off is not None:
        letters = list(col_off.find({"company": slug}))
        for l in letters:
            try:
                os.remove(os.path.join(current_app.config["UPLOAD_FOLDER"], "offer_letters", l["filename"]))
            except Exception: pass
        col_off.delete_many({"company": slug})

    col_pay = PaySlip.get_collection()
    if col_pay is not None:
        slips = list(col_pay.find({"company": slug}))
        for s in slips:
            try:
                os.remove(os.path.join(current_app.config["UPLOAD_FOLDER"], "pay_slips", s["filename"]))
            except Exception: pass
        col_pay.delete_many({"company": slug})

    col_inc = Incentive.get_collection()
    if col_inc is not None:
        incs = list(col_inc.find({"company": slug}))
        for i in incs:
            try:
                os.remove(os.path.join(current_app.config["UPLOAD_FOLDER"], "incentives", i["filename"]))
            except Exception: pass
        col_inc.delete_many({"company": slug})

    CompanyExperience.delete_by_id(company_id)
    cache.clear()
    flash(f"🗑️ Company '{comp['name']}' and its associated documents/analytics were deleted.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/admin/experience/edit/<string:company_id>", methods=["GET", "POST"])
@admin_required
def edit_company_experience(company_id):
    """GET renders spreadsheet editor, POST saves edited metrics & profile details."""
    comp = CompanyExperience.find_by_id(company_id)
    if not comp:
        flash("❌ Company not found.", "error")
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        try:
            name = request.form.get("name")
            role_title = request.form.get("role_title")
            duration = request.form.get("duration")
            location = request.form.get("location")
            description = request.form.get("description")
            metric_type = request.form.get("metric_type", "units")
            sort_order = request.form.get("sort_order", 1)

            bullets_raw = request.form.get("bullets", "")
            bullets = [b.strip() for b in bullets_raw.split("\n") if b.strip()]

            skills_raw = request.form.get("skills", "")
            skills = [s.strip() for s in skills_raw.split(",") if s.strip()]

            months_raw = request.form.get("months_data", "[]")
            months = json.loads(months_raw)
            for m in months:
                m["target"] = float(m.get("target", 0))
                m["sales"] = float(m.get("sales", 0))

            products_raw = request.form.get("products_data", "[]")
            products = json.loads(products_raw)
            for p in products:
                p["price"] = float(p.get("price", 0))
                p["target"] = int(p.get("target", 0))
                p["sales"] = int(p.get("sales", 0))

            data = {
                "name": name,
                "role_title": role_title,
                "duration": duration,
                "location": location,
                "description": description,
                "bullets": bullets,
                "skills": skills,
                "metric_type": metric_type,
                "sort_order": int(sort_order),
                "months": months,
                "products": products
            }
            CompanyExperience.update_by_id(company_id, data)
            cache.clear()
            flash("✅ Experience and analytics updated successfully!", "success")
            return redirect(url_for("admin.dashboard"))
        except Exception as e:
            flash(f"❌ Error updating experience: {str(e)}", "error")
            return redirect(url_for("admin.edit_company_experience", company_id=company_id))

    return render_template("admin/edit_experience.html", company=comp)
