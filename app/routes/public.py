"""
🌐 Public Routes Blueprint — Homepage and Professional Experience
Purpose:
  Serves all public-facing pages of the portfolio, including the homepage, professional experience landing page, sitemaps, and robots.txt.
Connections:
  - app/models.py: Fetches active certifications, platforms, visible projects, and resume files to inject into context.
  - app/templates/{index.html, experience.html}: Renders server-side content with server-driven values.
  - app/extensions.py: Utilizes Flask-Caching (@cache.cached) to speed up public page load times and save database queries.
"""
import json
import os
from flask import Blueprint, render_template, jsonify, make_response, request
from app.extensions import cache
from app.models import (
    Certificate, Platform, Project, Resume, AppointmentLetter,
    Incentive, OfferLetter, PaySlip, CompanyExperience
)

public_bp = Blueprint("public", __name__)

# Site URL — set SITE_URL env var on Render to your custom domain
_SITE_URL = os.getenv("SITE_URL", "https://vigneshwaranm.onrender.com").rstrip("/")


@public_bp.route("/")
@cache.cached(timeout=60)
def home():
    """Render the portfolio page with DB-driven data."""
    certificates = Certificate.find_active()
    projects = Project.find_visible()
    platforms = Platform.find_visible()
    active_it_resume = Resume.find_active("it")
    active_sales_resume = Resume.find_active("sales")

    return render_template(
        "index.html",
        certificates=certificates,
        projects=projects,
        platforms=platforms,
        has_it_resume=active_it_resume is not None,
        has_sales_resume=active_sales_resume is not None,
    )


@public_bp.route("/experience")
@cache.cached(timeout=60)
def experience():
    """Render the professional experience landing page."""
    companies = CompanyExperience.find_all_ordered()

    enriched_companies = []
    json_data = []

    for c in companies:
        slug = c["slug"]
        c_dict = dict(c)
        c_dict["appointment_letter"] = AppointmentLetter.find_by_company(slug)
        c_dict["offer_letter"] = OfferLetter.find_by_company(slug)
        c_dict["pay_slip"] = PaySlip.find_by_company(slug)
        c_dict["incentives"] = Incentive.find_active_by_company(slug)
        enriched_companies.append(c_dict)

        json_data.append({
            "name": c.get("name"),
            "slug": c.get("slug"),
            "metric_type": c.get("metric_type"),
            "months": c.get("months", []),
            "products": c.get("products", [])
        })

    company_data_json = json.dumps(json_data)

    return render_template(
        "experience.html",
        companies=enriched_companies,
        company_data_json=company_data_json
    )


@public_bp.route("/ping")
def ping():
    """Health check for UptimeRobot / monitoring."""
    return jsonify({"status": "healthy", "version": "2.0"})


@public_bp.route("/sitemap.xml")
def sitemap():
    """Dynamic XML sitemap — consumed by Google Search Console."""
    site_url = os.getenv("SITE_URL", request.url_root).rstrip("/")
    pages = [
        (site_url + "/",           "1.0", "weekly"),
        (site_url + "/experience", "0.9", "monthly"),
    ]
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for url, priority, freq in pages:
        xml_lines.append(
            f"  <url>\n"
            f"    <loc>{url}</loc>\n"
            f"    <priority>{priority}</priority>\n"
            f"    <changefreq>{freq}</changefreq>\n"
            f"  </url>"
        )
    xml_lines.append("</urlset>")
    response = make_response("\n".join(xml_lines))
    response.headers["Content-Type"] = "application/xml"
    return response


@public_bp.route("/robots.txt")
def robots_txt():
    """robots.txt — instructs search crawlers what to allow / disallow."""
    site_url = os.getenv("SITE_URL", request.url_root).rstrip("/")
    content = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /admin\n"
        "Disallow: /vignesh-secret-2025\n"
        f"Sitemap: {site_url}/sitemap.xml\n"
    )
    return content, 200, {"Content-Type": "text/plain; charset=utf-8"}


@public_bp.route("/google1795f5f2a4eb8da8.html")
def google_verification():
    """Serve the Google Search Console verification file dynamically."""
    return "google-site-verification: google1795f5f2a4eb8da8.html", 200, {"Content-Type": "text/html; charset=utf-8"}
