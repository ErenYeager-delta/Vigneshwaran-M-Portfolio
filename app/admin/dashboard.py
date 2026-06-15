"""
📊 Administrative Dashboard Controller
Purpose:
  Renders the administrative dashboard control panel, querying all database entries
  (resumes, certifications, projects, social links, employment documentation, and experience logs)
  to feed lists to the admin templates.
Connections:
  - app/models.py: Queries all structural collection models (Resume, Certificate, Platform, etc.).
  - app/security.py: Guards access via `@admin_required` and generates a secure session CSRF token.
  - app/templates/admin/dashboard.html: Renders the unified admin administration interface.
"""
from flask import render_template
from flask_wtf.csrf import generate_csrf
from app.models import Resume, Certificate, Platform, Project, AppointmentLetter, Incentive, OfferLetter, PaySlip, CompanyExperience
from app.security import admin_required
from app.admin import admin_bp


# Connection: Invoked on admin authentication success in app/admin/auth.py (L53) or via URL navigation.
# Purpose: Renders admin/dashboard.html and fetches all database objects (resumes, projects, certifications, etc.) to list inside panels.
@admin_bp.route("/admin/dashboard")
@admin_required
def dashboard():
    """Render administrative dashboard control panel."""
    generate_csrf() # Force CSRF token into session
    resumes = Resume.find_all()
    certificates = Certificate.find_all()
    projects = Project.find_all(sort_key="created_at")
    platforms = Platform.find_all(sort_key="created_at")
    appointment_letters = AppointmentLetter.find_all()
    incentives = Incentive.find_all()
    offer_letters = OfferLetter.find_all()
    pay_slips = PaySlip.find_all()
    companies = CompanyExperience.find_all_ordered()

    return render_template(
        "admin/dashboard.html",
        resumes=resumes,
        certificates=certificates,
        projects=projects,
        platforms=platforms,
        appointment_letters=appointment_letters,
        incentives=incentives,
        offer_letters=offer_letters,
        pay_slips=pay_slips,
        companies=companies,
    )
