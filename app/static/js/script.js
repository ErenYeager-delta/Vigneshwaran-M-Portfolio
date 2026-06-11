document.addEventListener('DOMContentLoaded', function () {
    console.log('Portfolio v2.0 — Secure Build');

    // Global function for dynamic icons
    window.getBrandIcon = (title, issuer) => {
        const titleLower = (title || '').toLowerCase();
        const issuerLower = (issuer || '').toLowerCase();
        
        const brandMap = {
            'python': 'fab fa-python',
            'django': 'fab fa-python',
            'flask': 'fab fa-python',
            'google': 'fab fa-google',
            'ibm': 'fab fa-ibm',
            'microsoft': 'fab fa-microsoft',
            'aws': 'fab fa-aws',
            'amazon': 'fab fa-aws',
            'meta': 'fab fa-facebook',
            'facebook': 'fab fa-facebook',
            'coursera': 'fas fa-graduation-cap',
            'udemy': 'fas fa-play-circle',
            'linkedin': 'fab fa-linkedin',
            'deep learning': 'fas fa-brain',
            'machine learning': 'fas fa-robot',
            'data science': 'fas fa-chart-line',
            'react': 'fab fa-react',
            'javascript': 'fab fa-js',
            'node': 'fab fa-node-js',
            'docker': 'fab fa-docker',
            'kubernetes': 'fas fa-dharmachakra',
            'sql': 'fas fa-database',
            'mongo': 'fas fa-leaf',
            'html': 'fab fa-html5',
            'css': 'fab fa-css3-alt',
            'full stack': 'fas fa-layer-group',
            'java': 'fab fa-java',
            'php': 'fab fa-php'
        };

        for (const [key, value] of Object.entries(brandMap)) {
            if (titleLower.includes(key) || issuerLower.includes(key)) {
                return value;
            }
        }
        return 'fas fa-certificate';
    };

    // Auto-apply icons to all cert cards immediately
    document.querySelectorAll('.cert-card').forEach(card => {
        const iconClass = window.getBrandIcon(card.dataset.title, card.dataset.issuer);
        const iconEl = card.querySelector('.cert-icon i');
        if (iconEl) iconEl.className = iconClass;
        card.dataset.icon = iconClass;
    });

    /* ============================================
       1. SMOOTH NAVIGATION & SCROLLING
       ============================================ */
    // Connection: index.html (L8), index.css (.navbar). Purpose: Observe navbar offset.
    const navbar = document.querySelector('.navbar');

    /* Navbar scroll logic removed to maintain curved pill design integrity */

    /* ============================================
       2. HAMBURGER MENU TOGGLE
       ============================================ */
    // Connection: index.html (L11), index.css (.hamburger). Purpose: Toggle mobile navigation menu.
    const hamburger = document.getElementById('hamburger');
    // Connection: index.html (L17), index.css (#navContainer). Purpose: Container containing sliding nav links.
    const navContainer = document.getElementById('navContainer');
    // Connection: index.html (L19), index.css (.nav-links a). Purpose: Highlight active menu item.
    const navLinks = document.querySelectorAll('.nav-links a');

    if (hamburger) {
        hamburger.addEventListener('click', () => {
            hamburger.classList.toggle('active');
            navContainer.classList.toggle('active');
        }, { passive: true });

        // Event delegation for nav links
        navContainer.addEventListener('click', (e) => {
            if (e.target.tagName === 'A') {
                hamburger.classList.remove('active');
                navContainer.classList.remove('active');
            }
        }, { passive: true });
    }

    /* ============================================
       3. SCROLL SPY (ACTIVE LINK HIGHLIGHT)
       ============================================ */
    const sections = document.querySelectorAll('section[id]');
    
    const scrollSpyOptions = {
        threshold: 0.2,
        rootMargin: "-20% 0px -30% 0px"
    };

    const scrollSpyObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const id = entry.target.getAttribute('id');
                navLinks.forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === `#${id}`) {
                        link.classList.add('active');
                    }
                });
            }
        });
    }, scrollSpyOptions);

    sections.forEach(section => scrollSpyObserver.observe(section));

    // Manual click override for instant feedback
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
        });
    });


    /* ============================================
       3. PROJECT FILTERING & CATEGORY DROPDOWNS
       ============================================ */
    const projectCards = document.querySelectorAll('.project-card');
    const allProjectsBtn = document.querySelector('.filter-tab[data-filter="all"]');
    // Connection: index.html (L446), index.css (.filter-dropdown-container). Purpose: Toggle hover/click open states.
    const dropdownContainers = document.querySelectorAll('.filter-dropdown-container');
    // Connection: index.html (L453), index.css (.filter-dropdown-item). Purpose: Sort projects grid.
    const dropdownItems = document.querySelectorAll('.filter-dropdown-item');

    let activeCategory = 'all';
    let activeDomain = 'all';

    const originalNames = {
        elysium: 'Elysium Center',
        self: 'Self Learning'
    };

    const domainNames = {
        all: '',
        datascience: 'Data Science',
        fullstack: 'Full Stack'
    };

    // Card filtering helper
    function filterCards() {
        projectCards.forEach(card => {
            const cardCategory = card.getAttribute('data-category'); // 'elysium' or 'self'
            const cardType = card.getAttribute('data-type');         // 'datascience' or 'fullstack'
            // The card may be wrapped in a <a class="project-card-link"> — show/hide that
            const cardWrapper = card.closest('.project-card-link') || card;

            let isMatch = false;
            if (activeCategory === 'all') {
                isMatch = true;
            } else if (cardCategory === activeCategory) {
                if (activeDomain === 'all' || cardType === activeDomain) {
                    isMatch = true;
                }
            }

            if (isMatch) {
                cardWrapper.style.display = 'block';
                setTimeout(() => {
                    cardWrapper.style.opacity = '1';
                }, 10);
            } else {
                cardWrapper.style.opacity = '0';
                setTimeout(() => {
                    cardWrapper.style.display = 'none';
                }, 300);
            }
        });
    }

    // Toggle dropdown menus on trigger click
    dropdownContainers.forEach(container => {
        const trigger = container.querySelector('.dropdown-trigger');
        
        trigger.addEventListener('click', (e) => {
            e.stopPropagation();
            
            // Toggle active-toggle class on this container, close others
            const isOpen = container.classList.contains('active-toggle');
            dropdownContainers.forEach(c => c.classList.remove('active-toggle'));
            
            if (!isOpen) {
                container.classList.add('active-toggle');
            }
        });

        // Open on hover on wider screens for fluid UX
        container.addEventListener('mouseenter', () => {
            if (window.innerWidth > 850) {
                container.classList.add('active-toggle');
            }
        });

        container.addEventListener('mouseleave', () => {
            if (window.innerWidth > 850) {
                container.classList.remove('active-toggle');
            }
        });
    });

    // Handle dropdown item click
    dropdownItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.stopPropagation();
            const category = item.getAttribute('data-filter');
            const domain = item.getAttribute('data-domain');

            activeCategory = category;
            activeDomain = domain;

            // Remove active classes
            if (allProjectsBtn) allProjectsBtn.classList.remove('active');
            dropdownContainers.forEach(c => {
                c.querySelector('.dropdown-trigger').classList.remove('active');
                c.querySelectorAll('.filter-dropdown-item').forEach(i => i.classList.remove('active'));
            });

            // Find current dropdown container and update trigger
            const parentContainer = item.closest('.filter-dropdown-container');
            const parentTrigger = parentContainer.querySelector('.dropdown-trigger');
            parentTrigger.classList.add('active');
            item.classList.add('active');

            // Update trigger label dynamically
            const labelSpan = parentTrigger.querySelector('.trigger-label');
            if (labelSpan) {
                if (domain === 'all') {
                    labelSpan.textContent = originalNames[category];
                } else {
                    labelSpan.textContent = `${originalNames[category]}: ${domainNames[domain]}`;
                }
            }

            // Reset other trigger button label to original name
            dropdownContainers.forEach(c => {
                if (c !== parentContainer) {
                    const otherTrigger = c.querySelector('.dropdown-trigger');
                    const otherCategory = otherTrigger.getAttribute('data-filter');
                    const otherLabel = c.querySelector('.trigger-label');
                    if (otherLabel) {
                        otherLabel.textContent = originalNames[otherCategory];
                    }
                    c.querySelectorAll('.filter-dropdown-item').forEach(i => {
                        if (i.getAttribute('data-domain') === 'all') {
                            i.classList.add('active');
                        } else {
                            i.classList.remove('active');
                        }
                    });
                }
            });

            // Close all dropdown menus
            dropdownContainers.forEach(c => c.classList.remove('active-toggle'));

            // Filter
            filterCards();
        });
    });

    // Handle All Projects tab click
    if (allProjectsBtn) {
        allProjectsBtn.addEventListener('click', () => {
            activeCategory = 'all';
            activeDomain = 'all';

            // Reset active states
            allProjectsBtn.classList.add('active');
            dropdownContainers.forEach(c => {
                c.querySelector('.dropdown-trigger').classList.remove('active');
                c.querySelectorAll('.filter-dropdown-item').forEach(item => {
                    if (item.getAttribute('data-domain') === 'all') {
                        item.classList.add('active');
                    } else {
                        item.classList.remove('active');
                    }
                });

                // Reset text labels
                const trigger = c.querySelector('.dropdown-trigger');
                const category = trigger.getAttribute('data-filter');
                const label = c.querySelector('.trigger-label');
                if (label) {
                    label.textContent = originalNames[category];
                }
            });

            // Close all dropdowns
            dropdownContainers.forEach(c => c.classList.remove('active-toggle'));

            // Filter
            filterCards();
        });
    }

    // Close dropdowns when clicking outside
    document.addEventListener('click', () => {
        dropdownContainers.forEach(c => c.classList.remove('active-toggle'));
    });

    /* ============================================
       4. GENERAL MODAL LOGIC
       Reads data from HTML data-* attributes
       (rendered server-side by Jinja — no secrets in JS)
       ============================================ */
    // Connection: index.html (L581), index.css (.modal). Purpose: Certificate details modal.
    const generalModal = document.getElementById('generalModal');
    const closeGeneralModal = document.getElementById('closeGeneralModal');
    const closeGeneralModalBtn = document.getElementById('closeGeneralModalBtn');

    let currentZoom = 1;
    const modalPreview = document.getElementById('modalPreviewContainer');

    function openModalFromElement(el) {
        if (!el) return;

        const data = {
            id: el.dataset.certId || '',
            issuer: el.dataset.issuer || '',
            title: el.dataset.title || '',
            date: el.dataset.date || '',
            desc: el.dataset.desc || '',
            icon: el.dataset.icon || 'fas fa-certificate',
            link: el.dataset.link || '#',
            tags: el.dataset.tags ? JSON.parse(el.dataset.tags) : [],
            hasFile: el.dataset.hasFile === 'true',
            filename: el.dataset.filename || '',
            image: el.dataset.image || '',
            previewImage: el.dataset.previewImage || ''
        };

        try {
            data.tags = JSON.parse(el.dataset.tags || '[]');
        } catch (e) {
            data.tags = [];
        }

        // Set text content
        const setSafe = (id, text) => {
            const target = document.getElementById(id);
            if (target) target.textContent = text;
        };

        setSafe('modalIssuer', data.issuer);
        setSafe('modalTitle', data.title);
        setSafe('modalDate', data.date.includes('Issued') ? data.date : `Issued: ${data.date}`);
        setSafe('modalDesc', data.desc);

        const actionBtn = document.getElementById('modalActionBtn');
        const certUrlBtn = document.getElementById('modalCertUrlBtn');
        const downloadBtn = document.getElementById('modalDownloadBtn');
        
        if (actionBtn) {
            if (data.hasFile && !el.classList.contains('project-card')) {
                actionBtn.href = `/certificate/` + data.id + `/preview#toolbar=0`;
                actionBtn.textContent = 'View Certificate';
            } else {
                actionBtn.href = data.link;
                actionBtn.textContent = el.classList.contains('project-card') ? 'View Project' : 'View Certificate';
            }
            
            // If it's a project card, or if it doesn't have a file, the actionBtn acts as the main link.
            // If we have a file AND a link (for certs), we show the certUrlBtn as well.
            if (actionBtn.href === '#' || !actionBtn.href || actionBtn.href.endsWith('#')) {
                actionBtn.style.display = 'none';
            } else {
                actionBtn.style.display = 'inline-block';
            }
            const icon = document.createElement('i');
            icon.className = 'fas fa-external-link-alt';
            icon.style.marginLeft = '8px';
            actionBtn.appendChild(icon);
        }

        if (certUrlBtn) {
            if (data.link && data.link !== '#' && data.hasFile && !el.classList.contains('project-card')) {
                certUrlBtn.href = data.link;
                certUrlBtn.style.display = 'inline-block';
            } else {
                certUrlBtn.style.display = 'none';
            }
        }

        if (downloadBtn) {
            if (data.hasFile && !el.classList.contains('project-card')) {
                downloadBtn.href = `/certificate/` + data.id + `/download`;
                downloadBtn.style.display = 'inline-block';
            } else {
                downloadBtn.style.display = 'none';
            }
        }

        // --- Brand Icon Logic ---
        const issuerIcon = document.getElementById('modalIssuerIcon');
        if (issuerIcon) {
            issuerIcon.className = window.getBrandIcon(data.title, data.issuer);
        }

        // --- Visual Side Logic ---
        const previewContainer = document.getElementById('modalPreviewContainer');
        const defaultIcon = document.getElementById('modalDefaultIcon');
        
        // Clear previous content
        const existingImg = previewContainer.querySelector('img');
        const existingIframe = previewContainer.querySelector('iframe');
        if (existingImg) existingImg.remove();
        if (existingIframe) existingIframe.remove();

        if (data.image) {
            defaultIcon.style.display = 'none';
            const img = document.createElement('img');
            img.src = data.image;
            img.alt = data.title;
            img.style.width = '100%';
            img.style.height = '100%';
            img.style.objectFit = 'cover';
            img.style.borderRadius = '15px';
            previewContainer.appendChild(img);
        } else if (!el.classList.contains('project-card')) {
            const ext = data.filename ? data.filename.split('.').pop().toLowerCase() : '';
            defaultIcon.style.display = 'none';
            
            if (data.previewImage) {
                const img = document.createElement('img');
                img.src = `/certificate/${data.id}/preview-image`;
                img.alt = data.title;
                img.style.width = '100%';
                img.style.height = '100%';
                img.style.objectFit = 'contain';
                previewContainer.appendChild(img);
            } else if (data.hasFile && ['jpg', 'jpeg', 'png', 'webp', 'gif'].includes(ext)) {
                const img = document.createElement('img');
                img.src = `/certificate/${data.id}/preview`;
                img.alt = data.title;
                img.style.width = '100%';
                img.style.height = '100%';
                img.style.objectFit = 'contain';
                previewContainer.appendChild(img);
            } else if (data.hasFile && ext === 'pdf') {
                const iframe = document.createElement('iframe');
                iframe.src = `/certificate/${data.id}/preview#toolbar=0`;
                iframe.style.width = '100%';
                iframe.style.height = '100%';
                iframe.style.border = 'none';
                iframe.style.borderRadius = '15px';
                previewContainer.appendChild(iframe);
            } else if (data.link && data.link !== '#' && data.link.startsWith('http')) {
                const img = document.createElement('img');
                img.src = `https://image.thum.io/get/width/800/crop/600/${data.link}`;
                img.alt = data.title;
                img.style.width = '100%';
                img.style.height = '100%';
                img.style.objectFit = 'cover';
                img.style.borderRadius = '15px';
                previewContainer.appendChild(img);
            } else {
                defaultIcon.style.display = 'flex';
            }
        } else {
            defaultIcon.style.display = 'flex';
        }

        // --- Render Tags ---
        const metaBox = document.getElementById('modalMeta');
        while (metaBox.firstChild) metaBox.removeChild(metaBox.firstChild);

        data.tags.forEach(tag => {
            const span = document.createElement('span');
            span.className = 'tech-tag-new';
            span.textContent = tag;
            metaBox.appendChild(span);
        });

        generalModal.classList.remove('hidden');
        void generalModal.offsetWidth;
        generalModal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    // Connection: index.html (.cert-card L329), index.css (.cert-card). Purpose: Click delegate target to load certification details into modal.
    document.addEventListener('click', (e) => {
        const card = e.target.closest('.cert-card');
        if (card) {
            openModalFromElement(card);
        }
    }, { passive: true });

    function closeModal() {
        generalModal.classList.remove('active');
        setTimeout(() => {
            generalModal.classList.add('hidden');
            document.body.style.overflow = 'auto';
        }, 400); // Matches transition duration
    }

    if (closeGeneralModal) closeGeneralModal.addEventListener('click', closeModal);
    if (closeGeneralModalBtn) closeGeneralModalBtn.addEventListener('click', closeModal);

    window.addEventListener('click', (e) => {
        if (e.target === generalModal) closeModal();
    });

    /* ============================================
       5. OTP & VERIFICATION LOGIC
       (All sensitive processing happens on the backend)
       ============================================ */
    // Connection: index.html (L640), index.css (.modal). Purpose: OTP validation overlay.
    const verifyModal = document.getElementById("verificationModal");
    const viewNumberBtn = document.getElementById("viewNumberBtn");
    const closeVerifyModal = document.getElementById("closeVerifyModal");
    const phoneDisplay = document.getElementById("revealedPhone");
    // Connection: index.html (L650), index.css (.btn-otp-margin). Purpose: Requesting secure OTPs.
    const sendOtpBtn = document.getElementById("sendOtpBtn");
    // Connection: index.html (L659), index.css (.btn-otp-margin). Purpose: Confirming and verifying OTP inputs.
    const verifyOtpBtn = document.getElementById("verifyOtpBtn");

    let otpSendInProgress = false;
    let otpVerifyInProgress = false;

    const openVerifyModal = () => {
        verifyModal.classList.remove("hidden");
        void verifyModal.offsetWidth; // Force reflow
        verifyModal.classList.add("active");
        document.body.style.overflow = 'hidden';
        resetForm();
    };

    // Connection: index.html (L568), index.css (.btn-full-width). Purpose: Form submission trigger to /submit-brief.
    const sendBriefBtn = document.getElementById("sendBriefBtn");
    if (sendBriefBtn) {
        sendBriefBtn.addEventListener("click", async function() {
            const name = document.getElementById("briefName").value.trim();
            const email = document.getElementById("briefEmail").value.trim();
            const message = document.getElementById("briefMessage").value.trim();
            const status = document.getElementById("formStatus");

            if (!name || !email || !message) {
                alert("Please fill in all fields.");
                return;
            }

            sendBriefBtn.disabled = true;
            sendBriefBtn.innerText = "Sending...";

            try {
                const response = await fetch("/submit-brief", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ name, email, message })
                });

                if (response.ok) {
                    status.classList.remove("hidden");
                    sendBriefBtn.innerText = "Message Sent";
                } else {
                    const data = await response.json();
                    alert(data.message || "Failed to send message. Please try again.");
                    sendBriefBtn.disabled = false;
                    sendBriefBtn.innerText = "Send Message";
                }
            } catch (err) {
                alert("An error occurred.");
                sendBriefBtn.disabled = false;
                sendBriefBtn.innerText = "Send Message";
            }
        });
    }

    if (viewNumberBtn) {
        viewNumberBtn.addEventListener("click", openVerifyModal);
    }

    // Connection: index.html (L528), index.css (.contact-clickable). Purpose: Reveal lock click triggering verification modal.
    const phonePlaceholder = document.getElementById("phonePlaceholder");
    if (phonePlaceholder) {
        console.log("✅ Phone placeholder listener attached");
        phonePlaceholder.addEventListener("click", () => {
            console.log("📞 Phone placeholder clicked");
            openVerifyModal();
        });
    }

    if (closeVerifyModal) {
        closeVerifyModal.addEventListener("click", () => {
            verifyModal.classList.remove("active");
            setTimeout(() => {
                verifyModal.classList.add("hidden");
                document.body.style.overflow = 'auto';
                resetForm();
            }, 400);
        });
    }

    // Connection: index.html (L650), index.css (.btn-otp-margin). Purpose: Submits credentials request post to /send-otp API.
    if (sendOtpBtn) {
        sendOtpBtn.addEventListener("click", async function () {
            if (otpSendInProgress) return;

            const name = document.getElementById("userName").value.trim();
            const email = document.getElementById("userEmail").value.trim();
            const mobile = document.getElementById("userMobile").value.trim();
            const msg = document.getElementById("otpMsg");

            if (!name || !email || !mobile) {
                msg.innerText = "⚠️ All fields are required.";
                msg.style.color = "#ff4d4d";
                return;
            }

            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                msg.innerText = "⚠️ Please enter a valid email address.";
                msg.style.color = "#ff4d4d";
                return;
            }

            otpSendInProgress = true;
            sendOtpBtn.disabled = true;
            msg.innerText = "📧 Generating secure OTP...";
            msg.style.color = "var(--accent)";

            try {
                const response = await fetch("/send-otp", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email: email, name: name })
                });

                if (response.ok) {
                    msg.innerText = "✅ OTP sent! Check your email.";
                    msg.style.color = "var(--accent)";
                    infoBox.classList.add("hidden");
                    otpBox.classList.remove("hidden");
                } else {
                    const data = await response.json();
                    msg.innerText = "❌ " + (data.message || "Failed to send OTP. Try again.");
                    msg.style.color = "#ff4d4d";
                }
            } catch (err) {
                msg.innerText = "❌ Failed to send OTP. Try again.";
                msg.style.color = "#ff4d4d";
            } finally {
                otpSendInProgress = false;
                sendOtpBtn.disabled = false;
            }
        });
    }

    // Connection: index.html (L659), index.css (.btn-otp-margin). Purpose: Submits OTP post request to /verify-otp API.
    if (verifyOtpBtn) {
        verifyOtpBtn.addEventListener("click", function () {
            if (otpVerifyInProgress) return;

            const name = document.getElementById("userName").value.trim();
            const email = document.getElementById("userEmail").value.trim();
            const mobile = document.getElementById("userMobile").value.trim();
            const otp = document.getElementById("otpInput").value.trim();
            const msg = document.getElementById("otpMsg");

            if (!otp || otp.length !== 6 || isNaN(otp)) {
                msg.innerText = "⚠️ Enter a valid 6-digit OTP.";
                msg.style.color = "#ff4d4d";
                return;
            }

            otpVerifyInProgress = true;
            verifyOtpBtn.disabled = true;
            msg.innerText = "🔐 Verifying...";

            fetch("/verify-otp", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name, email, mobile, otp })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    msg.innerText = "✅ Verification Successful!";
                    msg.style.color = "#28a745";
                    setTimeout(() => {
                        verifyModal.classList.remove("active");
                        setTimeout(() => {
                            verifyModal.classList.add("hidden");
                            document.body.style.overflow = 'auto';
                            if (viewNumberBtn) {
                                viewNumberBtn.innerText = "PROTOCOL INITIATED";
                                viewNumberBtn.disabled = true;
                            }

                            // Show success message on form
                            const formStatus = document.getElementById("formStatus");
                            if (formStatus) formStatus.classList.remove("hidden");
                            
                            // Reveal logic
                            const placeholder = document.getElementById("phonePlaceholder");
                            const phoneDisplay = document.getElementById("revealedPhone");
                            if (placeholder) placeholder.classList.add("hidden");
                            if (phoneDisplay) phoneDisplay.classList.remove("hidden");
                        }, 400);
                    }, 1500);
                } else {
                    msg.innerText = "❌ " + (data.error || "Verification failed.");
                    msg.style.color = "#ff4d4d";
                }
            })
            .catch(err => {
                msg.innerText = "❌ Error during verification.";
                msg.style.color = "#ff4d4d";
            })
            .finally(() => {
                otpVerifyInProgress = false;
                verifyOtpBtn.disabled = false;
            });
        });
    }

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

