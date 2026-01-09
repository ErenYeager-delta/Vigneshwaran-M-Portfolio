// --- Modal and Phone Number View Logic ---

const modal = document.getElementById("verificationModal");
const viewNumberBtn = document.getElementById("viewNumberBtn");
const closeBtn = document.querySelector(".close-btn");
const phoneDisplay = document.getElementById("phoneNumber");

// Open modal when "View Number" button is clicked
viewNumberBtn.addEventListener("click", () => {
    modal.classList.remove("hidden");
});

// Close modal when X button is clicked
closeBtn.addEventListener("click", () => {
    modal.classList.add("hidden");
    resetForm();
});

// Close modal when clicking outside the modal content
window.addEventListener("click", (e) => {
    if (e.target === modal) {
        modal.classList.add("hidden");
        resetForm();
    }
});

// --- Send OTP Function ---
function sendOTP() {
    const name = document.getElementById("userName").value.trim();
    const email = document.getElementById("userEmail").value.trim();
    const mobile = document.getElementById("userMobile").value.trim();
    const msg = document.getElementById("otpMsg");

    // Validation
    if (!name || !email || !mobile) {
        msg.innerText = "⚠️ All fields are required.";
        msg.style.background = "#ffebee";
        msg.style.color = "#d32f2f";
        return;
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        msg.innerText = "⚠️ Please enter a valid email address.";
        msg.style.background = "#ffebee";
        msg.style.color = "#d32f2f";
        return;
    }

    // Mobile validation (10 digits)
    const mobileRegex = /^[0-9]{10}$/;
    const cleanMobile = mobile.replace(/[^0-9]/g, "");
    if (!mobileRegex.test(cleanMobile)) {
        msg.innerText = "⚠️ Please enter a valid 10-digit mobile number.";
        msg.style.background = "#ffebee";
        msg.style.color = "#d32f2f";
        return;
    }

    // Show loading message
    msg.innerText = "📧 Sending OTP to your email...";
    msg.style.background = "#e3f2fd";
    msg.style.color = "#1976d2";

    // Send OTP request to backend
    fetch("/send-otp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email })
    })
    .then(res => res.json())
    .then(data => {
        msg.innerText = "✅ " + data.message;
        msg.style.background = "#e8f5e9";
        msg.style.color = "#2e7d32";

        // Hide info box and show OTP box
        document.getElementById("infoBox").classList.add("hidden");
        document.getElementById("otpBox").classList.remove("hidden");
    })
    .catch(err => {
        msg.innerText = "❌ Error. Please check your connection.";
        msg.style.background = "#ffebee";
        msg.style.color = "#d32f2f";
    });
}

// --- Verify OTP Function ---
document.getElementById("verifyOtpBtn").addEventListener("click", () => {
    const name = document.getElementById("userName").value.trim();
    const email = document.getElementById("userEmail").value.trim();
    const mobile = document.getElementById("userMobile").value.trim();
    const otp = document.getElementById("otpInput").value.trim();
    const msg = document.getElementById("otpMsg");

    // Validation
    if (!otp || otp.length !== 6) {
        msg.innerText = "⚠️ Please enter a valid 6-digit OTP.";
        msg.style.background = "#ffebee";
        msg.style.color = "#d32f2f";
        return;
    }

    // Show loading
    msg.innerText = "🔄 Verifying OTP...";
    msg.style.background = "#e3f2fd";
    msg.style.color = "#1976d2";

    // Verify OTP with backend
    fetch("/verify-otp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            name: name,
            email: email,
            mobile: mobile,
            otp: otp
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            // Success! Show the full phone number
            msg.innerText = "✅ Verification Successful!";
            msg.style.background = "#e8f5e9";
            msg.style.color = "#2e7d32";

            // Hide modal after a short delay
            setTimeout(() => {
                modal.classList.add("hidden");

                // Hide the "View Number" button
                viewNumberBtn.classList.add("hidden");

                // Show the full phone number
                phoneDisplay.classList.remove("hidden");
                phoneDisplay.innerHTML = "📞 +91 8300759609"; // Replace with your actual number

                // Reset form
                resetForm();
            }, 1500);
        } else {
            // Error in verification
            msg.innerText = "❌ " + data.error;
            msg.style.background = "#ffebee";
            msg.style.color = "#d32f2f";
        }
    })
    .catch(err => {
        msg.innerText = "❌ Verification failed. Please try again.";
        msg.style.background = "#ffebee";
        msg.style.color = "#d32f2f";
    });
});

// --- Reset Form Function ---
function resetForm() {
    document.getElementById("userName").value = "";
    document.getElementById("userEmail").value = "";
    document.getElementById("userMobile").value = "";
    document.getElementById("otpInput").value = "";
    document.getElementById("otpMsg").innerText = "";

    // Show info box, hide OTP box
    document.getElementById("infoBox").classList.remove("hidden");
    document.getElementById("otpBox").classList.add("hidden");
}

// --- Smooth Scrolling for Navigation Links ---
document.querySelectorAll('.nav-links a').forEach(link => {
    link.addEventListener('click', function(e) {
        e.preventDefault();
        const targetId = this.getAttribute('href');
        const targetSection = document.querySelector(targetId);

        if (targetSection) {
            targetSection.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});