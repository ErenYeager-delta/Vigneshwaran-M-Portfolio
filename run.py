"""
🚀 Development Server Entry Point
Purpose:
  Launches the portfolio web server locally. Reads optional PORT from environment variables.
Connections:
  - app/__init__.py: Imports create_app() application factory to spin up the Flask context.
  - app/config.py: Inspects development configuration options.
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 5000))
    debug_mode = app.config.get("DEBUG", False)
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
