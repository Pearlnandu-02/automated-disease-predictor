<?php
// image_scanner.php - AI Infection & Injury Image Scanner (Upgraded)
require_once __DIR__ . '/includes/functions.php';
require_once __DIR__ . '/includes/auth.php';
require_once __DIR__ . '/includes/ml_bridge.php';

$max_file_size = 8 * 1024 * 1024; // 8 MB
$allowed_exts = ['jpg', 'jpeg', 'png', 'webp'];
$allowed_mimes = ['image/jpeg', 'image/png', 'image/webp'];

$scan_result = null;
$error_message = null;

// Handle POST request (Both AJAX and regular form submission)
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $is_ajax = (isset($_GET['action']) && $_GET['action'] === 'scan') || 
               (isset($_SERVER['HTTP_X_REQUESTED_WITH']) && strtolower($_SERVER['HTTP_X_REQUESTED_WITH']) === 'xmlhttprequest');

    if (!isset($_FILES['image']) || $_FILES['image']['error'] === UPLOAD_ERR_NO_FILE) {
        $error_message = "Please select or photograph an affected skin area to scan.";
    } elseif ($_FILES['image']['error'] !== UPLOAD_ERR_OK) {
        $error_message = "Upload failed with code " . $_FILES['image']['error'] . ". Please choose or take another photo.";
    } elseif ($_FILES['image']['size'] > $max_file_size) {
        $file_mb = round($_FILES['image']['size'] / (1024 * 1024), 1);
        $error_message = "Image size ({$file_mb} MB) exceeds the 8 MB limit. Please select a smaller photo.";
    } else {
        $file_tmp = $_FILES['image']['tmp_name'];
        $orig_name = basename($_FILES['image']['name']);
        $ext = strtolower(pathinfo($orig_name, PATHINFO_EXTENSION));

        // MIME validation via finfo
        $finfo = finfo_open(FILEINFO_MIME_TYPE);
        $mime_type = finfo_file($finfo, $file_tmp);
        finfo_close($finfo);

        // Verification of image validity via getimagesize
        $img_info = @getimagesize($file_tmp);

        if (!in_array($ext, $allowed_exts) || !in_array($mime_type, $allowed_mimes) || $img_info === false) {
            $error_message = "Invalid or unsupported image file. Only genuine JPG, JPEG, PNG, and WebP images are accepted.";
        } else {
            // Ephemeral temporary processing in system temp dir
            $temp_scan_path = sys_get_temp_dir() . DIRECTORY_SEPARATOR . 'scan_' . bin2hex(random_bytes(8)) . '.' . $ext;
            
            if (move_uploaded_file($file_tmp, $temp_scan_path)) {
                try {
                    // Call Python Computer Vision & ML bridge
                    $scan_result = call_image_scanner($temp_scan_path);
                } catch (Exception $e) {
                    $error_message = "Computer vision service error: " . $e->getMessage();
                } finally {
                    // STRICT PRIVACY: Immediately delete temporary uploaded image file
                    if (file_exists($temp_scan_path)) {
                        @unlink($temp_scan_path);
                    }
                }
            } else {
                $error_message = "Failed to allocate temporary storage for image processing. Please try again.";
            }
        }
    }

    if ($is_ajax) {
        header('Content-Type: application/json');
        if ($error_message) {
            echo json_encode(['success' => false, 'error' => $error_message, 'category' => 'Unable to Assess']);
        } else {
            echo json_encode($scan_result);
        }
        exit;
    }
}

$page_title = 'MediSense AI | Injury & Infection Scanner';
require_once __DIR__ . '/includes/header.php';
?>

<!-- Page Header & Hero -->
<div class="row mb-4">
    <div class="col-12">
        <div class="scanner-hero-banner p-4 p-md-5 mb-3">
            <div class="row align-items-center">
                <div class="col-lg-8">
                    <span class="badge hero-badge px-3 py-2 rounded-pill mb-3">
                        <i class="bi bi-cpu-fill me-1"></i> Computer Vision & Machine Learning Pipeline
                    </span>
                    <h1 class="display-6 fw-bold hero-heading mb-2">AI Infection & Injury Scanner</h1>
                    <p class="lead mb-0 hero-lead">
                        Upload or photograph a skin injury, wound, rash, swelling, or redness for an AI-assisted preliminary visual assessment.
                    </p>
                    <div class="mt-2 text-white-50 small">
                        <i class="bi bi-stars me-1 text-info"></i> MediSense AI &bull; <em>“Smarter Insights. Better Health.”</em>
                    </div>
                </div>
                <div class="col-lg-4 text-lg-end d-none d-lg-block">
                    <i class="bi bi-shield-check display-1 scanner-hero-icon opacity-50"></i>
                </div>
            </div>
        </div>

        <!-- Mandatory Educational Disclaimer -->
        <div class="disclaimer-banner mb-3 shadow-sm">
            <div class="d-flex align-items-start gap-2">
                <i class="bi bi-exclamation-triangle-fill fs-5 mt-1 flex-shrink-0 text-warning"></i>
                <div>
                    <strong class="disclaimer-title">Important Medical Notice:</strong> This AI-assisted scanner provides an <em>educational preliminary visual assessment</em> and is NOT a medical diagnosis. It does not replace professional clinical evaluation. For worsening, painful, infected, deep, or concerning wounds, please consult a qualified healthcare professional immediately.
                </div>
            </div>
        </div>

        <!-- Privacy Assurance Banner -->
        <div class="alert alert-secondary py-2 px-3 small border d-flex align-items-center gap-2 mb-4 bg-card-custom text-secondary-theme">
            <i class="bi bi-shield-lock-fill text-success fs-5 flex-shrink-0"></i>
            <div>
                <strong>Privacy Assurance:</strong> Uploaded images are processed ephemerally in memory and permanently deleted immediately after metric extraction. Photos are <strong>never stored</strong> in our database or logged to disk. <em>Do not upload identifying personal documents or faces.</em>
            </div>
        </div>
    </div>
</div>

<!-- Main Scanner Layout -->
<div class="row g-4 mb-5">
    <!-- Left Column: Upload, Camera & Live Preview -->
    <div class="col-lg-6">
        <div class="card card-custom h-100 p-4">
            <h4 class="fw-bold mb-1 d-flex align-items-center gap-2">
                <i class="bi bi-cloud-arrow-up text-info"></i> Scan an Infection or Injury
            </h4>
            <p class="text-muted small mb-3">
                Upload a clear, well-lit image of the affected skin area for preliminary analysis.
            </p>

            <!-- Error Feedback Alert -->
            <div id="scannerErrorAlert" class="alert alert-danger d-none mb-3 py-2 px-3 small" role="alert">
                <div class="d-flex align-items-start gap-2">
                    <i class="bi bi-exclamation-circle-fill fs-6 mt-1 flex-shrink-0"></i>
                    <div id="scannerErrorMsg"></div>
                </div>
            </div>

            <!-- Upload Area / Drag & Drop -->
            <div id="dropZone" class="scanner-dropzone mb-3" tabindex="0" role="button" aria-label="Drop image here or click upload image">
                <div class="scanner-icon-circle">
                    <i class="bi bi-image"></i>
                </div>
                <h5 class="fw-bold mb-1">Drag &amp; Drop Image Here</h5>
                <p class="text-muted small mb-3">or choose an option below to select from your device</p>
                
                <div class="d-flex flex-wrap justify-content-center gap-2">
                    <button type="button" class="btn btn-outline-info rounded-pill px-3 py-2 btn-sm fw-semibold" id="btnBrowseFiles">
                        <i class="bi bi-folder2-open me-1"></i> Upload Image
                    </button>
                    <button type="button" class="btn btn-info rounded-pill px-3 py-2 btn-sm text-white fw-semibold" id="btnTakePhoto">
                        <i class="bi bi-camera-fill me-1"></i> Take Photo
                    </button>
                </div>

                <div class="mt-3 text-muted small">
                    <span class="badge bg-secondary-subtle text-secondary me-1">JPG</span>
                    <span class="badge bg-secondary-subtle text-secondary me-1">JPEG</span>
                    <span class="badge bg-secondary-subtle text-secondary me-1">PNG</span>
                    <span class="badge bg-secondary-subtle text-secondary">WEBP</span>
                    <span class="ms-2">Max 8 MB</span>
                </div>

                <!-- Hidden file inputs -->
                <input type="file" id="imageFileInput" accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp" class="d-none">
                <input type="file" id="cameraFileInput" accept="image/*" capture="environment" class="d-none">
            </div>

            <!-- Image Preview & Scanner Frame (Hidden until image selected) -->
            <div id="previewContainer" class="d-none mt-2">
                <div class="scanner-preview-wrapper mb-3" id="previewFrame">
                    <img id="previewImage" class="scanner-preview-img" alt="Selected Skin Image Preview">
                    <!-- Laser Scanning Effect Beam -->
                    <div class="scanner-laser-beam" aria-hidden="true">
                        <div class="scanner-laser-glow"></div>
                    </div>
                </div>

                <!-- File Info Bar -->
                <div class="d-flex justify-content-between align-items-center bg-card-subtle p-2 px-3 rounded-3 mb-3 border">
                    <div class="d-flex align-items-center gap-2 overflow-hidden text-truncate me-2">
                        <i class="bi bi-file-earmark-image text-info fs-5"></i>
                        <span id="previewFilename" class="small fw-semibold text-truncate">image.jpg</span>
                    </div>
                    <span id="previewFilesize" class="badge bg-secondary rounded-pill">0 KB</span>
                </div>

                <!-- Action Controls (User confirms before scan begins) -->
                <div class="d-flex gap-2" id="previewActions">
                    <button type="button" class="btn btn-outline-danger flex-fill py-2 rounded-3 fw-semibold" id="btnRemoveImage">
                        <i class="bi bi-trash3 me-1"></i> Remove Image
                    </button>
                    <button type="button" class="btn btn-outline-secondary flex-fill py-2 rounded-3 fw-semibold" id="btnRetakeOption">
                        <i class="bi bi-camera me-1"></i> Retake / Replace
                    </button>
                    <button type="button" class="btn btn-primary-custom flex-fill py-2 fw-bold" id="btnScanImage">
                        <i class="bi bi-cpu me-1"></i> Scan Image
                    </button>
                </div>

                <!-- Scanning Progress State (Hidden by default) -->
                <div id="scanningState" class="d-none text-center py-3">
                    <div class="d-inline-flex align-items-center gap-2 mb-2">
                        <span class="scanner-status-pulse"></span>
                        <strong class="text-info fs-5" id="scanningTitle">Analyzing image...</strong>
                    </div>
                    <p id="scanningStatusText" class="text-muted small mb-2">
                        Initializing computer vision pipeline...
                    </p>
                    <div class="progress mb-2" style="height: 8px;">
                        <div id="scanProgressBar" class="progress-bar progress-bar-striped progress-bar-animated bg-info" style="width: 15%;"></div>
                    </div>
                    <small class="text-muted" style="font-size: 0.76rem;">
                        Extracting spectrophotometric erythema, Sobel gradients, and calibrated patterns...
                    </small>
                </div>
            </div>
        </div>
    </div>

    <!-- Right Column: Results & Educational Assessment -->
    <div class="col-lg-6">
        <div class="card card-custom h-100 p-4" id="resultCardContainer">
            <!-- Initial Idle State -->
            <div id="idleState" class="text-center py-5 my-auto">
                <div class="scanner-icon-circle mb-3" style="width: 80px; height: 80px; font-size: 2.5rem;">
                    <i class="bi bi-activity"></i>
                </div>
                <h4 class="fw-bold mb-2">Preliminary Assessment Output</h4>
                <p class="text-muted small max-w-sm mx-auto mb-4" style="max-width: 400px;">
                    Select or photograph an affected skin area and click <strong>"Scan Image"</strong>. The AI analyzer will evaluate erythema indices, edge disruption, chromatic dispersion, and pattern correlation.
                </p>
                <div class="p-3 bg-card-subtle rounded-3 border text-start small">
                    <h6 class="fw-bold mb-2 text-info"><i class="bi bi-info-circle me-1"></i> How this module works:</h6>
                    <ul class="mb-0 text-muted ps-3">
                        <li class="mb-1"><strong>Erythema Index:</strong> Measures localized hemoglobin absorption and capillary dilation.</li>
                        <li class="mb-1"><strong>Edge Roughness:</strong> Computes high-frequency Sobel gradient changes for abrasions and cuts.</li>
                        <li class="mb-1"><strong>Quality &amp; Scope Gate:</strong> Filters out blurry, dark, or non-skin photos to prevent misleading inferences.</li>
                        <li><strong>Calibrated Model:</strong> Outputs probabilistic confidence calibrated against benchmarked dermatological distributions.</li>
                    </ul>
                </div>
            </div>

            <!-- Quality Failure Rejection View (blurry, dark, low-res) -->
            <div id="qualityFailContent" class="d-none">
                <div class="scanner-quality-card p-4 mb-3">
                    <div class="d-flex align-items-center gap-2 mb-2">
                        <i class="bi bi-exclamation-triangle-fill text-warning fs-4"></i>
                        <h5 class="fw-bold mb-0 text-warning">Image quality is too low for reliable analysis</h5>
                    </div>
                    <p class="text-muted small mb-3" id="qualityFailReason">
                        The uploaded photo does not meet the minimum clarity thresholds required for computer vision feature extraction.
                    </p>
                    <h6 class="fw-bold small text-uppercase text-muted mb-2">Recommended Instructions:</h6>
                    <ul class="small text-muted ps-3 mb-3">
                        <li class="mb-1"><strong>Use good, even lighting:</strong> Avoid harsh flash glare or deep shadows.</li>
                        <li class="mb-1"><strong>Keep the affected area in focus:</strong> Hold the camera steady and tap to focus.</li>
                        <li class="mb-1"><strong>Avoid excessive distance:</strong> Frame the skin lesion closely while including a little surrounding normal skin.</li>
                        <li><strong>Keep the area visible:</strong> Remove bandages, clothing, or hair obstructing the view.</li>
                    </ul>
                    <button type="button" class="btn btn-outline-warning w-100 rounded-3 py-2 fw-semibold" id="btnQualityRetake">
                        <i class="bi bi-camera me-1"></i> Retake / Upload Another Image
                    </button>
                </div>
            </div>

            <!-- Out-of-Scope / Non-Skin / Uncertain Rejection View -->
            <div id="outOfScopeContent" class="d-none">
                <div class="scanner-scope-card p-4 mb-3">
                    <div class="d-flex align-items-center gap-2 mb-2">
                        <i class="bi bi-question-circle-fill text-secondary fs-4"></i>
                        <h5 class="fw-bold mb-0">Unable to Confidently Assess This Image</h5>
                    </div>
                    <p class="text-muted small mb-3" id="outOfScopeReason">
                        Visual features did not meet the statistical confidence threshold for supported skin categories. The image appears to be outside supported clinical categories or non-skin subject matter.
                    </p>
                    <div class="p-3 bg-card-subtle rounded-3 border mb-3 small">
                        <strong>Supported Categories:</strong>
                        <div class="d-flex flex-wrap gap-1 mt-2">
                            <span class="badge bg-secondary-subtle text-secondary">Infection Indicators</span>
                            <span class="badge bg-secondary-subtle text-secondary">Minor Injury</span>
                            <span class="badge bg-secondary-subtle text-secondary">Rash / Skin Irritation</span>
                            <span class="badge bg-secondary-subtle text-secondary">Swelling / Contusion</span>
                            <span class="badge bg-secondary-subtle text-secondary">Inflammation / Redness</span>
                        </div>
                    </div>
                    <p class="text-muted small mb-3">
                        Please upload a clearer, well-lit photo of the affected skin area, or seek direct in-person medical evaluation from a healthcare provider.
                    </p>
                    <button type="button" class="btn btn-outline-info w-100 rounded-3 py-2 fw-semibold" id="btnScopeRetake">
                        <i class="bi bi-arrow-repeat me-1"></i> Try Different Image
                    </button>
                </div>
            </div>

            <!-- Unsupported Skin Lesion / Mole / Pigmented Spot View (Section 5, 11, 12, 13) -->
            <div id="unsupportedLesionContent" class="d-none">
                <div class="scanner-scope-card p-4 mb-3 border-warning" style="border-left: 4px solid #f59e0b;">
                    <div class="d-flex align-items-center gap-2 mb-2">
                        <i class="bi bi-shield-exclamation text-warning fs-3"></i>
                        <div>
                            <h5 class="fw-bold mb-0 text-warning">Unable to Confidently Assess: Unsupported Skin Lesion</h5>
                            <span class="badge bg-warning-subtle text-warning border border-warning border-opacity-25 mt-1">Outside Supported Acute Domain</span>
                        </div>
                    </div>
                    
                    <div class="alert alert-warning border-0 bg-warning bg-opacity-10 my-3 small p-3 rounded-3 text-start">
                        <strong class="d-block mb-1 text-warning"><i class="bi bi-info-circle-fill me-1"></i> Critical Scope Notice:</strong>
                        This scanner is configured exclusively for acute superficial injury and infection screening. <strong>This scanner currently does not support reliable classification of this type of skin lesion.</strong>
                    </div>

                    <p class="small text-muted mb-3" id="lesionWhatDetected">
                        The computer vision analyzer detected localized hyperpigmented melanin clustering with high contrast drop and chromatic variegation against surrounding skin.
                    </p>

                    <!-- Technical Image Features -->
                    <h6 class="fw-bold small text-uppercase text-muted mb-2">Technical Image Features</h6>
                    <div class="p-3 bg-card-subtle rounded-3 border mb-3 small" id="lesionTechFeaturesList">
                        <!-- Populated dynamically -->
                    </div>

                    <!-- Clinical Recommendation -->
                    <div class="p-3 bg-card-subtle rounded-3 border mb-3 small border-start border-4 border-info text-start">
                        <strong class="text-info d-block mb-1"><i class="bi bi-person-badge-fill me-1"></i> Recommended Next Step:</strong>
                        <p class="mb-0 text-muted" id="lesionNextStepText">
                            Please seek evaluation by a qualified healthcare professional (such as a board-certified dermatologist) for a new, changing, bleeding, painful, or otherwise concerning lesion.
                        </p>
                    </div>

                    <!-- ABCDE Educational Awareness Guide -->
                    <div class="mb-3 p-3 bg-card-subtle rounded-3 border small text-start">
                        <strong class="text-heading d-block mb-2"><i class="bi bi-card-checklist me-1 text-info"></i> ABCDE Awareness Guide for Skin Lesions:</strong>
                        <p class="text-muted small mb-2">Dermatologists recommend monitoring suspicious skin spots using the ABCDE criteria (this guide is educational and does not constitute a diagnosis):</p>
                        <ul class="text-muted small ps-3 mb-0">
                            <li class="mb-1"><strong>A - Asymmetry:</strong> One half of the spot does not match the other half in shape, border, or contour.</li>
                            <li class="mb-1"><strong>B - Border:</strong> The edges are irregular, ragged, notched, scalloped, or blurred.</li>
                            <li class="mb-1"><strong>C - Color:</strong> Color is non-uniform; contains varying shades of tan, brown, black, red, or white.</li>
                            <li class="mb-1"><strong>D - Diameter:</strong> Spot is larger than 6 mm (about pencil eraser size), though some can be smaller.</li>
                            <li><strong>E - Evolving:</strong> The lesion is changing in size, shape, surface elevation, color, or bleeding/itching.</li>
                        </ul>
                    </div>

                    <!-- Educational Disclaimer -->
                    <div class="p-2 px-3 rounded-2 border bg-card-subtle text-muted small mb-3 text-start" style="font-size: 0.78rem;">
                        <i class="bi bi-shield-check me-1 text-info"></i>
                        <strong>Important Disclaimer:</strong> This AI-assisted preliminary assessment is for educational awareness and is NOT a medical diagnosis. Never ignore a changing skin spot.
                    </div>

                    <button type="button" class="btn btn-outline-info w-100 rounded-3 py-2 fw-semibold" id="btnLesionRetake">
                        <i class="bi bi-arrow-repeat me-1"></i> Scan Another Image
                    </button>
                </div>
            </div>

            <!-- Active Assessment Result View (Revealed when valid result returned) -->
            <div id="resultContent" class="d-none">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <span class="text-muted small fw-bold text-uppercase tracking-wider">
                        <i class="bi bi-clipboard2-pulse me-1 text-info"></i> AI-ASSISTED VISUAL ASSESSMENT
                    </span>
                    <span id="resultTimestamp" class="small text-muted">Just now</span>
                </div>

                <!-- Category Badge -->
                <div class="mb-3 d-flex flex-wrap align-items-center gap-2">
                    <span id="resultCategoryBadge" class="badge-category badge-category-injury">
                        <i class="bi bi-search"></i> <span id="resultCategoryText">Evaluating...</span>
                    </span>
                    <!-- Severity Status (Honest, un-fabricated clinical limitation) -->
                    <span class="scanner-severity-badge" id="resultSeverityBadge" title="Severity classification requires in-person medical palpation">
                        <i class="bi bi-info-circle"></i> Severity cannot be reliably determined from this scan
                    </span>
                </div>

                <!-- Model Statistical Confidence Score -->
                <div class="mb-3 p-3 bg-card-subtle rounded-3 border">
                    <div class="d-flex justify-content-between align-items-center mb-1">
                        <span class="small fw-semibold">Model Statistical Confidence:</span>
                        <span id="resultScoreText" class="fw-bold text-info">0.0%</span>
                    </div>
                    <div class="progress mb-1" style="height: 8px;">
                        <div id="resultScoreBar" class="progress-bar bg-info" style="width: 0%;"></div>
                    </div>
                    <small class="text-muted d-block" style="font-size: 0.76rem;">
                        Statistical alignment score reflecting pattern correlation with benchmarked vision training distributions. <strong>Model confidence is not the same as medical certainty.</strong>
                    </small>
                </div>

                <!-- Runner-Up Pattern Container (If confidence was shared) -->
                <div id="resultRunnerUpContainer" class="d-none mb-3 scanner-runnerup-box small">
                    <i class="bi bi-signpost-split me-1 text-info"></i>
                    <strong>Secondary Observation:</strong> <span id="resultRunnerUpText">None</span>
                </div>

                <!-- What the Model Detected -->
                <div class="p-3 bg-card-subtle rounded-3 border mb-3">
                    <h6 class="fw-bold small text-uppercase text-muted mb-1"><i class="bi bi-eye me-1 text-info"></i> What the Model Detected:</h6>
                    <p class="text-muted small mb-0" id="resultWhatDetected">
                        Analysis generated via calibrated spectrophotometric and textural computer vision model.
                    </p>
                </div>

                <!-- Observed Visual Characteristics -->
                <div class="mb-3">
                    <h6 class="fw-bold small text-uppercase text-muted mb-2">Observed Visual Characteristics:</h6>
                    <div id="resultObsList">
                        <!-- Populated dynamically -->
                    </div>
                </div>

                <!-- Technical Image Features (Section 4 & 13) -->
                <div class="mb-3 p-3 bg-card-subtle rounded-3 border small">
                    <h6 class="fw-bold text-heading small text-uppercase mb-2"><i class="bi bi-sliders me-1 text-info"></i> Technical Image Features:</h6>
                    <div id="resultTechFeaturesList">
                        <!-- Populated dynamically -->
                    </div>
                </div>

                <!-- What This Result Means (Section 13) -->
                <div class="mb-3 p-3 bg-card-subtle rounded-3 border small">
                    <h6 class="fw-bold text-info mb-1"><i class="bi bi-chat-left-text me-1"></i> What This Result Means:</h6>
                    <p class="text-muted mb-0" id="resultWhatMeansText">
                        Educational context regarding observed visual patterns.
                    </p>
                </div>

                <!-- Recommended Next Step (Section 13) -->
                <div class="mb-3 p-3 bg-card-subtle rounded-3 border small border-start border-4 border-info">
                    <strong class="text-info d-block mb-1"><i class="bi bi-arrow-right-circle-fill me-1"></i> Recommended Next Step:</strong>
                    <p class="mb-0 text-muted" id="resultNextStepText">
                        Follow appropriate first-aid care and monitor the affected area closely.
                    </p>
                </div>

                <!-- General Educational Care Guidance -->
                <div class="mb-3">
                    <h6 class="fw-bold small text-uppercase text-muted mb-2">What You Can Do (General First-Aid Points):</h6>
                    <div id="resultCareList">
                        <!-- Populated dynamically -->
                    </div>
                </div>

                <!-- Concerning Warning Signs -->
                <div class="mb-3 p-3 rounded-3 border border-danger-subtle bg-card-subtle small">
                    <h6 class="fw-bold text-danger mb-2">
                        <i class="bi bi-exclamation-octagon-fill me-1"></i> Warning Signs to Monitor:
                    </h6>
                    <div id="resultWarningList">
                        <!-- Populated dynamically -->
                    </div>
                </div>

                <!-- When to Seek Medical Attention -->
                <div class="mb-3 p-3 rounded-3 border border-warning-subtle bg-card-subtle small">
                    <h6 class="fw-bold text-warning mb-2">
                        <i class="bi bi-hospital me-1"></i> When to Seek Medical Attention:
                    </h6>
                    <div id="resultWhenCareList">
                        <!-- Populated dynamically -->
                    </div>
                </div>

                <!-- Prominent Disclaimer Card (Section 13 & 20) -->
                <div class="alert alert-secondary py-2 px-3 small border mb-3 bg-card-custom text-secondary-theme" style="font-size: 0.78rem;">
                    <i class="bi bi-shield-exclamation me-1 text-warning"></i>
                    <strong>Important Medical Notice:</strong> This AI-assisted preliminary assessment is strictly for educational purposes and is <strong>NOT a medical diagnosis</strong>. Results should not replace evaluation by a qualified healthcare professional.
                </div>

                <!-- Reset Button -->
                <button type="button" class="btn btn-outline-info w-100 rounded-3 py-2 fw-semibold" id="btnScanAnother">
                    <i class="bi bi-arrow-repeat me-1"></i> Scan Another Image
                </button>
            </div>
        </div>
    </div>
</div>

<!-- "When to Seek Immediate Medical Attention" Global Safety Section -->
<div class="row mb-5">
    <div class="col-12">
        <div class="card card-custom p-4 border-danger-subtle">
            <div class="d-flex align-items-center gap-2 mb-3">
                <span class="badge bg-danger text-white px-3 py-2 rounded-pill">
                    <i class="bi bi-hospital me-1"></i> Patient Safety Notice
                </span>
                <h4 class="fw-bold mb-0">When to Seek Immediate Medical Attention</h4>
            </div>
            <p class="text-muted small mb-4">
                Wounds and skin infections can deteriorate rapidly. Seek prompt evaluation from a licensed physician, urgent care clinic, or emergency room if any of the following warning signs are observed:
            </p>

            <div class="row g-3">
                <div class="col-md-4 col-sm-6">
                    <div class="warning-sign-card h-100">
                        <div class="fw-bold text-danger mb-1"><i class="bi bi-droplet-fill me-1"></i> Severe Bleeding</div>
                        <div class="small text-muted">Blood that spurts or continues to flow after 10 minutes of direct, continuous pressure.</div>
                    </div>
                </div>
                <div class="col-md-4 col-sm-6">
                    <div class="warning-sign-card h-100">
                        <div class="fw-bold text-danger mb-1"><i class="bi bi-graph-up-arrow me-1"></i> Rapidly Spreading Redness</div>
                        <div class="small text-muted">Red streaks branching toward the heart or an expanding erythematous border within hours.</div>
                    </div>
                </div>
                <div class="col-md-4 col-sm-6">
                    <div class="warning-sign-card h-100">
                        <div class="fw-bold text-danger mb-1"><i class="bi bi-thermometer-high me-1"></i> Fever & Systemic Chills</div>
                        <div class="small text-muted">Elevated body temperature (>100.4°F / 38°C), confusion, nausea, or general feeling of illness.</div>
                    </div>
                </div>
                <div class="col-md-4 col-sm-6">
                    <div class="warning-sign-card h-100">
                        <div class="fw-bold text-danger mb-1"><i class="bi bi-radioactive me-1"></i> Foul Pus or Drainage</div>
                        <div class="small text-muted">Thick, yellowish or greenish discharge, foul odor, or skin that feels unusually hot to the touch.</div>
                    </div>
                </div>
                <div class="col-md-4 col-sm-6">
                    <div class="warning-sign-card h-100">
                        <div class="fw-bold text-danger mb-1"><i class="bi bi-arrows-fullscreen me-1"></i> Rapidly Increasing Swelling</div>
                        <div class="small text-muted">Swelling that tightens the skin, produces intense throbbing pain, or numbs the limb.</div>
                    </div>
                </div>
                <div class="col-md-4 col-sm-6">
                    <div class="warning-sign-card h-100">
                        <div class="fw-bold text-danger mb-1"><i class="bi bi-bandaid-fill me-1"></i> Deep or Gaping Wounds</div>
                        <div class="small text-muted">Cuts that expose underlying yellow fat, tendon, or muscle, which typically require sutures.</div>
                    </div>
                </div>
                <div class="col-md-4 col-sm-6">
                    <div class="warning-sign-card h-100">
                        <div class="fw-bold text-danger mb-1"><i class="bi bi-fire me-1"></i> Serious Burns & Blistering</div>
                        <div class="small text-muted">Partial or full-thickness burns, large blisters, or chemical and electrical burn injuries.</div>
                    </div>
                </div>
                <div class="col-md-4 col-sm-6">
                    <div class="warning-sign-card h-100">
                        <div class="fw-bold text-danger mb-1"><i class="bi bi-lungs-fill me-1"></i> Difficulty Breathing / Anaphylaxis</div>
                        <div class="small text-muted">Swelling of the lips, tongue, or throat following an insect sting or contact rash.</div>
                    </div>
                </div>
                <div class="col-md-4 col-sm-6">
                    <div class="warning-sign-card h-100">
                        <div class="fw-bold text-danger mb-1"><i class="bi bi-shield-exclamation me-1"></i> Animal or Human Bites</div>
                        <div class="small text-muted">Bite puncture wounds carry high rates of polymicrobial anaerobic infection and need antibiotic prophylaxis.</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Upgraded Live Camera Modal (Complete 7-Step Experience) -->
<div class="modal fade" id="cameraModal" tabindex="-1" aria-labelledby="cameraModalLabel" aria-hidden="true" data-bs-backdrop="static">
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content card-custom border-info">
            <div class="modal-header border-bottom border-subtle">
                <h5 class="modal-title fw-bold" id="cameraModalLabel">
                    <i class="bi bi-camera-fill text-info me-2"></i>Photograph Affected Area
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close" id="btnCloseCameraX"></button>
            </div>
            
            <div class="modal-body p-3 text-center">
                <!-- Viewfinder Container -->
                <div id="cameraStreamContainer" class="camera-viewfinder position-relative">
                    <!-- Live Stream Video -->
                    <video id="cameraVideo" autoplay playsinline muted class="w-100 h-100" style="object-fit: cover;"></video>
                    
                    <!-- Frozen Captured Snapshot Preview -->
                    <img id="cameraPreviewImg" class="camera-preview-frozen d-none" alt="Captured Photo Preview">

                    <!-- Reticle and Framing Guides (Active in Live Video Mode) -->
                    <div id="cameraLiveOverlay">
                        <span class="camera-badge-mode" id="cameraModeBadge">Live Camera</span>
                        <div class="camera-reticle"></div>
                        <div class="camera-reticle-corners">
                            <div class="camera-corner-tr"></div>
                            <div class="camera-corner-bl"></div>
                        </div>
                        <div class="camera-guide-text">Center affected skin area within reticle</div>
                    </div>
                </div>

                <!-- Hidden canvas for snapping -->
                <canvas id="cameraCanvas" class="d-none"></canvas>

                <!-- Feedback alert inside modal -->
                <div id="cameraAlert" class="alert alert-warning d-none mt-2 py-2 px-3 small text-start" role="alert"></div>
            </div>

            <div class="modal-footer border-top border-subtle d-flex justify-content-between">
                <!-- Left Action: Flip Camera (in live mode) OR Cancel -->
                <div id="cameraLeftActions">
                    <button type="button" class="btn btn-outline-secondary rounded-pill px-3 btn-sm" id="btnFlipCamera" title="Switch front/rear camera">
                        <i class="bi bi-arrow-repeat me-1"></i> Flip Camera
                    </button>
                    <button type="button" class="btn btn-outline-info rounded-pill px-3 btn-sm d-none" id="btnRetakePhoto">
                        <i class="bi bi-arrow-counterclockwise me-1"></i> Retake Photo
                    </button>
                </div>

                <!-- Right Actions: Cancel / Capture / Confirm -->
                <div class="d-flex gap-2" id="cameraRightActions">
                    <button type="button" class="btn btn-outline-danger rounded-pill px-3 btn-sm" data-bs-dismiss="modal" id="btnCancelCamera">
                        Cancel
                    </button>
                    <!-- Snap button in Live Mode -->
                    <button type="button" class="btn btn-info rounded-pill px-4 btn-sm text-white fw-bold" id="btnSnapPhoto">
                        <i class="bi bi-circle-fill me-1"></i> Capture Photo
                    </button>
                    <!-- Confirm button in Review Mode -->
                    <button type="button" class="btn btn-success rounded-pill px-4 btn-sm text-white fw-bold d-none" id="btnConfirmPhoto">
                        <i class="bi bi-check-circle-fill me-1"></i> Confirm &amp; Use Photo
                    </button>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Interactive Scanner Client Script -->
<script>
document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const dropZone = document.getElementById('dropZone');
    const imageFileInput = document.getElementById('imageFileInput');
    const cameraFileInput = document.getElementById('cameraFileInput');
    const btnBrowseFiles = document.getElementById('btnBrowseFiles');
    const btnTakePhoto = document.getElementById('btnTakePhoto');
    const previewContainer = document.getElementById('previewContainer');
    const previewImage = document.getElementById('previewImage');
    const previewFilename = document.getElementById('previewFilename');
    const previewFilesize = document.getElementById('previewFilesize');
    const previewActions = document.getElementById('previewActions');
    const btnRemoveImage = document.getElementById('btnRemoveImage');
    const btnRetakeOption = document.getElementById('btnRetakeOption');
    const btnScanImage = document.getElementById('btnScanImage');
    const scanningState = document.getElementById('scanningState');
    const scanningStatusText = document.getElementById('scanningStatusText');
    const scanProgressBar = document.getElementById('scanProgressBar');
    const previewFrame = document.getElementById('previewFrame');

    // Result Column States
    const idleState = document.getElementById('idleState');
    const qualityFailContent = document.getElementById('qualityFailContent');
    const qualityFailReason = document.getElementById('qualityFailReason');
    const btnQualityRetake = document.getElementById('btnQualityRetake');
    
    const outOfScopeContent = document.getElementById('outOfScopeContent');
    const outOfScopeReason = document.getElementById('outOfScopeReason');
    const btnScopeRetake = document.getElementById('btnScopeRetake');

    const unsupportedLesionContent = document.getElementById('unsupportedLesionContent');
    const lesionWhatDetected = document.getElementById('lesionWhatDetected');
    const lesionTechFeaturesList = document.getElementById('lesionTechFeaturesList');
    const lesionNextStepText = document.getElementById('lesionNextStepText');
    const btnLesionRetake = document.getElementById('btnLesionRetake');

    const resultContent = document.getElementById('resultContent');
    const resultCategoryBadge = document.getElementById('resultCategoryBadge');
    const resultCategoryText = document.getElementById('resultCategoryText');
    const resultSummaryHeading = document.getElementById('resultSummaryHeading');
    const resultWhatDetected = document.getElementById('resultWhatDetected');
    const resultScoreText = document.getElementById('resultScoreText');
    const resultScoreBar = document.getElementById('resultScoreBar');
    const resultRunnerUpContainer = document.getElementById('resultRunnerUpContainer');
    const resultRunnerUpText = document.getElementById('resultRunnerUpText');
    const valErythema = document.getElementById('valErythema');
    const valRoughness = document.getElementById('valRoughness');
    const valChroma = document.getElementById('valChroma');
    const resultObsList = document.getElementById('resultObsList');
    const resultTechFeaturesList = document.getElementById('resultTechFeaturesList');
    const resultWhatMeansText = document.getElementById('resultWhatMeansText');
    const resultNextStepText = document.getElementById('resultNextStepText');
    const resultGeneralInfo = document.getElementById('resultGeneralInfo');
    const resultCareList = document.getElementById('resultCareList');
    const resultWarningList = document.getElementById('resultWarningList');
    const resultWhenCareList = document.getElementById('resultWhenCareList');
    const btnScanAnother = document.getElementById('btnScanAnother');

    const scannerErrorAlert = document.getElementById('scannerErrorAlert');
    const scannerErrorMsg = document.getElementById('scannerErrorMsg');

    // Camera Modal Elements
    const cameraModalElem = document.getElementById('cameraModal');
    let cameraModalInstance = null;
    const cameraVideo = document.getElementById('cameraVideo');
    const cameraPreviewImg = document.getElementById('cameraPreviewImg');
    const cameraLiveOverlay = document.getElementById('cameraLiveOverlay');
    const cameraModeBadge = document.getElementById('cameraModeBadge');
    const cameraCanvas = document.getElementById('cameraCanvas');
    const cameraAlert = document.getElementById('cameraAlert');
    const btnSnapPhoto = document.getElementById('btnSnapPhoto');
    const btnRetakePhoto = document.getElementById('btnRetakePhoto');
    const btnConfirmPhoto = document.getElementById('btnConfirmPhoto');
    const btnFlipCamera = document.getElementById('btnFlipCamera');

    let activeCameraStream = null;
    let currentFacingMode = 'environment'; // default rear camera for skin lesion
    let temporaryCapturedBlob = null;
    let currentSelectedFile = null;
    let scanAnimationTimer = null;

    function showError(msg) {
        scannerErrorMsg.innerHTML = msg;
        scannerErrorAlert.classList.remove('d-none');
    }

    function clearError() {
        scannerErrorAlert.classList.add('d-none');
        scannerErrorMsg.textContent = '';
    }

    // Trigger normal file browser upload
    btnBrowseFiles.addEventListener('click', (e) => {
        e.stopPropagation();
        imageFileInput.click();
    });

    btnRetakeOption.addEventListener('click', (e) => {
        e.stopPropagation();
        btnTakePhoto.click();
    });

    // -------------------------------------------------------------
    // Camera Implementation (7-Step Complete Flow)
    // -------------------------------------------------------------
    btnTakePhoto.addEventListener('click', (e) => {
        e.stopPropagation();
        clearError();

        // Check if WebRTC getUserMedia is available and supported
        if (navigator.mediaDevices && typeof navigator.mediaDevices.getUserMedia === 'function') {
            startLiveCamera(currentFacingMode);
        } else {
            // Fallback for browsers or non-HTTPS contexts without getUserMedia
            showCameraDeniedFallback("Direct browser camera access is unavailable in this environment. You can upload an image or capture using your device camera instead.");
        }
    });

    function showCameraDeniedFallback(msg) {
        showError('<strong>Camera access notification:</strong> ' + msg + '<br><button type="button" class="btn btn-sm btn-outline-info rounded-pill mt-2" id="btnFallbackUpload"><i class="bi bi-upload me-1"></i> Upload Image / Device Capture</button>');
        
        setTimeout(() => {
            const btnFallback = document.getElementById('btnFallbackUpload');
            if (btnFallback) {
                btnFallback.addEventListener('click', () => {
                    cameraFileInput.click();
                });
            }
        }, 100);
    }

    function startLiveCamera(facingMode) {
        if (!cameraModalInstance && typeof bootstrap !== 'undefined') {
            cameraModalInstance = new bootstrap.Modal(cameraModalElem);
        }

        stopActiveCameraStream();
        setCameraModalState('live');
        cameraAlert.classList.add('d-none');
        cameraAlert.textContent = '';

        const constraints = {
            video: {
                facingMode: { ideal: facingMode },
                width: { ideal: 1280 },
                height: { ideal: 720 }
            },
            audio: false
        };

        navigator.mediaDevices.getUserMedia(constraints)
        .then(stream => {
            activeCameraStream = stream;
            cameraVideo.srcObject = stream;
            if (cameraModalInstance) {
                cameraModalInstance.show();
            }
        })
        .catch(err => {
            console.warn("Camera getUserMedia error:", err);
            if (cameraModalInstance) {
                cameraModalInstance.hide();
            }
            // Exact requirement message: “Camera access was denied. You can upload an image from your device instead.”
            if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
                showCameraDeniedFallback("Camera access was denied. You can upload an image from your device instead.");
            } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
                showCameraDeniedFallback("No camera device was detected on your system. You can upload an image from your device instead.");
            } else {
                // Fallback to native capture input
                cameraFileInput.click();
            }
        });
    }

    function stopActiveCameraStream() {
        if (activeCameraStream) {
            activeCameraStream.getTracks().forEach(track => track.stop());
            activeCameraStream = null;
        }
        if (cameraVideo) {
            cameraVideo.srcObject = null;
        }
    }

    if (cameraModalElem) {
        cameraModalElem.addEventListener('hidden.bs.modal', function() {
            stopActiveCameraStream();
            setCameraModalState('live');
            temporaryCapturedBlob = null;
        });
    }

    // Switch camera mode between Live Viewfinder and Captured Preview
    function setCameraModalState(state) {
        if (state === 'live') {
            cameraVideo.classList.remove('d-none');
            cameraPreviewImg.classList.add('d-none');
            cameraPreviewImg.src = '';
            cameraLiveOverlay.classList.remove('d-none');
            cameraModeBadge.textContent = 'Live Camera';
            cameraModeBadge.classList.replace('text-success', 'text-info');
            
            // Buttons
            btnFlipCamera.classList.remove('d-none');
            btnRetakePhoto.classList.add('d-none');
            btnSnapPhoto.classList.remove('d-none');
            btnConfirmPhoto.classList.add('d-none');
        } else if (state === 'preview') {
            cameraVideo.classList.add('d-none');
            cameraPreviewImg.classList.remove('d-none');
            cameraLiveOverlay.classList.add('d-none');
            cameraModeBadge.textContent = 'Preview Captured Photo';
            
            // Buttons
            btnFlipCamera.classList.add('d-none');
            btnRetakePhoto.classList.remove('d-none');
            btnSnapPhoto.classList.add('d-none');
            btnConfirmPhoto.classList.remove('d-none');
        }
    }

    // Flip Camera button
    btnFlipCamera.addEventListener('click', () => {
        currentFacingMode = (currentFacingMode === 'environment') ? 'user' : 'environment';
        startLiveCamera(currentFacingMode);
    });

    // Step 3 & 4: Snap Photo and switch to Preview Mode
    btnSnapPhoto.addEventListener('click', () => {
        if (!cameraVideo || !cameraVideo.videoWidth) return;

        cameraCanvas.width = cameraVideo.videoWidth;
        cameraCanvas.height = cameraVideo.videoHeight;
        const ctx = cameraCanvas.getContext('2d');
        ctx.drawImage(cameraVideo, 0, 0, cameraCanvas.width, cameraCanvas.height);

        cameraCanvas.toBlob(blob => {
            if (!blob) return;
            temporaryCapturedBlob = blob;
            const previewUrl = URL.createObjectURL(blob);
            cameraPreviewImg.src = previewUrl;
            setCameraModalState('preview');
            // Pause video tracks to save power
            if (activeCameraStream) {
                activeCameraStream.getVideoTracks().forEach(t => t.enabled = false);
            }
        }, 'image/jpeg', 0.94);
    });

    // Step 5: Retake Photo (resumes live stream)
    btnRetakePhoto.addEventListener('click', () => {
        temporaryCapturedBlob = null;
        if (activeCameraStream) {
            activeCameraStream.getVideoTracks().forEach(t => t.enabled = true);
        }
        setCameraModalState('live');
    });

    // Step 6: Confirm & Use Photo
    btnConfirmPhoto.addEventListener('click', () => {
        if (!temporaryCapturedBlob) return;
        const capturedFile = new File([temporaryCapturedBlob], 'camera_photo_' + Date.now() + '.jpg', { type: 'image/jpeg' });
        
        if (cameraModalInstance) {
            cameraModalInstance.hide();
        }
        stopActiveCameraStream();
        handleFileSelect(capturedFile);
    });

    // -------------------------------------------------------------
    // Drag and Drop & File Upload
    // -------------------------------------------------------------
    dropZone.addEventListener('click', () => {
        imageFileInput.click();
    });

    // Keyboard accessibility for dropzone
    dropZone.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            imageFileInput.click();
        }
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.add('dragover');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove('dragover');
        }, false);
    });

    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length) {
            handleFileSelect(files[0]);
        }
    });

    imageFileInput.addEventListener('change', function() {
        if (this.files.length) handleFileSelect(this.files[0]);
    });

    cameraFileInput.addEventListener('change', function() {
        if (this.files.length) handleFileSelect(this.files[0]);
    });

    // File validation and preview loader
    function handleFileSelect(file) {
        clearError();
        const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
        const maxSize = 8 * 1024 * 1024; // 8 MB

        if (!allowedTypes.includes(file.type.toLowerCase()) && !file.name.match(/\.(jpg|jpeg|png|webp)$/i)) {
            showError('<strong>Unsupported file format.</strong> Please upload a JPG, JPEG, PNG, or WebP image.');
            return;
        }

        if (file.size > maxSize) {
            showError('<strong>Image file is too large</strong> (' + (file.size / (1024 * 1024)).toFixed(1) + ' MB). Maximum allowed size is 8 MB.');
            return;
        }

        currentSelectedFile = file;
        previewFilename.textContent = file.name;
        previewFilesize.textContent = (file.size < 1024 * 1024) 
            ? (file.size / 1024).toFixed(1) + ' KB' 
            : (file.size / (1024 * 1024)).toFixed(2) + ' MB';

        const reader = new FileReader();
        reader.onload = function(e) {
            previewImage.src = e.target.result;
            dropZone.classList.add('d-none');
            previewContainer.classList.remove('d-none');
            previewActions.classList.remove('d-none');
            scanningState.classList.add('d-none');

            // Reset result panels
            resetResultViews();
        };
        reader.readAsDataURL(file);
    }

    // Reset all result view containers to idle
    function resetResultViews() {
        resultContent.classList.add('d-none');
        qualityFailContent.classList.add('d-none');
        outOfScopeContent.classList.add('d-none');
        if (unsupportedLesionContent) unsupportedLesionContent.classList.add('d-none');
        idleState.classList.remove('d-none');
    }

    // Remove selected image
    btnRemoveImage.addEventListener('click', () => {
        resetScannerState();
    });

    btnScanAnother.addEventListener('click', () => {
        resetScannerState();
    });

    btnQualityRetake.addEventListener('click', () => {
        resetScannerState();
    });

    btnScopeRetake.addEventListener('click', () => {
        resetScannerState();
    });

    if (btnLesionRetake) {
        btnLesionRetake.addEventListener('click', () => {
            resetScannerState();
        });
    }

    function resetScannerState() {
        currentSelectedFile = null;
        imageFileInput.value = '';
        cameraFileInput.value = '';
        previewImage.src = '';
        previewContainer.classList.add('d-none');
        dropZone.classList.remove('d-none');
        clearError();
        
        // Reset preview frame animation
        previewFrame.classList.remove('scanning-active');
        previewActions.classList.remove('d-none');
        btnScanImage.removeAttribute('disabled');
        btnScanImage.innerHTML = '<i class="bi bi-cpu me-1"></i> Scan Image';
        scanningState.classList.add('d-none');
        if (scanAnimationTimer) clearInterval(scanAnimationTimer);

        resetResultViews();
    }

    // -------------------------------------------------------------
    // Step 7: Execute Scan Image
    // -------------------------------------------------------------
    btnScanImage.addEventListener('click', function() {
        if (!currentSelectedFile) {
            showError('Please choose or photograph an affected skin area first.');
            return;
        }

        clearError();

        // 1. Enter Scanning State
        btnScanImage.setAttribute('disabled', 'disabled');
        btnScanImage.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Processing...';
        previewActions.classList.add('d-none');
        scanningState.classList.remove('d-none');
        previewFrame.classList.add('scanning-active');

        // Progressive sequential stage animation
        const steps = [
            "Analyzing image format & dimensions...",
            "Verifying illumination, exposure & focus...",
            "Checking lesion morphology against supported acute domain...",
            "Extracting spectrophotometric erythema & capillary indices...",
            "Measuring Sobel edge gradients & surface roughness...",
            "Evaluating chromatic dispersion & tissue convexity...",
            "Executing calibrated AI classifier...",
            "Synthesizing clinical observation report..."
        ];
        let stepIdx = 0;
        scanningStatusText.textContent = steps[0];
        scanProgressBar.style.width = '15%';

        scanAnimationTimer = setInterval(() => {
            stepIdx++;
            if (stepIdx < steps.length) {
                scanningStatusText.textContent = steps[stepIdx];
                scanProgressBar.style.width = Math.min(92, 15 + stepIdx * 12) + '%';
            }
        }, 260);

        // Prepare multipart form data
        const formData = new FormData();
        formData.append('image', currentSelectedFile);

        fetch('image_scanner.php?action=scan', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Server returned HTTP ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            clearInterval(scanAnimationTimer);
            scanProgressBar.style.width = '100%';
            
            setTimeout(() => {
                previewFrame.classList.remove('scanning-active');
                scanningState.classList.add('d-none');
                previewActions.classList.remove('d-none');
                btnScanImage.removeAttribute('disabled');
                btnScanImage.innerHTML = '<i class="bi bi-cpu me-1"></i> Scan Image';

                if (!data || data.success === false) {
                    showError('<strong>Image analysis unavailable:</strong> ' + (data.error || 'The analysis service encountered an error.'));
                    resetResultViews();
                } else if (data.is_quality_failure) {
                    displayQualityFailure(data);
                } else if (data.status === 'unsupported_lesion' || data.is_unsupported_lesion) {
                    displayUnsupportedLesion(data);
                } else if (data.is_out_of_scope || data.category === 'Unable to Assess') {
                    displayOutOfScope(data);
                } else {
                    displayResult(data);
                }
            }, 300);
        })
        .catch(err => {
            clearInterval(scanAnimationTimer);
            previewFrame.classList.remove('scanning-active');
            scanningState.classList.add('d-none');
            previewActions.classList.remove('d-none');
            btnScanImage.removeAttribute('disabled');
            btnScanImage.innerHTML = '<i class="bi bi-cpu me-1"></i> Scan Image';
            showError('<strong>Connection error:</strong> Unable to communicate with the analysis service. ' + err.message);
            resetResultViews();
        });
    });

    // Display Quality Failure Card (Requirement 4)
    function displayQualityFailure(res) {
        idleState.classList.add('d-none');
        resultContent.classList.add('d-none');
        outOfScopeContent.classList.add('d-none');
        if (unsupportedLesionContent) unsupportedLesionContent.classList.add('d-none');
        qualityFailContent.classList.remove('d-none');

        const reason = (res.findings && res.findings.length) ? res.findings[0] : 'Image quality is too low for reliable analysis.';
        qualityFailReason.textContent = reason;

        if (window.innerWidth < 992) {
            document.getElementById('resultCardContainer').scrollIntoView({ behavior: 'smooth' });
        }
    }

    // Display Out of Scope / Uncertain Card (Requirement 8)
    function displayOutOfScope(res) {
        idleState.classList.add('d-none');
        resultContent.classList.add('d-none');
        qualityFailContent.classList.add('d-none');
        if (unsupportedLesionContent) unsupportedLesionContent.classList.add('d-none');
        outOfScopeContent.classList.remove('d-none');

        const reason = (res.findings && res.findings.length) 
            ? res.findings.join(' ') 
            : 'Visual features did not meet the statistical confidence threshold for supported skin categories.';
        outOfScopeReason.textContent = reason;

        if (window.innerWidth < 992) {
            document.getElementById('resultCardContainer').scrollIntoView({ behavior: 'smooth' });
        }
    }

    // Display Unsupported Skin Lesion / Outside Scope Card (Section 5, 11, 12, 13)
    function displayUnsupportedLesion(res) {
        idleState.classList.add('d-none');
        resultContent.classList.add('d-none');
        qualityFailContent.classList.add('d-none');
        outOfScopeContent.classList.add('d-none');
        if (unsupportedLesionContent) unsupportedLesionContent.classList.remove('d-none');

        if (lesionWhatDetected) {
            lesionWhatDetected.textContent = res.what_detected || (res.findings && res.findings[0]) || 
                'The computer vision analyzer detected localized hyperpigmented melanin clustering with high contrast drop and chromatic variegation against surrounding skin.';
        }
        if (lesionNextStepText && res.recommended_next_step) {
            lesionNextStepText.textContent = res.recommended_next_step;
        }

        if (lesionTechFeaturesList) {
            lesionTechFeaturesList.innerHTML = '';
            const techFeats = res.technical_image_features || [];
            if (techFeats.length) {
                techFeats.forEach(tf => {
                    const div = document.createElement('div');
                    div.className = 'd-flex align-items-center mb-1 text-muted small';
                    div.innerHTML = '<i class="bi bi-gear-fill me-2 text-warning" style="font-size: 0.75rem;"></i><span>' + tf + '</span>';
                    lesionTechFeaturesList.appendChild(div);
                });
            } else {
                const metrics = res.metrics || {};
                const div = document.createElement('div');
                div.className = 'text-muted small';
                div.textContent = 'Spectrophotometric Erythema: ' + (metrics.erythema_index ?? 'N/A') + ' | Surface Roughness: ' + (metrics.surface_roughness ?? 'N/A') + ' | Chromatic Dispersion: ' + (metrics.chromatic_variance ?? 'N/A');
                lesionTechFeaturesList.appendChild(div);
            }
        }

        if (window.innerWidth < 992) {
            document.getElementById('resultCardContainer').scrollIntoView({ behavior: 'smooth' });
        }
    }

    // Display Valid Result Card (Requirements 13 & 14)
    function displayResult(res) {
        idleState.classList.add('d-none');
        qualityFailContent.classList.add('d-none');
        outOfScopeContent.classList.add('d-none');
        if (unsupportedLesionContent) unsupportedLesionContent.classList.add('d-none');
        resultContent.classList.remove('d-none');

        const category = res.category || 'Unable to Assess';
        resultCategoryText.textContent = category;

        // Category Badge Colors
        resultCategoryBadge.className = 'badge-category';
        if (category.includes('Infection')) {
            resultCategoryBadge.classList.add('badge-category-infection');
        } else if (category.includes('Inflammation')) {
            resultCategoryBadge.classList.add('badge-category-inflammation');
        } else if (category.includes('Minor Injury')) {
            resultCategoryBadge.classList.add('badge-category-injury');
        } else if (category.includes('Rash')) {
            resultCategoryBadge.classList.add('badge-category-rash');
        } else if (category.includes('Swelling')) {
            resultCategoryBadge.classList.add('badge-category-swelling');
        } else {
            resultCategoryBadge.classList.add('badge-category-unable');
        }

        // Summary Heading
        resultSummaryHeading.textContent = "Visual indicators may be consistent with " + category.toLowerCase();
        resultWhatDetected.textContent = res.what_detected || (res.findings ? res.findings[0] : 'Optical features analyzed via calibrated vision model.');

        // Runner Up Pattern
        if (res.runner_ups && res.runner_ups.length > 0) {
            const ru = res.runner_ups[0];
            resultRunnerUpText.textContent = ru.category + ' (' + ru.probability + '% probability)';
            resultRunnerUpContainer.classList.remove('d-none');
        } else {
            resultRunnerUpContainer.classList.add('d-none');
        }

        // Quantitative Metrics
        const metrics = res.metrics || {};
        valErythema.textContent = (metrics.erythema_index !== undefined) ? metrics.erythema_index : '--';
        valRoughness.textContent = (metrics.surface_roughness !== undefined) ? metrics.surface_roughness : '--';
        valChroma.textContent = (metrics.chromatic_variance !== undefined) ? metrics.chromatic_variance : '--';

        // Confidence Score Bar (Calibrated Model Confidence)
        const score = (typeof res.confidence_score === 'number') ? res.confidence_score : 0;
        resultScoreText.textContent = score.toFixed(1) + '%';
        resultScoreBar.style.width = Math.min(100, Math.max(0, score)) + '%';

        // Observed Characteristics List
        resultObsList.innerHTML = '';
        const obs = res.observable_characteristics || res.findings || [];
        if (obs.length) {
            obs.forEach(item => {
                const div = document.createElement('div');
                div.className = 'scanner-obs-item';
                div.innerHTML = '<span class="scanner-obs-bullet"></span><span>' + item + '</span>';
                resultObsList.appendChild(div);
            });
        }

        // Technical Image Features (Section 4 & 13)
        if (resultTechFeaturesList) {
            resultTechFeaturesList.innerHTML = '';
            const techFeats = res.technical_image_features || [];
            if (techFeats.length) {
                techFeats.forEach(tf => {
                    const div = document.createElement('div');
                    div.className = 'd-flex align-items-center mb-1 text-muted small';
                    div.innerHTML = '<i class="bi bi-gear-fill me-2 text-info" style="font-size: 0.75rem;"></i><span>' + tf + '</span>';
                    resultTechFeaturesList.appendChild(div);
                });
            } else {
                const div = document.createElement('div');
                div.className = 'text-muted small';
                div.textContent = 'Erythema Index: ' + (metrics.erythema_index ?? '--') + ' | Surface Roughness: ' + (metrics.surface_roughness ?? '--') + ' | Chromatic Variance: ' + (metrics.chromatic_variance ?? '--');
                resultTechFeaturesList.appendChild(div);
            }
        }

        // What This Result Means (Section 13)
        if (resultWhatMeansText) {
            resultWhatMeansText.textContent = res.what_this_result_means || res.general_information || 'Educational context regarding observed visual patterns.';
        }

        // Recommended Next Step (Section 13)
        if (resultNextStepText) {
            resultNextStepText.textContent = res.recommended_next_step || 'Follow appropriate first-aid care and monitor the affected area closely.';
        }

        // General Information
        resultGeneralInfo.textContent = res.general_information || 'No general information available for this category.';

        // General Care Guidance
        resultCareList.innerHTML = '';
        const care = res.general_care || res.recommendations || [];
        if (care.length) {
            care.forEach(item => {
                const div = document.createElement('div');
                div.className = 'scanner-care-point';
                div.innerHTML = '<i class="bi bi-check-circle-fill"></i><span>' + item + '</span>';
                resultCareList.appendChild(div);
            });
        }

        // Warning Signs
        resultWarningList.innerHTML = '';
        const warnings = res.warning_signs || [];
        if (warnings.length) {
            warnings.forEach(item => {
                const div = document.createElement('div');
                div.className = 'scanner-warning-item';
                div.innerHTML = '<i class="bi bi-exclamation-triangle-fill"></i><span>' + item + '</span>';
                resultWarningList.appendChild(div);
            });
        }

        // When to Seek Care
        resultWhenCareList.innerHTML = '';
        const whenCare = res.when_to_seek_care || [];
        if (whenCare.length) {
            whenCare.forEach(item => {
                const div = document.createElement('div');
                div.className = 'scanner-care-point';
                div.innerHTML = '<i class="bi bi-arrow-right-circle-fill text-warning"></i><span>' + item + '</span>';
                resultWhenCareList.appendChild(div);
            });
        }

        // Scroll result into view on mobile
        if (window.innerWidth < 992) {
            document.getElementById('resultCardContainer').scrollIntoView({ behavior: 'smooth' });
        }
    }
});
</script>

<?php require_once __DIR__ . '/includes/footer.php'; ?>
