// ══════════════════════════════════════════════
// 1. COLLAPSIBLE FORM TOGGLE
// ══════════════════════════════════════════════
document.querySelectorAll('.toggle-form-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const targetId = this.getAttribute('data-target');
        const container = document.getElementById(targetId);
        if (!container) return;
        const isVisible = container.style.display === 'block';
        if (isVisible) {
            container.style.display = 'none';
            this.classList.remove('active');
            const label = targetId.replace('-form-container', '');
            const capitalized = label.charAt(0).toUpperCase() + label.slice(1);
            this.innerHTML = `<i class="fas fa-plus"></i> Add ${capitalized}`;
        } else {
            container.style.display = 'block';
            this.classList.add('active');
            this.innerHTML = `<i class="fas fa-times"></i> Cancel`;
        }
    });
});

// ══════════════════════════════════════════════
// 2. RESUME FILE UPLOAD PREVIEW
// ══════════════════════════════════════════════
const resumeFileInput = document.getElementById('resume_file_input');
const resumePreviewBox = document.getElementById('resume_preview_box');
const resumeFileName = document.getElementById('resume_file_name');
const resumeFileSize = document.getElementById('resume_file_size');

if (resumeFileInput && resumePreviewBox) {
    resumeFileInput.addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            resumePreviewBox.style.display = 'flex';
            resumeFileName.textContent = file.name;
            const sizeKB = (file.size / 1024).toFixed(1);
            const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
            resumeFileSize.textContent = file.size > 1024 * 1024
                ? `${sizeMB} MB`
                : `${sizeKB} KB`;
        } else {
            resumePreviewBox.style.display = 'none';
        }
    });
}

// ══════════════════════════════════════════════
// 3. CERTIFICATE FILE UPLOAD PREVIEW (Add Form)
// ══════════════════════════════════════════════
const certFileInput        = document.getElementById('cert_file_input');
const certImageUrlInput    = document.getElementById('cert_image_url');
const certPreviewBox       = document.getElementById('cert_preview_box');
const certImgPreview       = document.getElementById('cert_img_preview');
const certImgEl            = document.getElementById('cert_img_el');
const certImgName          = document.getElementById('cert_img_name');
const certPdfPreview       = document.getElementById('cert_pdf_preview');
const certPdfName          = document.getElementById('cert_pdf_name');
const certPdfSize          = document.getElementById('cert_pdf_size');
const certImageUploadWrap  = document.getElementById('cert_image_upload_wrap');
const certImageInput       = document.getElementById('cert_image_input');
const certImagePreviewBox  = document.getElementById('cert_image_preview_box');
const certImagePreviewEl   = document.getElementById('cert_image_preview_el');
const certUrlPreviewBox    = document.getElementById('cert_url_preview_box');
const certUrlPreviewEl     = document.getElementById('cert_url_preview_el');

// Helper: hide all cert preview areas
function resetCertAddPreviews() {
    if (certPreviewBox)      certPreviewBox.style.display = 'none';
    if (certImgPreview)      certImgPreview.style.display = 'none';
    if (certPdfPreview)      certPdfPreview.style.display = 'none';
    if (certImageUploadWrap) certImageUploadWrap.style.display = 'none';
    if (certImageInput)      { certImageInput.required = false; certImageInput.value = ''; }
    if (certImagePreviewBox) certImagePreviewBox.style.display = 'none';
    if (certUrlPreviewBox)   certUrlPreviewBox.style.display = 'none';
}

if (certFileInput) {
    certFileInput.addEventListener('change', function() {
        // Clear the URL input when a file is chosen
        if (certImageUrlInput) { certImageUrlInput.value = ''; }
        if (certUrlPreviewBox) certUrlPreviewBox.style.display = 'none';

        const file = this.files[0];
        if (!file) { resetCertAddPreviews(); return; }

        certPreviewBox.style.display = 'block';
        const ext = file.name.split('.').pop().toLowerCase();

        if (['png', 'jpg', 'jpeg', 'webp'].includes(ext)) {
            certPdfPreview.style.display = 'none';
            certImgPreview.style.display = 'block';
            if (certImageUploadWrap) certImageUploadWrap.style.display = 'none';
            if (certImageInput) { certImageInput.required = false; certImageInput.value = ''; }
            if (certImagePreviewBox) certImagePreviewBox.style.display = 'none';
            const reader = new FileReader();
            reader.onload = (e) => { certImgEl.src = e.target.result; certImgName.textContent = file.name; };
            reader.readAsDataURL(file);
        } else if (ext === 'pdf') {
            certImgPreview.style.display = 'none';
            certPdfPreview.style.display = 'flex';
            certPdfName.textContent = file.name;
            const sizeKB = (file.size / 1024).toFixed(1);
            const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
            certPdfSize.textContent = file.size > 1024 * 1024 ? `${sizeMB} MB` : `${sizeKB} KB`;
            // Show companion image section only if no URL provided
            if (!certImageUrlInput || !certImageUrlInput.value.trim()) {
                if (certImageUploadWrap) certImageUploadWrap.style.display = 'block';
                if (certImageInput) certImageInput.required = true;
            }
        } else {
            certImgPreview.style.display = 'none';
            certPdfPreview.style.display = 'none';
            if (certImageUploadWrap) certImageUploadWrap.style.display = 'none';
            if (certImageInput) { certImageInput.required = false; certImageInput.value = ''; }
            if (certImagePreviewBox) certImagePreviewBox.style.display = 'none';
        }
    });
}

// URL input → live preview + clear file
if (certImageUrlInput) {
    certImageUrlInput.addEventListener('input', function() {
        const url = this.value.trim();
        if (url) {
            // Clear any chosen file
            if (certFileInput) certFileInput.value = '';
            resetCertAddPreviews();
            // Show URL preview
            certUrlPreviewBox.style.display = 'block';
            certUrlPreviewEl.src = url;
        } else {
            if (certUrlPreviewBox) certUrlPreviewBox.style.display = 'none';
        }
    });
}

if (certImageInput && certImagePreviewBox) {
    certImageInput.addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            certImagePreviewBox.style.display = 'flex';
            const reader = new FileReader();
            reader.onload = (e) => { certImagePreviewEl.src = e.target.result; };
            reader.readAsDataURL(file);
        } else {
            certImagePreviewBox.style.display = 'none';
        }
    });
}

// ══════════════════════════════════════════════
// 4. PROJECT DYNAMIC FORM UTILITIES
// ══════════════════════════════════════════════
function updateProjectFields(formType, projectType) {
    const isAdd = formType === 'add';
    const prefix = isAdd ? 'add_' : 'edit_';
    
    const sourceCodeEl = document.getElementById(prefix + 'source_code_link');
    const deploymentWrap = document.getElementById(prefix + 'deployment_wrap');
    const colabWrap = document.getElementById(prefix + 'colab_wrap');
    
    const problemLabel = document.getElementById(prefix + 'problem_label');
    const problemTextarea = document.getElementById(prefix + 'problem_statement');
    const solutionLabel = document.getElementById(prefix + 'solution_label');
    const solutionTextarea = document.getElementById(prefix + 'solution_approach');
    const metricsLabel = document.getElementById(prefix + 'metrics_label');
    const metricsTextarea = document.getElementById(prefix + 'key_metrics');

    if (projectType === 'datascience') {
        if (deploymentWrap) deploymentWrap.style.display = 'none';
        if (colabWrap) colabWrap.style.display = 'block';
        if (sourceCodeEl) {
            sourceCodeEl.required = false;
            sourceCodeEl.placeholder = "Source Code Link (Optional for Data Science)";
        }
        if (problemLabel) problemLabel.innerHTML = '<i class="fas fa-exclamation-circle"></i> What is the goal of this data project?';
        if (problemTextarea) problemTextarea.placeholder = 'What are you trying to predict or analyze? What is the main goal? (e.g. Predict house prices based on size and location).';
        if (solutionLabel) solutionLabel.innerHTML = '<i class="fas fa-check-circle"></i> What data and models did you use?';
        if (solutionTextarea) solutionTextarea.placeholder = 'How did you clean the data and train your models? (e.g. Collected 10,000 house listings, cleaned empty rows, used linear regression and decision trees).';
        if (metricsLabel) metricsLabel.innerHTML = '<i class="fas fa-chart-line"></i> How did the model perform?';
        if (metricsTextarea) metricsTextarea.placeholder = 'What were your final model results? (e.g. 92% prediction accuracy | 0.90 F1-Score | Fast prediction response).';
        
        // Show DS metrics section
        const dsMetricsSec = document.getElementById(prefix + 'ds_metrics_section');
        if (dsMetricsSec) dsMetricsSec.style.display = 'block';
    } else {
        if (deploymentWrap) deploymentWrap.style.display = 'block';
        if (colabWrap) colabWrap.style.display = 'none';
        if (sourceCodeEl) {
            sourceCodeEl.required = true;
            sourceCodeEl.placeholder = "Source Code Link (Required for Full Stack) *";
        }
        if (problemLabel) problemLabel.innerHTML = '<i class="fas fa-exclamation-circle"></i> What problem does this project solve?';
        if (problemTextarea) problemTextarea.placeholder = 'What is this app for? What problem does it solve for users? (e.g. A website to order food online easily).';
        if (solutionLabel) solutionLabel.innerHTML = '<i class="fas fa-check-circle"></i> How did you build it?';
        if (solutionTextarea) solutionTextarea.placeholder = 'What technologies did you use for the frontend and backend? How does it work? (e.g. React frontend, Node.js backend, and MongoDB database).';
        if (metricsLabel) metricsLabel.innerHTML = '<i class="fas fa-list-ul"></i> Key Features of the App';
        if (metricsTextarea) metricsTextarea.placeholder = 'What are the main features of your app? (e.g. User Login | Product Search | Shopping Cart | Payment System).';
        
        // Hide DS metrics section
        const dsMetricsSec = document.getElementById(prefix + 'ds_metrics_section');
        if (dsMetricsSec) dsMetricsSec.style.display = 'none';
    }
}

function validateAndPreviewImage(fileInput, previewBox, urlInput) {
    const file = fileInput.files[0];
    if (!file) return;

    const allowedExtensions = ['png', 'jpg', 'jpeg', 'webp', 'gif'];
    const maxSizeBytes = 5 * 1024 * 1024; // 5 MB

    const ext = file.name.split('.').pop().toLowerCase();
    if (!allowedExtensions.includes(ext)) {
        alert(`❌ Invalid file type. Allowed formats: ${allowedExtensions.join(', ')}`);
        fileInput.value = '';
        if (previewBox) {
            previewBox.innerHTML = '<span style="color: #ff4d4d; font-size: 0.8rem;">Invalid file format</span>';
            previewBox.style.borderStyle = 'dashed';
        }
        return;
    }

    if (file.size > maxSizeBytes) {
        alert('❌ File size exceeds 5MB limit. Please choose a smaller image.');
        fileInput.value = '';
        if (previewBox) {
            previewBox.innerHTML = '<span style="color: #ff4d4d; font-size: 0.8rem;">File size too large (>5MB)</span>';
            previewBox.style.borderStyle = 'dashed';
        }
        return;
    }

    const reader = new FileReader();
    reader.onload = function(e) {
        if (previewBox) {
            previewBox.innerHTML = `<img src="${e.target.result}" style="width: 100%; height: 100%; object-fit: cover;">`;
            previewBox.style.borderStyle = 'solid';
        }
    };
    reader.readAsDataURL(file);

    if (urlInput) {
        urlInput.value = '';
    }
}

// Attach listeners for Add Project type-switching
const addProjectTypeEl = document.getElementById('add_project_type');
if (addProjectTypeEl) {
    addProjectTypeEl.addEventListener('change', function() {
        updateProjectFields('add', this.value);
    });
    // Run on load to set defaults
    updateProjectFields('add', addProjectTypeEl.value);
}

// Attach listeners for Edit Project type-switching
const editProjectTypeEl = document.getElementById('edit_project_type');
if (editProjectTypeEl) {
    editProjectTypeEl.addEventListener('change', function() {
        updateProjectFields('edit', this.value);
    });
}

// Image file upload listeners
const addProjectImgFile = document.getElementById('add_project_image_file');
const addProjectImgUrl = document.getElementById('project_image_url');
const addPreviewBox = document.getElementById('image_preview_box');
if (addProjectImgFile) {
    addProjectImgFile.addEventListener('change', function() {
        validateAndPreviewImage(this, addPreviewBox, addProjectImgUrl);
    });
}

const editProjectImgFile = document.getElementById('edit_project_image_file');
const editProjectImgUrl = document.getElementById('edit_image_url');
const editPreviewBox = document.getElementById('edit_image_preview_box');
if (editProjectImgFile) {
    editProjectImgFile.addEventListener('change', function() {
        validateAndPreviewImage(this, editPreviewBox, editProjectImgUrl);
    });
}

// Live text URL preview listeners
if (addProjectImgUrl && addPreviewBox) {
    addProjectImgUrl.addEventListener('input', function() {
        const url = this.value.trim();
        if (url) {
            if (addProjectImgFile) addProjectImgFile.value = '';
            addPreviewBox.innerHTML = `<img src="${url}" style="width: 100%; height: 100%; object-fit: cover;">`;
            addPreviewBox.style.borderStyle = 'solid';
        } else {
            addPreviewBox.innerHTML = `<span style="color: #555; font-size: 0.8rem;">Image Preview</span>`;
            addPreviewBox.style.borderStyle = 'dashed';
        }
    });
}

if (editProjectImgUrl && editPreviewBox) {
    editProjectImgUrl.addEventListener('input', function() {
        const url = this.value.trim();
        if (url) {
            if (editProjectImgFile) editProjectImgFile.value = '';
            editPreviewBox.innerHTML = `<img src="${url}" style="width: 100%; height: 100%; object-fit: cover;">`;
            editPreviewBox.style.borderStyle = 'solid';
        } else {
            editPreviewBox.innerHTML = `<span style="color: #555; font-size: 0.8rem;">Image Preview</span>`;
            editPreviewBox.style.borderStyle = 'dashed';
        }
    });
}

// ══════════════════════════════════════════════
// 5. EDIT PROJECT MODAL
// ══════════════════════════════════════════════
const editModal = document.getElementById('editProjectModal');
const closeEditModalBtn = document.getElementById('closeEditModal');
const editForm = document.getElementById('editProjectForm');

document.querySelectorAll('.edit-project-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const id = this.getAttribute('data-id');
        editForm.action = `/admin/edit-project/${id}`;

        // Reset file input
        if (editProjectImgFile) editProjectImgFile.value = '';

        document.getElementById('edit_title').value = this.getAttribute('data-title') || '';
        document.getElementById('edit_category').value = this.getAttribute('data-category') || '';
        
        const projType = this.getAttribute('data-project_type') || '';
        document.getElementById('edit_project_type').value = projType;
        
        document.getElementById('edit_date_completed').value = this.getAttribute('data-date_completed') || '';
        document.getElementById('edit_tags').value = this.getAttribute('data-tags') || '';
        document.getElementById('edit_highlight_tag').value = this.getAttribute('data-highlight_tag') || '';
        document.getElementById('edit_source_code_link').value = this.getAttribute('data-source_code_link') || '';
        document.getElementById('edit_deployment_link').value = this.getAttribute('data-deployment_link') || '';
        document.getElementById('edit_colab_link').value = this.getAttribute('data-colab_link') || '';

        const imgUrl = this.getAttribute('data-image_url') || '';
        document.getElementById('edit_image_url').value = imgUrl;
        if (editPreviewBox) {
            if (imgUrl) {
                editPreviewBox.innerHTML = `<img src="${imgUrl}" style="width: 100%; height: 100%; object-fit: cover;">`;
                editPreviewBox.style.borderStyle = 'solid';
            } else {
                editPreviewBox.innerHTML = `<span style="color: #555; font-size: 0.8rem;">Image Preview</span>`;
                editPreviewBox.style.borderStyle = 'dashed';
            }
        }

        document.getElementById('edit_description').value = this.getAttribute('data-description') || '';
        document.getElementById('edit_problem_statement').value = this.getAttribute('data-problem_statement') || '';
        document.getElementById('edit_solution_approach').value = this.getAttribute('data-solution_approach') || '';
        document.getElementById('edit_key_metrics').value = this.getAttribute('data-key_metrics') || '';

        // Populate Data Science metrics fields from JSON
        let dsMetrics = {};
        try { dsMetrics = JSON.parse(this.getAttribute('data-ds_metrics') || '{}'); } catch(e) {}
        const setField = (id, val) => { const el = document.getElementById(id); if (el) el.value = val || ''; };
        setField('edit_ds_accuracy',    dsMetrics.accuracy    || '');
        setField('edit_ds_f1_score',    dsMetrics.f1_score    || '');
        setField('edit_ds_precision',   dsMetrics.precision   || '');
        setField('edit_ds_recall',      dsMetrics.recall      || '');
        setField('edit_ds_rmse',        dsMetrics.rmse        || '');
        setField('edit_ds_auc_roc',     dsMetrics.auc_roc     || '');
        setField('edit_ds_custom_name', dsMetrics.custom_name || '');
        setField('edit_ds_custom_value',dsMetrics.custom_value|| '');
        setField('edit_notebook_url',   this.getAttribute('data-notebook_url') || '');

        // Run type-specific field updater to update placeholders and show/hide Colab/Deployment inputs
        updateProjectFields('edit', projType);

        editModal.classList.add('active');
    });
});

if (closeEditModalBtn) {
    closeEditModalBtn.addEventListener('click', () => editModal.classList.remove('active'));
}

// ══════════════════════════════════════════════
// 6. EDIT CERTIFICATE MODAL
// ══════════════════════════════════════════════
const editCertModal = document.getElementById('editCertificateModal');
const closeEditCertBtn = document.getElementById('closeEditCertModal');
const editCertForm = document.getElementById('editCertificateForm');

document.querySelectorAll('.edit-cert-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const id           = this.getAttribute('data-id');
        const filename     = this.getAttribute('data-filename') || '';
        const previewImg   = this.getAttribute('data-preview_image') || '';

        editCertForm.action = `/admin/edit-certificate/${id}`;

        document.getElementById('ec_title').value        = this.getAttribute('data-title') || '';
        document.getElementById('ec_issuer').value       = this.getAttribute('data-issuer') || '';
        document.getElementById('ec_date_issued').value  = this.getAttribute('data-date_issued') || '';
        document.getElementById('ec_link').value         = this.getAttribute('data-link') || '';
        document.getElementById('ec_tags').value         = this.getAttribute('data-tags') || '';
        document.getElementById('ec_description').value  = this.getAttribute('data-description') || '';

        // Show current file info
        const currentFileInfo = document.getElementById('ec_current_file_info');
        const currentFilename = document.getElementById('ec_current_filename');
        const currentPreviewBadge = document.getElementById('ec_current_preview_badge');
        if (filename) {
            currentFilename.textContent = filename;
            currentPreviewBadge.style.display = previewImg ? 'inline' : 'none';
            currentFileInfo.style.display = 'block';
        } else {
            currentFileInfo.style.display = 'none';
        }

        // Populate and reset the URL field
        const ecPreviewUrlInput = document.getElementById('ec_preview_image_url');
        const ecCertUrlPreviewBox = document.getElementById('ec_cert_url_preview_box');
        const ecCertUrlPreviewEl  = document.getElementById('ec_cert_url_preview_el');

        // If preview_image is an external URL, put it in the URL field and show preview
        if (ecPreviewUrlInput) {
            if (previewImg && (previewImg.startsWith('http://') || previewImg.startsWith('https://'))) {
                ecPreviewUrlInput.value = previewImg;
                if (ecCertUrlPreviewBox) { ecCertUrlPreviewBox.style.display = 'block'; }
                if (ecCertUrlPreviewEl)  { ecCertUrlPreviewEl.src = previewImg; }
            } else {
                ecPreviewUrlInput.value = '';
                if (ecCertUrlPreviewBox) ecCertUrlPreviewBox.style.display = 'none';
            }
        }

        // Reset the file input and previews
        const ecCertFileInputEl = document.getElementById('ec_cert_file_input');
        const ecCertPreviewBox = document.getElementById('ec_cert_preview_box');
        const ecCertImgPreview = document.getElementById('ec_cert_img_preview');
        const ecCertPdfPreview = document.getElementById('ec_cert_pdf_preview');
        const ecImageUploadWrap = document.getElementById('ec_cert_image_upload_wrap');
        const ecImageInput = document.getElementById('ec_cert_image_input');
        const ecImagePreviewBox = document.getElementById('ec_cert_image_preview_box');
        if (ecCertFileInputEl) ecCertFileInputEl.value = '';
        if (ecCertPreviewBox) ecCertPreviewBox.style.display = 'none';
        if (ecCertImgPreview) ecCertImgPreview.style.display = 'none';
        if (ecCertPdfPreview) ecCertPdfPreview.style.display = 'none';
        if (ecImageUploadWrap) ecImageUploadWrap.style.display = 'none';
        if (ecImageInput) { ecImageInput.required = false; ecImageInput.value = ''; }
        if (ecImagePreviewBox) ecImagePreviewBox.style.display = 'none';

        editCertModal.classList.add('active');
    });
});

if (closeEditCertBtn) {
    closeEditCertBtn.addEventListener('click', () => editCertModal.classList.remove('active'));
}

// ── Edit Certificate: file upload & URL input ──
const ecCertFileInput    = document.getElementById('ec_cert_file_input');
const ecPreviewUrlInput  = document.getElementById('ec_preview_image_url');
const ecCertPreviewBox   = document.getElementById('ec_cert_preview_box');
const ecCertImgPreview   = document.getElementById('ec_cert_img_preview');
const ecCertImgEl        = document.getElementById('ec_cert_img_el');
const ecCertImgName      = document.getElementById('ec_cert_img_name');
const ecCertPdfPreview   = document.getElementById('ec_cert_pdf_preview');
const ecCertPdfName      = document.getElementById('ec_cert_pdf_name');
const ecCertPdfSize      = document.getElementById('ec_cert_pdf_size');
const ecImageUploadWrap  = document.getElementById('ec_cert_image_upload_wrap');
const ecImageInput       = document.getElementById('ec_cert_image_input');
const ecImagePreviewBox  = document.getElementById('ec_cert_image_preview_box');
const ecImagePreviewEl   = document.getElementById('ec_cert_image_preview_el');
const ecCertUrlPreviewBox = document.getElementById('ec_cert_url_preview_box');
const ecCertUrlPreviewEl  = document.getElementById('ec_cert_url_preview_el');

function resetEcFilePreviews() {
    if (ecCertPreviewBox)  ecCertPreviewBox.style.display = 'none';
    if (ecCertImgPreview)  ecCertImgPreview.style.display = 'none';
    if (ecCertPdfPreview)  ecCertPdfPreview.style.display = 'none';
    if (ecImageUploadWrap) ecImageUploadWrap.style.display = 'none';
    if (ecImageInput)      { ecImageInput.required = false; ecImageInput.value = ''; }
    if (ecImagePreviewBox) ecImagePreviewBox.style.display = 'none';
}

if (ecCertFileInput) {
    ecCertFileInput.addEventListener('change', function() {
        // Clear URL input when a file is chosen
        if (ecPreviewUrlInput) { ecPreviewUrlInput.value = ''; }
        if (ecCertUrlPreviewBox) ecCertUrlPreviewBox.style.display = 'none';

        const file = this.files[0];
        if (!file) { resetEcFilePreviews(); return; }

        ecCertPreviewBox.style.display = 'block';
        const ext = file.name.split('.').pop().toLowerCase();

        if (['png','jpg','jpeg','webp'].includes(ext)) {
            ecCertPdfPreview.style.display = 'none';
            ecCertImgPreview.style.display = 'block';
            if (ecImageUploadWrap) ecImageUploadWrap.style.display = 'none';
            if (ecImageInput) { ecImageInput.required = false; ecImageInput.value = ''; }
            if (ecImagePreviewBox) ecImagePreviewBox.style.display = 'none';
            const reader = new FileReader();
            reader.onload = (e) => { ecCertImgEl.src = e.target.result; ecCertImgName.textContent = file.name; };
            reader.readAsDataURL(file);
        } else if (ext === 'pdf') {
            ecCertImgPreview.style.display = 'none';
            ecCertPdfPreview.style.display = 'flex';
            ecCertPdfName.textContent = file.name;
            const sizeKB = (file.size / 1024).toFixed(1);
            const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
            ecCertPdfSize.textContent = file.size > 1024 * 1024 ? `${sizeMB} MB` : `${sizeKB} KB`;
            // Show companion upload only when no URL given
            if (!ecPreviewUrlInput || !ecPreviewUrlInput.value.trim()) {
                if (ecImageUploadWrap) ecImageUploadWrap.style.display = 'block';
                if (ecImageInput) ecImageInput.required = true;
            }
        } else {
            resetEcFilePreviews();
        }
    });
}

// URL input → live preview + clear file
if (ecPreviewUrlInput) {
    ecPreviewUrlInput.addEventListener('input', function() {
        const url = this.value.trim();
        if (url) {
            if (ecCertFileInput) ecCertFileInput.value = '';
            resetEcFilePreviews();
            if (ecCertUrlPreviewBox) { ecCertUrlPreviewBox.style.display = 'block'; }
            if (ecCertUrlPreviewEl)  { ecCertUrlPreviewEl.src = url; }
        } else {
            if (ecCertUrlPreviewBox) ecCertUrlPreviewBox.style.display = 'none';
        }
    });
}

if (ecImageInput && ecImagePreviewBox) {
    ecImageInput.addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            ecImagePreviewBox.style.display = 'flex';
            const reader = new FileReader();
            reader.onload = (e) => { ecImagePreviewEl.src = e.target.result; };
            reader.readAsDataURL(file);
        } else {
            ecImagePreviewBox.style.display = 'none';
        }
    });
}

// ══════════════════════════════════════════════
// 7. EDIT PLATFORM MODAL
// ══════════════════════════════════════════════
const editPlatformModal = document.getElementById('editPlatformModal');
const closeEditPlatformBtn = document.getElementById('closeEditPlatformModal');
const editPlatformForm = document.getElementById('editPlatformForm');

document.querySelectorAll('.edit-platform-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const id = this.getAttribute('data-id');
        editPlatformForm.action = `/admin/edit-platform/${id}`;

        document.getElementById('ep_name').value = this.getAttribute('data-name') || '';
        document.getElementById('ep_url').value = this.getAttribute('data-url') || '';

        editPlatformModal.classList.add('active');
    });
});

if (closeEditPlatformBtn) {
    closeEditPlatformBtn.addEventListener('click', () => editPlatformModal.classList.remove('active'));
}

// ══════════════════════════════════════════════
// 8. CLOSE ALL MODALS ON OUTSIDE CLICK
// ══════════════════════════════════════════════
window.addEventListener('click', (e) => {
    if (e.target === editModal) editModal.classList.remove('active');
    if (e.target === editCertModal) editCertModal.classList.remove('active');
    if (e.target === editPlatformModal) editPlatformModal.classList.remove('active');
});
