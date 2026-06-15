"""
⚙️ Admin Blueprint & Controller Initialization
Purpose:
  Defines the admin blueprint and configures local template/static directories.
  Imports all admin sub-activities (auth, dashboard, resume, certificate, project, platform, experience)
  to hook their respective HTTP handler routes.
Connections:
  - app/__init__.py: Imports and registers the blueprint `admin_bp` and binds the custom secret login route.
  - app/admin/*.py: Routes in sub-modules use `@admin_bp.route` to map dashboard operations.
"""
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
