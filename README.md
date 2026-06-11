# 🌐 Vigneshwaran M — Interactive & Secure Portfolio

A high-performance, Flask-based professional portfolio designed with a modern dark-mode aesthetic and advanced security controls. The application features twin resume tracks, experience metrics, an admin dashboard, an OTP-protected contact card, and deep integration with EmailJS and MongoDB.

---

## 🚀 Key Features

* **Dual Resume Tracks**: Modular separation allowing the user to configure and serve distinct resumes for **IT / Data Science** and **Sales / Marketing** roles.
* **OTP Identity Protection**: To block scrapers and spam, contact details (phone, email) are locked behind an OTP verification modal. Visitors verify their email/phone to unlock.
* **Administrative Control Panel**: Secure, custom-obscured `/vignesh-secret-2025` endpoint providing full management of certificates, projects, and career experiences.
* **Professional Document Vault**: Secure download system for official credentials (Offer Letters, Pay Slips, Incentives, Appointment Letters) stored securely and protected against direct directory traversal.
* **Serverless Notifications**: Integrates with EmailJS API to handle contact messages, send OTP verification tokens, and dispatch security warning notifications for unauthorized admin login attempts.

---

## 📂 Project Structure

```text
Vigneshwaran-M-Portfolio/
├── app/                           # Core Flask application package
│   ├── admin/                     # Admin dashboard blueprint
│   │   ├── static/css/            # Admin style sheets
│   │   ├── static/js/             # Admin interactive logic
│   │   ├── templates/admin/       # Admin HTML panel pages
│   │   ├── auth.py                # Admin session authentication
│   │   └── dashboard.py           # Admin control views
│   ├── routes/                    # API and public page routing blueprints
│   │   ├── api.py                 # OTP send/verify and project briefs API
│   │   ├── downloads.py           # Document security download controllers
│   │   └── public.py              # Main homepage & experience routing
│   ├── static/                    # Public web resources
│   │   ├── css/index.css          # Main UI layout styling (Vanilla CSS)
│   │   ├── js/script.js           # Client actions, modals, and observers
│   │   └── uploads/               # Subdirectories for uploaded assets
│   ├── templates/                 # Core HTML layouts
│   │   ├── base.html              # Main HTML container layout (Meta/SEO/JS)
│   │   ├── index.html             # Homepage sections (Hero, Projects, Certs)
│   │   └── experience.html        # Dynamic timeline/metrics page
│   ├── config.py                  # Environment settings and configuration map
│   ├── extensions.py              # Flask-Limiter, Cache, CSRF initializers
│   ├── models.py                  # PyMongo ORM data models (CRUD operations)
│   ├── security.py                # Input sanitization and IP brute-force logic
│   └── services.py                # OTP codes generation and EmailJS REST service
├── .env.example                   # Configuration template for deployment
├── Procfile                       # Gunicorn execution instructions for Heroku/Render
├── render.yaml                    # Blueprints for multi-service Render deployments
├── requirements.txt               # Application dependencies manifest
├── run.py                         # Local server runner script
└── setup_and_customization_guide.md # Comprehensive setup and customization instructions
```

---

## 🛠️ Quick Start

To install dependencies, set up environment secrets, connect your database, and run this application on any system, please refer to the detailed guide:
👉 **[setup_and_customization_guide.md](file:///c:/Users/1771v/Downloads/Vigneshwaran-M-Portfolio-main/Vigneshwaran-M-Portfolio-main/setup_and_customization_guide.md)**
