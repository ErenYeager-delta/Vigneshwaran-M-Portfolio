# Code Connections & Architectural Mapping Report

This document outlines the line-by-line connections, selectors, scripts, and operational purposes of the elements across the different pages of the portfolio application.

---

## 🌐 1. Public Portfolio Home Page

### Files Involved:
* **HTML Template**: `app/templates/index.html` (Extends `base.html`)
* **CSS Stylesheet**: `app/static/css/index.css`
* **JS Client Logic**: `app/static/js/script.js`

### Connections & Purpose:

| HTML Element & Line | CSS Selector / Line | JS Selector / Line | Operational Purpose |
| :--- | :--- | :--- | :--- |
| `<nav class="navbar">` (L8) | `.navbar` (L38) | `const navbar = ...` (L59) | Standard navigation bar curved pill design container. |
| `<button class="hamburger">` (L11) | `.hamburger` (L238) | `const hamburger = ...` (L66) | Mobile navigation toggle button. Displays burger icon transforming to an 'X' on click. |
| `<div id="navContainer">` (L17) | `#navContainer` (L75) | `const navContainer = ...` (L67) | Flex wrapper containing links. Slides out in mobile responsive layouts. |
| `<a href="#home">` (L19) | `.nav-links a` (L110) | `navLinks.forEach(...)` (L68) | Individual navigation links. Class `.active` applied by scroll observer highlights current view. |
| `<i class="fa-download btn-icon-spacing">` (L53) | `.btn-icon-spacing` (L2019) | — | Extracted margin rule to space the download icon away from the button text. |
| `<h4 class="expertise-accent-title">` (L108) | `.expertise-accent-title` (L2023) | — | Injects the core accent variable styling to section subtitle headers. |
| `<img class="tech-item-inverted">` (L244) | `.tech-item-inverted` (L2027) | — | Inverts the black Flask/Django logos to render cleanly on dark background themes. |
| `<i class="fab fa-github tech-github-icon">` (L253) | `.tech-github-icon` (L2031) | — | Enforces white icon fill for GitHub items in the marquee track. |
| `<h3 class="cert-title-size">` (L329) | `.cert-title-size` (L2035) | — | Sizes dynamic database certificate titles inside cert cards. |
| `<p class="cert-desc-text">` (L330) | `.cert-desc-text` (L2039) | — | Applies secondary muted text variables to certificate description cards. |
| `<div class="cert-card" ...>` (L322) | `.cert-card` (L732) | `document.addEventListener('click', ...)` (L472) | Click delegate target. Reading metadata attributes (e.g. data-title, data-desc, data-has-file) and loading them into the certification modal. |
| `<div class="filter-dropdown-container">` (L379) | `.filter-dropdown-container` (L1107) | `dropdownContainers.forEach(...)` (L174) | Dropdown layout container. Triggers the open state via click toggling or hover. |
| `<button class="filter-dropdown-item">` (L386) | `.filter-dropdown-item` (L1142) | `dropdownItems.forEach(...)` (L204) | Triggers project grid sorting by context and tech domain (Data Science vs. Full Stack). |
| `<div id="phonePlaceholder" class="contact-clickable">` (L461) | `.contact-clickable` (L2043) | `phonePlaceholder.addEventListener(...)` (L561) | Click indicator for phone number lock button. Triggers the OTP identity verification modal. |
| `<i class="contact-lock-icon">` (L462) | `.contact-lock-icon` (L2056) | — | Formats lock icon spacing in phone placeholder. |
| `<span class="contact-placeholder-text">` (L463) | `.contact-placeholder-text` (L2060) | — | Formats italicized placeholder block text showing masked digits. |
| `<textarea class="brief-textarea">` (L499) | `.brief-textarea` (L2065) | — | Formats project brief description box with disabled resizing handles. |
| `<button id="sendBriefBtn" class="btn-full-width">` (L502) | `.btn-full-width` (L2069) | `sendBriefBtn.addEventListener(...)` (L516) | Triggers async submit-brief backend operations. Updates status indicators to "Sending...". |
| `<div id="formStatus" class="status-brief-success">` (L505) | `.status-brief-success` (L2073) | — | Displays a green check box confirming successful brief delivery. |
| `<div id="generalModal" class="modal">` (L516) | `.modal` (L1424) | `const generalModal = ...` (L308) | Modal overlay window. Handles certificate viewing with iframe preview embeds. |
| `<a id="modalCertUrlBtn" class="btn-cert-url">` (L561) | `.btn-cert-url` (L2085) | — | Modal dynamic URL link button. Hidden unless certificate item includes verification links. |
| `<div id="verificationModal" class="modal">` (L573) | `.modal` (L1424) | `const verifyModal = ...` (L498) | Authentication modal backdrop showing user validation state. |
| `<div class="verify-modal-content">` (L574) | `.verify-modal-content` (L2089) | — | Verification modal interior container padding. |
| `<h3 class="verify-modal-title">` (L578) | `.verify-modal-title` (L2093) | — | Formats header title in authentication panels. |
| `<p class="verify-modal-subtitle">` (L579) | `.verify-modal-subtitle` (L2098) | — | Formats secondary texts explaining the OTP process. |
| `<div class="verify-input-group">` (L581) | `.verify-input-group` (L2103) | — | Vertical layout alignment containing inputs and verification buttons. |
| `<input class="verify-input">` (L583) | `.verify-input` (L2108) | — | Unified text input box style. |
| `<input id="otpInput" class="verify-otp-input">` (L598) | `.verify-otp-input` (L2121) | — | Enforces character spacings, large text size, and numeric alignments in OTP field. |
| `<button class="btn-otp-margin">` (L588) | `.btn-otp-margin` (L2135) | `sendOtpBtn` (L576) / `verifyOtpBtn` (L630) | Submits request to `/send-otp` (SMS/Mail trigger) and verifies input via `/verify-otp`. |
| `<p id="otpMsg" class="verify-status-msg">` (L602) | `.verify-status-msg` (L2139) | — | Renders dynamic text feedback during verification operations. |
| `<footer class="footer-container">` (L606) | `.footer-container` (L2144) | — | Footer container block. |
| `<div class="footer-content">` (L607) | `.footer-content` (L2150) | — | Alignment layout for footer logo and social circles. |
| `<div class="footer-socials">` (L609) | `.footer-socials` (L2158) | — | Flex row containing social anchor wraps. |
| `<a class="footer-social-link">` (L612) | `.footer-social-link` (L2163) | — | Enforces transition and default gray text color; maps hover variables dynamically. |
| `<p class="footer-copyright">` (L628) | `.footer-copyright` (L2176) | — | Formats muted credits and system versions text block. |

---

## 🔐 2. Admin Login Page

### Files Involved:
* **HTML Template**: `app/admin/templates/admin/login.html`
* **CSS Stylesheet**: `app/admin/static/css/admin_login.css`

### Connections & Purpose:

| HTML Element & Line | CSS Selector / Line | Operational Purpose |
| :--- | :--- | :--- |
| `<div class="login-box">` (L11) | `.login-box` (L12) | Anchors the absolute center box layout containing input forms. |
| `<h1>🔐 Admin Access</h1>` (L12) | `.login-box h1` (L22) | Styles the administration header (font size, margins, weights). |
| `<div class="error">` (L16) | `.error` (L27) | Renders red background warning box when credential checking fails. |
| `<input type="password">` (L21) | `input[type="password"]` (L33) | Formats password field with custom background colors, borders, and animations. |
| `<button type="submit">` (L22) | `button` (L42) | Triggers form post request to `/vignesh-secret-2025` handling login requests. |

---

## ⚡ 3. Admin Dashboard Page

### Files Involved:
* **HTML Template**: `app/admin/templates/admin/dashboard.html`
* **CSS Stylesheet**: `app/admin/static/css/admin_dashboard.css`
* **JS Client Logic**: `app/admin/static/js/admin_dashboard.js`

### Connections & Purpose:

| HTML Element & Line | CSS Selector / Line | JS Selector / Line | Operational Purpose |
| :--- | :--- | :--- | :--- |
| `<form ... class="d-inline">` (L18) | `.d-inline` (L235) | — | Extracted styling for inline buttons inside header layout tables. |
| `<h3 class="dash-section-h3">` (L38) | `.dash-section-h3` (L243) | — | Injects header typography styles inside resume upload sections. |
| `<div class="col-span-2-wrapper">` (L40) | `.col-span-2-wrapper` (L254) | — | Spans file uploads input wrappers across two grid cells. |
| `<div class="file-input-wrap full-width">` (L41) | `.full-width` (L249) | — | Force element to occupy 100% parent container space. |
| `<div id="resume_preview_box" class="upload-preview-container">` (L47) | `.upload-preview-container` (L259) | `const resumePreviewBox = ...` (L28) | Selection box. Dynamically unhides when files are dropped or selected. |
| `<div class="upload-preview-icon-box">` (L48) | `.upload-preview-icon-box` (L272) | — | Background box wrap for preview file icon. |
| `<i class="fa-file-pdf upload-preview-icon">` (L49) | `.upload-preview-icon` (L283) | — | Colors PDF icon to red and updates size. |
| `<div class="upload-preview-details">` (L51) | `.upload-preview-details` (L288) | — | Wrap styling containing file name and details. |
| `<div id="resume_file_name" class="upload-preview-filename">` (L53) | `.upload-preview-filename` (L293) | `const resumeFileName = ...` (L29) | Sets white filename color and handles ellipsis overflow. |
| `<div id="resume_file_size" class="upload-preview-filesize">` (L56) | `.upload-preview-filesize` (L303) | `const resumeFileSize = ...` (L30) | Mutes subtitle file size dimensions. |
| `<span class="upload-preview-ready">` (L59) | `.upload-preview-ready` (L309) | — | Renders green confirmation badge when file validates. |
| `<button class="toggle-btn btn-trash">` (L105) | `.btn-trash` (L316) | — | Red styling background indicating destructive operations. |
| `<button class="toggle-btn edit-cert-btn btn-edit">` (L275) | `.btn-edit` (L322) | `document.querySelectorAll('.edit-cert-btn')` (L393) | Blue styling background. Clicking triggers Modal popup containing item details. |
| `<div class="form-row grid-two-columns">` (L149) | `.grid-two-columns` (L328) | — | Displays form layouts inside subforms side by side. |
| `<label class="form-label-blue">` (L151) | `.form-label-blue` (L333) | — | Injects blue labels identifying input roles. |
| `<label class="form-label-orange">` (L197) | `.form-label-orange` (L340) | — | Injects orange warnings asking to upload cert cover image files. |
| `<div id="cert_preview_box" class="cert-preview-wrapper-box">` (L168) | `.cert-preview-wrapper-box` (L348) | `const certPreviewBox = ...` (L54) | Container box holding certificate file rendering blocks. |
| `<div id="cert_img_preview" class="cert-image-preview-sub-box">` (L170) | `.cert-image-preview-sub-box` (L359) | `const certImgPreview = ...` (L55) | JS toggles display showing uploaded certificate picture. |
| `<img id="cert_img_el" class="cert-img-element-full">` (L172) | `.cert-img-element-full` (L366) | `const certImgEl = ...` (L56) | Formats preview image display fits. |
| `<div class="cert-image-preview-label">` (L174) | `.cert-image-preview-label` (L373) | `const certImgName = ...` (L57) | Injects absolute bottom bar text overlay showing filename. |
| `<div id="cert_pdf_preview" class="cert-pdf-preview-sub-box">` (L177) | `.cert-pdf-preview-sub-box` (L383) | `const certPdfPreview = ...` (L58) | Handles layout box for uploaded PDF cover confirmations. |
| `<div id="cert_image_upload_wrap" class="cert-companion-image-wrapper">` (L196) | `.cert-companion-image-wrapper` (L390) | `const certImageUploadWrap = ...` (L61) | Companion display wrapper for PDF images. |
| `<div id="cert_image_preview_box" class="cert-companion-image-preview-box">` (L204) | `.cert-companion-image-preview-box` (L395) | `const certImagePreviewBox = ...` (L63) | Wrapper preview showing chosen companion upload file. |
| `<img id="cert_image_preview_el" class="preview-img-element">` (L206) | `.preview-img-element` (L416) | `const certImagePreviewEl = ...` (L64) | Preview image scale styling. |
| `<div id="cert_url_preview_box" class="cert-url-preview-wrapper-box">` (L212) | `.cert-url-preview-wrapper-box` (L407) | `const certUrlPreviewBox = ...` (L65) | URL-based live preview box. |
| `<div class="table-preview-img-wrap">` (L241) | `.table-preview-img-wrap` (L422) | — | Thumbnail box sizes for database items inside view tables. |
| `<img class="table-preview-img">` (L243) | `.table-preview-img` (L434) | — | Cover style layout sizing inside table cell boxes. |
| `<span class="table-preview-fallback">` (L246) | `.table-preview-fallback` (L439) | — | Mutes background styling for fileless records. |
| `<span class="table-preview-fallback-icon">` (L249) | `.table-preview-fallback-icon` (L449) | — | Mutes fallback certificate icon. |
| `<h3 class="section-sub-header">` (L315) | `.section-sub-header` (L454) | — | Formats numbered administrative form subsections. |
| `<div class="flex-1-wrapper">` (L343) | `.flex-1-wrapper` (L460) | — | Divides input grid forms equally. |
| `<div id="add_colab_wrap" class="d-none">` (L351) | `.d-none` (L239) | `const colabWrap = ...` (L162) | Toggles view displaying Colab URL inputs based on project type. |
| `<div id="image_preview_box" class="project-image-box-preview">` (L371) | `.project-image-box-preview` (L464) | `const addPreviewBox = ...` (L271) | Box area rendering live thumbnail preview. |
| `<span class="preview-placeholder-text">` (L372) | `.preview-placeholder-text` (L477) | — | Formats preview title inside project boxes. |
| `<textarea class="brief-textarea-min-height">` (L381) | `.brief-textarea-min-height` (L482) | — | Minimizes overview input container height. |
| `<p class="notebook-info-hint">` (L464) | `.notebook-info-hint` (L486) | — | Mutes Jupyter notebook hint guides. |
| `<div class="project-table-thumbnail-wrap">` (L509) | `.project-table-thumbnail-wrap` (L492) | — | Thumbnail box size layout for list tables. |
| `<span class="badge badge-purple-ds">` (L520) | `.badge-purple-ds` (L501) | — | Purple theme indicating Data Science tag attributes. |
| `<span class="badge badge-green-fs">` (L524) | `.badge-green-fs` (L507) | — | Green theme indicating Full Stack tag attributes. |
| `<span class="text-dim-fallback">` (L527) | `.text-dim-fallback` (L513) | — | Muted dash line inside empty table columns. |
| `<td class="td-highlight-tag">` (L530) | `.td-highlight-tag` (L517) | — | Colors highlight tag columns cell inputs. |
| `<td class="td-platform-url">` (L619) | `.td-platform-url` (L522) | — | Prevents platform urls from overflowing database control cards. |
| `<textarea class="brief-textarea-modal-height">` (L685) | `.brief-textarea-modal-height` (L528) | — | Modal textarea heights layout styles. |
| `<div id="ec_current_file_info" class="cert-current-file-badge">` (L696) | `.cert-current-file-badge` (L532) | `const currentFileInfo = ...` (L409) | Formats badge element showing currently uploaded certificate files. |
| `<span id="ec_current_preview_badge" class="cert-current-preview-green">` (L699) | `.cert-current-preview-green` (L543) | `const currentPreviewBadge = ...` (L411) | Injects green badge highlighting existence of cover pictures. |
| `<button type="submit" class="submit-btn full-width-submit-margin">` (L989) | `.full-width-submit-margin` (L549) | — | Force modal buttons to stretch full layout width. |
