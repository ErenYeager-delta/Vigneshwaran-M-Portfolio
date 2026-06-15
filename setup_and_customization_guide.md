# ⚙️ Setup and Customization Guide

This guide details instructions for setting up, configuring, and modifying the Vigneshwaran M Portfolio application. Follow these steps to run the site on any system or deploy it to production.

---

## 💻 1. Terminal Commands (Installation & Execution)

Prerequisites: Ensure **Python 3.10+** is installed on your system.

### Step 1: Create Virtual Environment
Isolate python dependencies by spinning up a local virtual environment:
* **Windows (PowerShell)**:
  ```powershell
  python -m venv .venv
  ./venv/scripts/activate
  ```
* **macOS / Linux**:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### Step 2: Install Required Dependencies
Ensure you have upgraded pip and install everything from `requirements.txt`:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Run the Application Locally
Launch the local development server (bound by default to port `5000`):
```bash
python run.py
```
Visit the local client in your browser: `http://localhost:5000`

---

## 🔑 2. Environment Variables & Credentials Setup

Copy `.env.example` to a new file named `.env` in the project root:
```bash
cp .env.example .env
```
Fill out the variables listed below:

| Environment Variable | Description & Configuration Source |
| :--- | :--- |
| `MONGO_URI` | MongoDB Atlas database connectivity string (described in Step 1 below). |
| `SECRET_KEY` | Hex string signing cookies. Generate securely: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `ADMIN_PASSWORD` | Secure hash of the admin dashboard password (described in Step 2 below). |
| `ADMIN_SECRET_PATH` | Customized path segment obscuring the dashboard login url (e.g. `/vignesh-secret-2025`). |
| `SITE_URL` | Live canonical website domain url (e.g. `https://vigneshwaranm.onrender.com`). |
| `EMAILJS_SERVICE_ID` | EmailJS service identifier mapping mail delivery integrations. |
| `EMAILJS_TEMPLATE_ID` | EmailJS template identifier defining email layout parameters. |
| `EMAILJS_PUBLIC_KEY` | Account Public Key authenticating basic client API inputs. |
| `EMAILJS_PRIVATE_KEY` | Account Private Key authorizing Server-to-Server direct mail dispatches. |
| `PORT` | Local network binding port (default: `5000`). |

---

### Step 1: MongoDB Database Setup
1. Log in to the [MongoDB Atlas Console](https://www.mongodb.com/cloud/atlas).
2. Create a free-tier Shared Cluster.
3. Set up Database Access: Add a database user with **Read and Write** permissions.
4. Set up Network Access: Whitelist IP addresses. (For local testing and standard hosting solutions like Render, add `0.0.0.0/0`).
5. Select "Connect" -> "Drivers" -> Copy the connection string.
6. Paste the string under `MONGO_URI` inside your `.env` file, replacing `<password>` with your database user password:
   `MONGO_URI=mongodb+srv://<username>:<password>@cluster0.xxxx.mongodb.net/?appName=Cluster`

---

### Step 2: Admin Password Hashing
To prevent security alerts on application startups, plain text credentials are blocked in production. Paste a secure password hash:
1. Run the hashing CLI utility:
   ```bash
   python hash_password.py
   ```
2. Enter the admin credentials at the prompt.
3. Copy the output hash (starts with `scrypt:` or `pbkdf2:`) and set it inside `.env`:
   `ADMIN_PASSWORD=scrypt:32768:8:1$kXf...`

To log in, navigate to `http://localhost:5000/<ADMIN_SECRET_PATH>` (e.g. `http://localhost:5000/vignesh-secret-2025`).

---

### Step 3: EmailJS Setup & Template Mapping
The contact forms and OTP systems rely on EmailJS REST endpoints.
1. Create an account on [EmailJS](https://www.emailjs.com/).
2. Connect an email service provider (e.g. Gmail) -> Copy the **Service ID**.
3. Create an Email Template -> Copy the **Template ID**. Ensure the template contains these binding parameters:
   * `{{to_email}}`: Target email address where notification alerts are dispatched.
   * `{{name}}`: Name of sender.
   * `{{email}}`: Sender address.
   * `{{reply_to}}`: Configured reply-to mapping.
   * `{{time}}`: Dispatch time.
   * `{{message}}`: Detailed message block.
   * `{{otp_code}}`: OTP value (maps dynamic `6-digit` numeric codes, or text flags `DIRECT_MSG` / `SEC_ALERT`).
4. Find API Keys: Go to **Account** -> **API Keys** -> Copy the **Public Key** and **Private Key**. Paste all of them into `.env`.

---

## 🎨 3. Customization & Code Modifications

Use the guidelines below to modify specific visual elements and layouts:

### 🌈 Modify Theme & Accent Colors
Core styling parameters reside in variables declared at the root of:
📄 **[index.css](file:///c:/Users/1771v/Downloads/Vigneshwaran-M-Portfolio-main/Vigneshwaran-M-Portfolio-main/app/static/css/index.css#L1-L30)**

Modify variables in the `:root` pseudo-class:
```css
:root {
    --bg-dark: #090a0f;           /* Main page dark background color */
    --accent-color: #6366f1;      /* Primary accent color (indigo highlight) */
    --accent-gradient: linear-gradient(135deg, #6366f1, #a855f7); /* Highlights gradient */
    --card-bg: rgba(255, 255, 255, 0.03); /* Glassmorphism background alpha values */
    --text-primary: #f3f4f6;      /* Heading and primary text colors */
}
```

---

### 🌐 Navigation Bar & Top Header
* **HTML Element layout**: Add or remove navbar anchors in:
  📄 [index.html:L8-L25](file:///c:/Users/1771v/Downloads/Vigneshwaran-M-Portfolio-main/Vigneshwaran-M-Portfolio-main/app/templates/index.html#L8-L25)
* **Styling & CSS**: Navbar styling, hover animations, floating pill design, and media query breakpoints:
  📄 [index.css:L38-L135](file:///c:/Users/1771v/Downloads/Vigneshwaran-M-Portfolio-main/Vigneshwaran-M-Portfolio-main/app/static/css/index.css#L38-L135)
* **JS Interactions**: Scroll offset calculations and hamburger toggling logic:
  📄 [script.js:L59-L85](file:///c:/Users/1771v/Downloads/Vigneshwaran-M-Portfolio-main/Vigneshwaran-M-Portfolio-main/app/static/js/script.js#L59-L85)

---

### 💼 Dual Resume Tracks (IT vs. Sales/Marketing)
This system displays split resume download items on the front page and dashboard.
* **Database entries**: Upload a file through the admin dashboard and assign it the type: `it` or `sales`.
* **Home Page Display**:
  📄 [index.html:L33-L75](file:///c:/Users/1771v/Downloads/Vigneshwaran-M-Portfolio-main/Vigneshwaran-M-Portfolio-main/app/templates/index.html#L33-L75)
  Checks context flags `has_it_resume` and `has_sales_resume`. Toggling slides between descriptions and triggers secure download endpoints.
* **Downloads route logic**:
  📄 [downloads.py](file:///c:/Users/1771v/Downloads/Vigneshwaran-M-Portfolio-main/Vigneshwaran-M-Portfolio-main/app/routes/downloads.py)
  Controls access to the local folders. Serves files from `app/static/uploads/resumes/`.

---

### 🧪 Skills & Interactive Projects Grid
* **Projects Database Object**: Created or modified through the admin dashboard panel. Each record includes a title, highlight tag, details, source link, live deployment url, and type (`Data Science` or `Full Stack`).
* **HTML Render**:
  📄 [index.html:L340-L420](file:///c:/Users/1771v/Downloads/Vigneshwaran-M-Portfolio-main/Vigneshwaran-M-Portfolio-main/app/templates/index.html#L340-L420)
* **Dynamic Grid Filters (JS)**: Hiding/showing cards based on the selected dropdown:
  📄 [script.js:L174-L210](file:///c:/Users/1771v/Downloads/Vigneshwaran-M-Portfolio-main/Vigneshwaran-M-Portfolio-main/app/static/js/script.js#L174-L210)

---

### 🛡️ Secure OTP Modal & Masked Contacts
* **Locked DOM Inputs**: Phone number lock text and buttons:
  📄 [index.html:L461-L470](file:///c:/Users/1771v/Downloads/Vigneshwaran-M-Portfolio-main/Vigneshwaran-M-Portfolio-main/app/templates/index.html#L461-L470)
* **Trigger and verification functions (JS)**:
  📄 [script.js:L561-L645](file:///c:/Users/1771v/Downloads/Vigneshwaran-M-Portfolio-main/Vigneshwaran-M-Portfolio-main/app/static/js/script.js#L561-L645)
  Handles overlay show state, dispatch fetches to `/send-otp`, and verifies matching codes from `/verify-otp`.
* **OTP Backend validation limits**:
  📄 [api.py:L16-L86](file:///c:/Users/1771v/Downloads/Vigneshwaran-M-Portfolio-main/Vigneshwaran-M-Portfolio-main/app/routes/api.py#L16-L86)
  Applies Flask-Limiter constraints to prevent request exhaustion, handles input sanitization, and saves verified records.

---

### 📊 Experience Timeline & Company Metrics
The experience metrics route renders an interactive charts layout.
* **HTML template page**:
  📄 [experience.html](file:///c:/Users/1771v/Downloads/Vigneshwaran-M-Portfolio-main/Vigneshwaran-M-Portfolio-main/app/templates/experience.html)
* **Interactive Chart Canvas**: Incorporates Chart.js to render product performance timelines:
  📄 [experience.html:L330-L440](file:///c:/Users/1771v/Downloads/Vigneshwaran-M-Portfolio-main/Vigneshwaran-M-Portfolio-main/app/templates/experience.html#L330-L440)
* **Document Vault Downloads**: Restricts access to company payload attachments (incentives, offer letter, payslips):
  📄 [downloads.py:L26-L135](file:///c:/Users/1771v/Downloads/Vigneshwaran-M-Portfolio-main/Vigneshwaran-M-Portfolio-main/app/routes/downloads.py#L26-L135)

---

## 🛠️ 4. Production Hosting & Troubleshooting

For a detailed walkthrough of hosting issues (such as CSRF validation failures under Gunicorn workers, reverse proxy sessions checking, and database GridFS migrations), please consult the dedicated guide:
👉 **[production_troubleshooting_guide.md](production_troubleshooting_guide.md)**
