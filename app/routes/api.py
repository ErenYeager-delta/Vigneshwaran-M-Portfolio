"""
API routes — OTP send/verify.
Refactored to cleanly delegate database and notification tasks to model/service layers.
"""

import re
from flask import Blueprint, request, jsonify
from app.extensions import limiter
from app.models import VerifiedUser, ProjectBrief
from app.services import OTPService, EmailService
from app.security import sanitize_input

api_bp = Blueprint("api", __name__)


@api_bp.route("/send-otp", methods=["POST"])
@limiter.limit("3 per minute")
def send_otp():
    """Send OTP via EmailJS service layer."""
    try:
        data = request.json or {}
        email = data.get("email")
        name = data.get("name", "User")

        if not email:
            return jsonify({"message": "Email is required"}), 400

        # Backend Email Validation
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            return jsonify({"message": "Invalid email format"}), 400

        # Generate OTP
        otp = OTPService.generate_otp(email)

        # Trigger Send
        success, error_detail = EmailService.send_otp_email(email, name, otp)
        if not success:
            print(f"❌ EmailJS Error: {error_detail}")
            return jsonify({
                "message": "Failed to send verification email. Please try again later.",
                "status": 500
            }), 500

        print(f"✅ OTP sent to {email} successfully.")
        return jsonify({"message": "OTP sent successfully to your email!"})

    except Exception as e:
        print(f"Error in send_otp route: {e}")
        return jsonify({"message": "An internal error occurred"}), 500


@api_bp.route("/verify-otp", methods=["POST"])
@limiter.limit("5 per minute")
def verify_otp():
    """Verify OTP and save verified user to database."""
    try:
        data = request.json or {}
        email = data.get("email")
        user_otp = data.get("otp")
        name = data.get("name")
        mobile = data.get("mobile")

        if not email:
            return jsonify({"success": False, "error": "Session expired. Please request a new OTP."}), 400

        # Sanitize input
        name = sanitize_input(name, max_length=100)
        mobile = sanitize_input(mobile, max_length=20)

        # Verify Code
        success, error_msg = OTPService.verify_otp_code(email, user_otp)
        if not success:
            return jsonify({"success": False, "error": error_msg}), 400

        # Save to database
        if VerifiedUser.find_by_mobile(mobile):
            return jsonify({"success": False, "error": "Mobile already registered."}), 400

        VerifiedUser.add(name, email, mobile)
        return jsonify({"success": True})

    except Exception as e:
        print(f"Error in verify_otp route: {e}")
        return jsonify({"success": False, "error": "An internal error occurred."}), 500


@api_bp.route("/submit-brief", methods=["POST"])
def submit_brief():
    """Submit Project Brief via EmailService notification and store details in database."""
    try:
        data = request.json or {}
        name = data.get("name")
        email = data.get("email")
        message = data.get("message")

        if not name or not email or not message:
            return jsonify({"message": "Missing required fields"}), 400

        # Check for duplicates
        if ProjectBrief.find_brief_by_email(email):
            return jsonify({"message": "This email has already submitted a project brief."}), 400

        # Add to database
        ProjectBrief.add_brief(name, email, message)

        # Trigger Admin Email Notification
        success, error_detail = EmailService.send_brief_email(name, email, message)
        if not success:
            print(f"❌ EmailJS Error: {error_detail}")
            return jsonify({"message": "Failed to send email"}), 500

        return jsonify({"success": True}), 200

    except Exception as e:
        print(f"Error in submit_brief route: {e}")
        return jsonify({"message": "Internal error"}), 500
