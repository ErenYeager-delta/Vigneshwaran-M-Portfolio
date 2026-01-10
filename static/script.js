// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Script loaded successfully!');

    // --- Initialize EmailJS ---
    // Using the Public Key from your .env: vGTkdK-mR61nBEhdN
    emailjs.init("KF70fTzyyxd3aje3B");

    // --- Get DOM Elements ---
    const modal = document.getElementById("verificationModal");
    const viewNumberBtn = document.getElementById("viewNumberBtn");
    const closeBtn = document.querySelector(".close-btn");
    const phoneDisplay = document.getElementById("phoneNumber");
    const sendOtpBtn = document.getElementById("sendOtpBtn");
    const verifyOtpBtn = document.getElementById("verifyOtpBtn");

    // Check if elements exist
    if (!modal || !viewNumberBtn) {
        console.error('Required elements not found!');
        return;
    }

    // --- Modal Functions ---

    viewNumberBtn.addEventListener("click", function() {
        console.log('View Number clicked');
        modal.classList.remove("hidden");
    });

    closeBtn.addEventListener("click", function() {
        console.log('Close button clicked');
        modal.classList.add("hidden");
        resetForm();
    });

    window.addEventListener("click", function(e) {
        if (e.target === modal) {
            console.log('Outside modal clicked');
            modal.classList.add("hidden");
            resetForm();
        }
    });

    // --- Send OTP Function ---
    sendOtpBtn.addEventListener("click", function() {
        console.log('Send OTP clicked');
        sendOTP();
    });

    function sendOTP() {
        const name = document.getElementById("userName").value.trim();
        const email = document.getElementById("userEmail").value.trim();
        const mobile = document.getElementById("userMobile").value.trim();
        const msg = document.getElementById("otpMsg");

        // --- Original Validations ---
        if (!name || !email || !mobile) {
            msg.innerText = "⚠️ All fields are required.";
            msg.style.background = "#ffebee";
            msg.style.color = "#d32f2f";
            return;
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            msg.innerText = "⚠️ Please enter a valid email address.";
            msg.style.background = "#ffebee";
            msg.style.color = "#d32f2f";
            return;
        }

        const mobileRegex = /^[0-9]{10}$/;
        const cleanMobile = mobile.replace(/[^0-9]/g, "");
        if (!mobileRegex.test(cleanMobile)) {
            msg.innerText = "⚠️ Please enter a valid 10-digit mobile number.";
            msg.style.background = "#ffebee";
            msg.style.color = "#d32f2f";
            return;
        }

        // Show loading message
        msg.innerText = "📧 Generating secure OTP...";
        msg.style.background = "#e3f2fd";
        msg.style.color = "#1976d2";

        // Step 1: Fetch the OTP from your Flask backend
        fetch("/send-otp", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email: email })
        })
        .then(res => res.json())
        .then(data => {
            console.log('Backend Response:', data);

            if (data.otp) {
                // Step 2: Send the email via EmailJS using the OTP from the backend
                const templateParams = {
                    to_name: name,
                    to_email: email,
                    otp_code: data.otp // Matches {{otp_code}} in your template
                };

                return emailjs.send('service_ospo2ec', 'template_fjq3l44', templateParams);
            } else {
                throw new Error(data.message || "Failed to generate OTP");
            }
        })
        .then((response) => {
            console.log('EmailJS Success:', response.status, response.text);
            msg.innerText = "✅ OTP sent successfully to your email!";
            msg.style.background = "#e8f5e9";
            msg.style.color = "#2e7d32";

            // Hide info box and show OTP box
            document.getElementById("infoBox").classList.add("hidden");
            document.getElementById("otpBox").classList.remove("hidden");
        })
        .catch(err => {
            console.error('Process Error:', err);
            msg.innerText = "❌ Failed to send OTP. Please try again.";
            msg.style.background = "#ffebee";
            msg.style.color = "#d32f2f";
        });
    }

    // --- Verify OTP Function ---
    verifyOtpBtn.addEventListener("click", function() {
        console.log('Verify OTP clicked');
        verifyOTP();
    });

    function verifyOTP() {
        const name = document.getElementById("userName").value.trim();
        const email = document.getElementById("userEmail").value.trim();
        const mobile = document.getElementById("userMobile").value.trim();
        const otp = document.getElementById("otpInput").value.trim();
        const msg = document.getElementById("otpMsg");

        if (!otp || otp.length !== 6) {
            msg.innerText = "⚠️ Please enter a valid 6-digit OTP.";
            msg.style.background = "#ffebee";
            msg.style.color = "#d32f2f";
            return;
        }

        msg.innerText = "🔄 Verifying OTP...";
        msg.style.background = "#e3f2fd";
        msg.style.color = "#1976d2";

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
            console.log('Verify Response:', data);
            if (data.success) {
                msg.innerText = "✅ Verification Successful!";
                msg.style.background = "#e8f5e9";
                msg.style.color = "#2e7d32";

                setTimeout(function() {
                    modal.classList.add("hidden");
                    viewNumberBtn.classList.add("hidden");
                    phoneDisplay.classList.remove("hidden");
                    phoneDisplay.innerHTML = "📞 +91 8300759609";
                    resetForm();
                }, 1500);
            } else {
                msg.innerText = "❌ " + data.error;
                msg.style.background = "#ffebee";
                msg.style.color = "#d32f2f";
            }
        })
        .catch(err => {
            console.error('Verify Error:', err);
            msg.innerText = "❌ Verification failed. Please try again.";
        });
    }

    // --- Reset Form Function ---
    function resetForm() {
        document.getElementById("userName").value = "";
        document.getElementById("userEmail").value = "";
        document.getElementById("userMobile").value = "";
        document.getElementById("otpInput").value = "";
        document.getElementById("otpMsg").innerText = "";
        document.getElementById("otpMsg").style.background = "transparent";

        document.getElementById("infoBox").classList.remove("hidden");
        document.getElementById("otpBox").classList.add("hidden");
    }

    // --- Smooth Scrolling ---
    document.querySelectorAll('.nav-links a').forEach(function(link) {
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

    console.log('All event listeners attached successfully!');
});