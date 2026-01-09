from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os, random, smtplib, time

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
CORS(app)

# --- MongoDB Connection ---
client = MongoClient(os.getenv("MONGO_URI"))
db = client["otpDB"]
users = db["verified_users"]

# Temporary store for OTPs (stored in memory)
otp_store = {}


@app.route('/')
def home():
    return render_template("index.html")


@app.route("/send-otp", methods=["POST"])
def send_otp():
    data = request.json
    email = data.get("email")

    if not email:
        return jsonify({"message": "Email is required"}), 400

    # Generate and store a 6-digit OTP
    otp = str(random.randint(100000, 999999))
    otp_store[email] = {"otp": otp, "time": time.time()}

    try:
        # SMTP setup for Gmail
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))

        subject = "Your Verification OTP"
        body = f"""
Hello! 

Your verification OTP is: {otp}

This OTP is valid for 5 minutes.

Please do not share this OTP with anyone. 

Best regards,
Vigneshwaran M
        """
        msg = f"Subject: {subject}\n\n{body}"

        server.sendmail(os. getenv("EMAIL_USER"), email, msg)
        server.quit()

        return jsonify({"message": "OTP sent successfully to your email!"})
    except Exception as e:
        print(f"Error sending email: {e}")
        return jsonify({"message": "Failed to send OTP.  Please check your email settings. "}), 500


@app.route("/verify-otp", methods=["POST"])
def verify_otp():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    mobile = data.get("mobile")
    user_otp = data.get("otp")

    # Check if OTP exists and is not expired (5 minutes = 300 seconds)
    record = otp_store.get(email)
    if not record:
        return jsonify({"success": False, "error": "OTP not found.  Please request a new OTP."}), 400

    if (time.time() - record["time"]) > 300:
        del otp_store[email]
        return jsonify({"success":  False, "error": "OTP has expired. Please request a new one."}), 400

    # Verify OTP
    if user_otp != record["otp"]:
        return jsonify({"success": False, "error": "Invalid OTP. Please try again."}), 400

    # Check for duplicate mobile numbers in MongoDB
    if users.find_one({"mobile":  mobile}):
        return jsonify({"success": False, "error": "This mobile number is already registered. "}), 400

    # Save verified user to MongoDB
    try:
        users.insert_one({
            "name": name,
            "email": email,
            "mobile": mobile,
            "verified_at": time.time()
        })

        # Remove OTP from temporary storage
        del otp_store[email]

        return jsonify({"success": True})
    except Exception as e:
        print(f"Database error: {e}")
        return jsonify({"success": False, "error": "Database error.  Please try again. "}), 500


if __name__ == "__main__":
    # Use environment variable PORT for deployment, default to 5000 for local testing
    port = int(os. getenv("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)