import os
import secrets
import time
import requests
from datetime import datetime
from flask import current_app

class OTPService:
    """
    Manages OTP generation, in-memory caching, validation, and security blocks.
    Connection: Invoked by api routes (app/routes/api.py L34 and L72) to secure phone/email lock fields.
    Key Source: Caches temporary 6-digit codes in class variable memory store (_store).
    """
    _store = {}

    @classmethod
    def generate_otp(cls, email: str) -> str:
        """Generates a secure 6-digit OTP code and records it in the store."""
        otp = "".join([str(secrets.randbelow(10)) for _ in range(6)])
        cls._store[email] = {
            "otp": otp,
            "time": time.time(),
            "trials": 0,
        }
        return otp

    @classmethod
    def verify_otp_code(cls, email: str, user_otp: str) -> tuple[bool, str | None]:
        """
        Validates OTP code input.
        Returns (success: bool, error_message: str | None).
        """
        if not email or email not in cls._store:
            return False, "Session expired. Please request a new OTP."

        record = cls._store[email]

        # Check Expiration (5 minutes)
        if time.time() - record["time"] > 300:
            cls._store.pop(email, None)
            return False, "OTP expired."

        # Brute Force Protection: Max 5 trials
        if record["trials"] >= 5:
            cls._store.pop(email, None)
            return False, "Too many failed attempts. Please request a new OTP."

        if user_otp != record["otp"]:
            record["trials"] += 1
            return False, f"Invalid OTP. {5 - record['trials']} attempts remaining."

        # Success — consume the OTP
        cls._store.pop(email, None)
        return True, None


class EmailService:
    """
    Dispatches Server-to-Server email requests via EmailJS REST API.
    Connection: Relies on app/config.py keys (EMAILJS_SERVICE_ID, etc.) to compile payloads, posting to https://api.emailjs.com/api/v1.0/email/send.
    """

    @staticmethod
    def send_otp_email(email: str, name: str, otp: str) -> tuple[bool, str | None]:
        """
        Sends verification OTP email to a user.
        Connection: Triggered by /send-otp (app/routes/api.py L37) when user clicks phone/email mask lock.
        """
        try:
            email_data = {
                "service_id": current_app.config["EMAILJS_SERVICE_ID"],
                "template_id": current_app.config["EMAILJS_TEMPLATE_ID"],
                "user_id": current_app.config["EMAILJS_PUBLIC_KEY"],
                "template_params": {
                    "to_email": email,
                    "otp_code": otp,
                    "name": name,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "message": "This is a secure verification code for your portfolio access.",
                    "email": email
                },
            }

            private_key = current_app.config.get("EMAILJS_PRIVATE_KEY")
            if private_key:
                email_data["accessToken"] = private_key

            response = requests.post(
                "https://api.emailjs.com/api/v1.0/email/send",
                json=email_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )

            if response.status_code == 200:
                return True, None
            return False, response.text
        except Exception as e:
            return False, str(e)

    @staticmethod
    def send_brief_email(name: str, email: str, message: str) -> tuple[bool, str | None]:
        """
        Sends a notification to the admin regarding a new project brief submission.
        Connection: Triggered by /submit-brief (app/routes/api.py L108) when visitor submits project brief form.
        """
        try:
            payload = {
                "service_id": current_app.config["EMAILJS_SERVICE_ID"],
                "template_id": current_app.config["EMAILJS_TEMPLATE_ID"],
                "user_id": current_app.config["EMAILJS_PUBLIC_KEY"],
                "accessToken": current_app.config["EMAILJS_PRIVATE_KEY"],
                "template_params": {
                    "to_email": "1771vigneshwaran@gmail.com",
                    "name": name,
                    "email": email,
                    "reply_to": email,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "message": message,
                    "otp_code": "DIRECT_MSG"
                }
            }

            response = requests.post(
                "https://api.emailjs.com/api/v1.0/email/send",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )

            if response.status_code == 200:
                return True, None
            return False, response.text
        except Exception as e:
            return False, str(e)

    @staticmethod
    def send_security_alert(ip: str, status: str, user_agent: str) -> tuple[bool, str | None]:
        """
        Sends a security notification to the admin regarding an admin login attempt.
        Connection: Triggered by admin login authentication routes (app/admin/routes.py) on login attempt events.
        """
        try:
            payload = {
                "service_id": current_app.config["EMAILJS_SERVICE_ID"],
                "template_id": current_app.config["EMAILJS_TEMPLATE_ID"],
                "user_id": current_app.config["EMAILJS_PUBLIC_KEY"],
                "template_params": {
                    "to_email": "1771vigneshwaran@gmail.com",
                    "name": "Security Sentinel",
                    "email": "security@vigneshwaran.portfolio",
                    "reply_to": "security@vigneshwaran.portfolio",
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "message": f"ALERT: Admin Login Attempt.\nIP: {ip}\nStatus: {status}\nUser-Agent: {user_agent}",
                    "otp_code": "SEC_ALERT"
                }
            }

            private_key = current_app.config.get("EMAILJS_PRIVATE_KEY")
            if private_key:
                payload["accessToken"] = private_key

            response = requests.post(
                "https://api.emailjs.com/api/v1.0/email/send",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )

            if response.status_code == 200:
                return True, None
            return False, response.text
        except Exception as e:
            return False, str(e)
