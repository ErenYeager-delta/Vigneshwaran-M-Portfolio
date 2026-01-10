document.addEventListener('DOMContentLoaded', function() {
    console.log('Script loaded successfully!');
    emailjs.init("KF70fTzyyxd3aje3B");

    const modal = document.getElementById("verificationModal");
    const viewNumberBtn = document.getElementById("viewNumberBtn");
    const closeBtn = document.querySelector(".close-btn");
    const phoneDisplay = document.getElementById("phoneNumber");
    const sendOtpBtn = document.getElementById("sendOtpBtn");
    const verifyOtpBtn = document.getElementById("verifyOtpBtn");

    viewNumberBtn.addEventListener("click", () => modal.classList.remove("hidden"));
    closeBtn.addEventListener("click", () => { modal.classList.add("hidden"); resetForm(); });

    sendOtpBtn.addEventListener("click", function() {
        const name = document.getElementById("userName").value.trim();
        const email = document.getElementById("userEmail").value.trim();
        const mobile = document.getElementById("userMobile").value.trim();
        const msg = document.getElementById("otpMsg");

        if (!name || !email || !mobile) {
            msg.innerText = "⚠️ All fields are required.";
            return;
        }

        msg.innerText = "📧 Generating secure OTP...";

        fetch("/send-otp", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email: email })
        })
        .then(res => res.json())
        .then(data => {
            if (data.otp) {
                // FIXED PARAMETERS FOR EMAILJS
                const templateParams = {
                    to_name: name,
                    to_email: email,      // MUST match {{to_email}} in EmailJS Dashboard
                    otp_code: data.otp    // MUST match {{otp_code}} in EmailJS Dashboard
                };
                return emailjs.send('service_ospo2ec', 'template_fjq3l44', templateParams);
            } else {
                throw new Error("OTP generation failed");
            }
        })
        .then(() => {
            msg.innerText = "✅ OTP sent successfully!";
            document.getElementById("infoBox").classList.add("hidden");
            document.getElementById("otpBox").classList.remove("hidden");
        })
        .catch(err => {
            msg.innerText = "❌ Failed to send OTP.";
            console.error(err);
        });
    });

    verifyOtpBtn.addEventListener("click", function() {
        const name = document.getElementById("userName").value.trim();
        const email = document.getElementById("userEmail").value.trim();
        const mobile = document.getElementById("userMobile").value.trim();
        const otp = document.getElementById("otpInput").value.trim();
        const msg = document.getElementById("otpMsg");

        fetch("/verify-otp", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, email, mobile, otp })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                msg.innerText = "✅ Verification Successful!";
                setTimeout(() => {
                    modal.classList.add("hidden");
                    viewNumberBtn.classList.add("hidden");
                    phoneDisplay.classList.remove("hidden");
                    phoneDisplay.innerHTML = "📞 +91 8300759609";
                }, 1500);
            } else {
                msg.innerText = "❌ " + data.error;
            }
        });
    });

    function resetForm() {
        document.getElementById("userName").value = "";
        document.getElementById("userEmail").value = "";
        document.getElementById("userMobile").value = "";
        document.getElementById("otpInput").value = "";
        document.getElementById("otpMsg").innerText = "";
        document.getElementById("infoBox").classList.remove("hidden");
        document.getElementById("otpBox").classList.add("hidden");
    }
});