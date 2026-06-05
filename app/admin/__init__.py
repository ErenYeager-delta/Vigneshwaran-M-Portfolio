from flask import Blueprint

admin_bp = Blueprint(
    "admin",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/admin/static"
)

# Import sub-activities to register routes on the blueprint
from app.admin import auth, dashboard, resume, certificate, project, platform, experience
