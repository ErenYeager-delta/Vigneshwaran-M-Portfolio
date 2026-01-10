from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os, random, time, certifi  # certifi is required for Render SSL fix

# Load environment variables
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
CORS(app)

# --- MongoDB Connection ---
try:
    uri = os.getenv("MONGO_URI")
    # Added tlsCAFile for Render compatibility
    client = MongoClient(uri, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=5000)
    client.server_info()
    db = client["otpDB"]
    users = db["verified_users"]
    print("✅ MongoDB connected successfully")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    db = None
    users = None

otp_store = {}


@app.route('/')
def home():
    return render_template("index.html")


@app.route("/send-otp", methods=["POST"])
def send_otp():
    try:
        data = request.json
        email = data.get("email")
        if not email:
            return jsonify({"message": "Email is required"}), 400

        otp = str(random.randint(100000, 999999))
        otp_store[email] = {"otp": otp, "time": time.time()}

        print(f"🔑 OTP {otp} generated for {email}")

        # RETURN THE OTP so script.js can send it via EmailJS
        return jsonify({
            "message": "OTP generated successfully!",
            "otp": otp
        })
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"message": "Failed to generate OTP"}), 500


@app.route("/verify-otp", methods=["POST"])
def verify_otp():
    try:
        data = request.json
        email = data.get("email")
        user_otp = data.get("otp")
        name = data.get("name")
        mobile = data.get("mobile")

        if email not in otp_store:
            return jsonify({"success": False, "error": "OTP expired or not sent."}), 400

        record = otp_store[email]
        if time.time() - record["time"] > 300:
            del otp_store[email]
            return jsonify({"success": False, "error": "OTP expired."}), 400

        if user_otp != record["otp"]:
            return jsonify({"success": False, "error": "Invalid OTP."}), 400

        if users is not None:
            if users.find_one({"mobile": mobile}):
                return jsonify({"success": False, "error": "Mobile already registered."}), 400

            users.insert_one({
                "name": name,
                "email": email,
                "mobile": mobile,
                "verified_at": time.time()
            })

        del otp_store[email]
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/health")
def health():
    return jsonify({"status": "healthy", "mongodb": "connected" if users is not None else "disconnected"})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
