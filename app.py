from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os, random, time
import os, random, time, certifi  # Add certifi here

# Load environment variables from .env
load_dotenv()

# Define paths explicitly
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

app = Flask(__name__,
            template_folder=TEMPLATE_DIR,
            static_folder=STATIC_DIR)
CORS(app)

# --- MongoDB Connection ---
try:
    # We combine the MONGO_URI with the certifi certificate helper in one line
    uri = os.getenv("MONGO_URI")
    client = MongoClient(uri, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=5000)
    
    # Test connection
    client.server_info()  
    
    db = client["otpDB"]
    users = db["verified_users"]
    print("✅ MongoDB connected successfully")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    db = None
    users = None

# Temporary store for OTPs (stored in memory)
otp_store = {}


@app.route('/')
def home():
    return render_template("index.html")


@app.route("/send-otp", methods=["POST"])
def send_otp():
    """
    Generates an OTP and returns it to the frontend.
    The frontend (script.js) will then send it via EmailJS.
    """
    try:
        data = request.json
        email = data.get("email")

        if not email:
            return jsonify({"message": "Email is required"}), 400

        # 1. Generate a 6-digit OTP
        otp = str(random.randint(100000, 999999))

        # 2. Store it in memory with a timestamp for verification later
        otp_store[email] = {"otp": otp, "time": time.time()}

        print(f"🔑 OTP {otp} generated for {email}")

        # 3. Return the OTP to the frontend.
        # Your script.js will catch this and trigger EmailJS.
        return jsonify({
            "message": "OTP generated successfully!",
            "otp": otp
        })

    except Exception as e:
        print(f"❌ Error generating OTP: {e}")
        return jsonify({"message": "Failed to generate OTP. Please try again."}), 500


@app.route("/verify-otp", methods=["POST"])
def verify_otp():
    """
    Verifies the OTP and saves the user to MongoDB.
    """
    try:
        data = request.json
        name = data.get("name")
        email = data.get("email")
        mobile = data.get("mobile")
        user_otp = data.get("otp")

        print(f"🔍 Verifying OTP for {email}")

        # Check if OTP exists in memory
        record = otp_store.get(email)
        if not record:
            return jsonify({"success": False, "error": "OTP not found. Please request a new OTP."}), 400

        # Check if OTP is expired (5 minutes = 300 seconds)
        if (time.time() - record["time"]) > 300:
            del otp_store[email]
            return jsonify({"success": False, "error": "OTP has expired. Please request a new one."}), 400

        # Verify the digits match
        if user_otp != record["otp"]:
            return jsonify({"success": False, "error": "Invalid OTP. Please try again."}), 400

        # Check if MongoDB is available
        if users is None:
            print("⚠️ MongoDB not available, skipping database save")
            del otp_store[email]
            return jsonify({"success": True})

        # Check for duplicate mobile numbers in MongoDB
        if users.find_one({"mobile": mobile}):
            return jsonify({"success": False, "error": "This mobile number is already registered."}), 400

        # Save verified user to MongoDB
        users.insert_one({
            "name": name,
            "email": email,
            "mobile": mobile,
            "verified_at": time.time()
        })

        # Cleanup: Remove OTP from temporary storage
        del otp_store[email]

        print(f"✅ User {name} verified and saved to MongoDB successfully")
        return jsonify({"success": True})

        #Deletes the OTP from memory so it cannot be reused
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return jsonify({"success": False, "error": "Verification failed. Please try again."}), 500


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "mongodb": "connected" if users is not None else "disconnected"
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    # Debug mode is ON unless FLASK_ENV is production
    debug_mode = os.getenv("FLASK_ENV") != "production"

    print(f"🚀 Starting Flask app on port {port}")
    app.run(debug=debug_mode, host='0.0.0.0', port=port)


