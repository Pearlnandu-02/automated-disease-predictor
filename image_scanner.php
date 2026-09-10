<?php
// image_scanner.php - AI Infection & Injury Image Scanner
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
    $is_ajax = isset($_GET['action']) && $_GET['action'] === 'scan' || 
               (isset($_SERVER['HTTP_X_REQUESTED_WITH']) && strtolower($_SERVER['HTTP_X_REQUESTED_WITH']) === 'xmlhttprequest');

    if (!isset($_FILES['image']) || $_FILES['image']['error'] === UPLOAD_ERR_NO_FILE) {
        $error_message = "Please select or capture an image of the affected area to scan.";
    } elseif ($_FILES['image']['error'] !== UPLOAD_ERR_OK) {
        $error_message = "Error uploading file (Code: " . $_FILES['image']['error'] . "). Please try again.";
    } elseif ($_FILES['image']['size'] > $max_file_size) {
        $error_message = "Image size exceeds the 8 MB limit. Please upload a smaller or compressed photo.";
    } else {
        $file_tmp = $_FILES['image']['tmp_name'];
        $orig_name = basename($_FILES['image']['name']);
        $ext = strtolower(pathinfo($orig_name, PATHINFO_EXTENSION));

        // MIME validation
        $finfo = finfo_open(FILEINFO_MIME_TYPE);
        $mime_type = finfo_file($finfo, $file_tmp);
        finfo_close($finfo);

        if (!in_array($ext, $allowed_exts) || !in_array($mime_type, $allowed_mimes)) {
            $error_message = "Unsupported file type ({$mime_type}). Only JPG, JPEG, PNG, and WEBP images are accepted.";
        } else {
            // Ephemeral temporary processing
            $temp_scan_path = sys_get_temp_dir() . DIRECTORY_SEPARATOR . 'scan_' . bin2hex(random_bytes(8)) . '.' . $ext;
            
            if (move_uploaded_file($file_tmp, $temp_scan_path)) {
                try {
                    // Call Python Computer Vision microservice / bridge
                    $scan_result = call_image_scanner($temp_scan_path);
                } catch (Exception $e) {
                    $error_message = "Computer vision processing error: " . $e->getMessage();
                } finally {
                    // STRICT PRIVACY: Immediately delete temporary uploaded image
                    if (file_exists($temp_scan_path)) {
                        @unlink($temp_scan_path);
                    }
                }
            } else {
                $error_message = "Failed to store temporary upload for processing. Please try again.";
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

require_once __DIR__ . '/includes/header.php';
?>

<!-- Page Header & Hero -->
<div class="row mb-4">
    <div class="col-12">
        <div class="hero-banner p-4 p-md-5 mb-3">
            <div class="row align-items-center">
                <div class="col-lg-8">
                    <span class="badge hero-badge px-3 py-2 rounded-pill mb-3">
                        <i class="bi bi-camera-fill me-1"></i> Computer Vision Pipeline
                    </span>
                    <h1 class="display-6 fw-bold hero-heading mb-2">AI Infection & Injury Scanner</h1>
                    <p class="lead mb-0 hero-lead">
                        Upload a clear image of a skin injury, wound, rash, swelling, or redness for an AI-assisted preliminary visual assessment.
                    </p>
                </div>
                <div class="col-lg-4 text-lg-end d-none d-lg-block">
                    <i class="bi bi-shield-check display-1 opacity-50"></i>
                </div>
            </div>
        </div>

        <!-- Mandatory Educational Disclaimer -->
        <div class="disclaimer-banner mb-3 shadow-sm">
            <div class="d-flex align-items-start gap-2">
                <i class="bi bi-exclamation-triangle-fill fs-5 mt-1 flex-shrink-0"></i>
                <div>
                    <strong>Important Medical Notice:</strong> This AI scanner provides an <em>educational preliminary visual assessment</em> and is not a medical diagnosis. For concerning, worsening, infected, or serious injuries, consult a qualified healthcare professional.
                </div>
            </div>
        </div>

        <!-- Privacy Assurance Banner -->
        <div class="alert alert-secondary py-2 px-3 small border d-flex align-items-center gap-2 mb-4 bg-card-custom text-secondary-theme">
            <i class="bi bi-shield-lock-fill text-success fs-5"></i>
            <div>
                <strong>Privacy Assurance:</strong> Uploaded images are processed ephemerally in memory and permanently deleted immediately after visual metric extraction. Photos are <strong>never stored</strong> in our database. <em>Do not upload identifying personal documents or faces.</em>
            </div>
        </div>
    </div>
</div>

<!-- Main Scanner Layout -->
<div class="row g-4 mb-5">
    <!-- Left Column: Upload & Live Preview -->
    <div class="col-lg-6">
        <div class="card card-custom h-100 p-4">
            <h4 class="fw-bold mb-1 d-flex align-items-center gap-2">
                <i class="bi bi-cloud-arrow-up text-info"></i> Scan an Infection or Injury
            </h4>
            <p class="text-muted small mb-3">
                Upload a clear, well-lit image of the affected skin area for preliminary analysis.
            </p>

            <!-- Error Feedback -->
            <div id="scannerErrorAlert" class="alert alert-danger d-none mb-3 py-2 px-3 small" role="alert">
                <i class="bi bi-exclamation-circle-fill me-1"></i> <span id="scannerErrorMsg"></span>
            </div>

            <!-- Upload Area / Drag & Drop -->
            <div id="dropZone" class="scanner-dropzone mb-3">
                <div class="scanner-icon-circle">
                    <i class="bi bi-image"></i>
                </div>
                <h5 class="fw-bold mb-1">Drag & Drop Image Here</h5>
                <p class="text-muted small mb-3">or click a button below to choose from your device</p>
                
                <div class="d-flex flex-wrap justify-content-center gap-2">
                    <button type="button" class="btn btn-outline-info rounded-pill px-3 py-2 btn-sm" id="btnBrowseFiles">
                        <i class="bi bi-folder2-open me-1"></i> Upload Image
                    </button>
                    <button type="button" class="btn btn-outline-info rounded-pill px-3 py-2 btn-sm" id="btnTakePhoto">
                        <i class="bi bi-camera me-1"></i> Take Photo
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
                    <div class="scanner-laser-beam">
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

                <!-- Action Controls (User must confirm before scan begins) -->
                <div class="d-flex gap-2" id="previewActions">
                    <button type="button" class="btn btn-outline-danger flex-fill py-2 rounded-3" id="btnRemoveImage">
                        <i class="bi bi-trash3 me-1"></i> Remove Image
                    </button>
                    <button type="button" class="btn btn-primary-custom flex-fill py-2" id="btnScanImage">
                        <i class="bi bi-cpu me-1"></i> Scan Image
                    </button>
                </div>

                <!-- Scanning Progress State (Hidden by default) -->
                <div id="scanningState" class="d-none text-center py-3">
                    <div class="d-inline-flex align-items-center gap-2 mb-2">
                        <span class="scanner-status-pulse"></span>
                        <strong class="text-info fs-5">Analyzing image...</strong>
                    </div>
                    <p id="scanningStatusText" class="text-muted small mb-2">
                        Analyzing visual characteristics...
                    </p>
                    <div class="progress" style="height: 6px;">
                        <div id="scanProgressBar" class="progress-bar progress-bar-striped progress-bar-animated bg-info" style="width: 45%;"></div>
                    </div>
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
                <p class="text-muted small max-w-sm mx-auto mb-4" style="max-width: 380px;">
                    Select or photograph an affected skin area and click <strong>"Scan Image"</strong>. The computer vision analyzer will calculate erythema indices, edge disruption, and color dispersion.
                </p>
                <div class="p-3 bg-card-subtle rounded-3 border text-start small">
                    <h6 class="fw-bold mb-2 text-info"><i class="bi bi-info-circle me-1"></i> How this tool works:</h6>
                    <ul class="mb-0 text-muted ps-3">
                        <li class="mb-1"><strong>Erythema Index:</strong> Measures capillary dilation and redness spectroscopy.</li>
                        <li class="mb-1"><strong>Edge Roughness:</strong> Computes high-frequency Sobel gradient changes (abrasions, lacerations).</li>
                        <li><strong>Quality Gate:</strong> Filters out blurry or poorly lit images to prevent false observations.</li>
                    </ul>
                </div>
            </div>

            <!-- Active Assessment Result View (Revealed after scan completes) -->
            <div id="resultContent" class="d-none">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <span class="text-muted small fw-bold text-uppercase tracking-wider">
                        <i class="bi bi-clipboard2-pulse me-1"></i> Visual Assessment
                    </span>
                    <span id="resultTimestamp" class="small text-muted">Just now</span>
                </div>

                <!-- Category Badge -->
                <div class="mb-3">
                    <span id="resultCategoryBadge" class="badge-category badge-category-injury">
                        <i class="bi bi-search"></i> <span id="resultCategoryText">Evaluating...</span>
                    </span>
                </div>

                <!-- Wording Requirement: "Visual indicators may be consistent with..." -->
                <div class="p-3 bg-card-subtle rounded-3 border mb-3">
                    <h5 class="fw-bold mb-1" id="resultSummaryHeading">Visual indicators may be consistent with...</h5>
                    <p class="text-muted small mb-0" id="resultSummaryDesc">
                        Assessment generated via spectrophotometric color analysis and surface edge gradient measurement.
                    </p>
                </div>

                <!-- Confidence / Assessment Metric Score -->
                <div class="mb-3 p-3 bg-card-subtle rounded-3 border">
                    <div class="d-flex justify-content-between align-items-center mb-1">
                        <span class="small fw-semibold">Visual Metric Correlation Score:</span>
                        <span id="resultScoreText" class="fw-bold text-info">0.0%</span>
                    </div>
                    <div class="progress" style="height: 8px;">
                        <div id="resultScoreBar" class="progress-bar bg-info" style="width: 0%;"></div>
                    </div>
                    <small class="text-muted" style="font-size: 0.76rem;">
                        Reflects quantitative alignment with benchmarked dermatological visual features. Not a diagnostic certainty.
                    </small>
                </div>

                <!-- Computer Vision Metrics Grid -->
                <h6 class="fw-bold small text-uppercase text-muted mb-2">Quantitative Image Metrics</h6>
                <div class="row g-2 mb-3">
                    <div class="col-4">
                        <div class="metric-pill-card">
                            <div class="metric-pill-val" id="valErythema">--</div>
                            <div class="metric-pill-lbl">Erythema Index</div>
                        </div>
                    </div>
                    <div class="col-4">
                        <div class="metric-pill-card">
                            <div class="metric-pill-val" id="valRoughness">--</div>
                            <div class="metric-pill-lbl">Roughness</div>
                        </div>
                    </div>
                    <div class="col-4">
                        <div class="metric-pill-card">
                            <div class="metric-pill-val" id="valChroma">--</div>
                            <div class="metric-pill-lbl">Color Variance</div>
                        </div>
                    </div>
                </div>

                <!-- Key Visual Observations -->
                <div class="mb-3">
                    <h6 class="fw-bold small text-uppercase text-muted mb-2">Visual Observations</h6>
                    <ul id="resultFindingsList" class="small text-muted ps-3 mb-0">
                        <!-- Populated dynamically -->
                    </ul>
                </div>

                <!-- Recommended Educational Care Guidance -->
                <div class="mb-3">
                    <h6 class="fw-bold small text-uppercase text-muted mb-2">General Educational First-Aid Points</h6>
                    <ul id="resultRecsList" class="small text-muted ps-3 mb-0">
                        <!-- Populated dynamically -->
                    </ul>
                </div>

                <!-- Reset Button -->
                <button type="button" class="btn btn-outline-info w-100 rounded-3 py-2" id="btnScanAnother">
                    <i class="bi bi-arrow-repeat me-1"></i> Scan Another Image
                </button>
            </div>
        </div>
    </div>
</div>

<!-- "When to Seek Immediate Medical Attention" Safety Section -->
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

<!-- Live Camera Modal -->
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
                <div id="cameraStreamContainer" class="position-relative overflow-hidden rounded-3 bg-black" style="min-height: 280px; max-height: 420px;">
                    <video id="cameraVideo" autoplay playsinline muted class="w-100 h-100" style="object-fit: cover;"></video>
                    <!-- Visual focus reticle -->
                    <div class="position-absolute top-50 start-50 translate-middle border border-info border-2 rounded-circle opacity-75 pointer-events-none" style="width: 140px; height: 140px; border-style: dashed !important;"></div>
                </div>
                <canvas id="cameraCanvas" class="d-none"></canvas>
                <div id="cameraAlert" class="alert alert-warning d-none mt-2 py-2 px-3 small text-start"></div>
            </div>
            <div class="modal-footer border-top border-subtle d-flex justify-content-between">
                <button type="button" class="btn btn-outline-secondary rounded-pill px-3" id="btnFlipCamera">
                    <i class="bi bi-arrow-repeat me-1"></i> Flip Camera
                </button>
                <div class="d-flex gap-2">
                    <button type="button" class="btn btn-outline-danger rounded-pill px-3" data-bs-dismiss="modal" id="btnCancelCamera">
                        Cancel
                    </button>
                    <button type="button" class="btn btn-info rounded-pill px-4 text-white fw-bold" id="btnSnapPhoto">
                        <i class="bi bi-circle-fill me-1"></i> Capture
                    </button>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Interactive Scanner Client Script -->
<script>
document.addEventListener('DOMContentLoaded', function() {
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
    const btnScanImage = document.getElementById('btnScanImage');
    const scanningState = document.getElementById('scanningState');
    const scanningStatusText = document.getElementById('scanningStatusText');
    const scanProgressBar = document.getElementById('scanProgressBar');
    const previewFrame = document.getElementById('previewFrame');

    const idleState = document.getElementById('idleState');
    const resultContent = document.getElementById('resultContent');
    const resultCategoryBadge = document.getElementById('resultCategoryBadge');
    const resultCategoryText = document.getElementById('resultCategoryText');
    const resultSummaryHeading = document.getElementById('resultSummaryHeading');
    const resultScoreText = document.getElementById('resultScoreText');
    const resultScoreBar = document.getElementById('resultScoreBar');
    const valErythema = document.getElementById('valErythema');
    const valRoughness = document.getElementById('valRoughness');
    const valChroma = document.getElementById('valChroma');
    const resultFindingsList = document.getElementById('resultFindingsList');
    const resultRecsList = document.getElementById('resultRecsList');
    const btnScanAnother = document.getElementById('btnScanAnother');

    const scannerErrorAlert = document.getElementById('scannerErrorAlert');
    const scannerErrorMsg = document.getElementById('scannerErrorMsg');

    // Camera Modal Elements
    const cameraModalElem = document.getElementById('cameraModal');
    let cameraModalInstance = null;
    const cameraVideo = document.getElementById('cameraVideo');
    const cameraCanvas = document.getElementById('cameraCanvas');
    const cameraAlert = document.getElementById('cameraAlert');
    const btnSnapPhoto = document.getElementById('btnSnapPhoto');
    const btnFlipCamera = document.getElementById('btnFlipCamera');
    let activeCameraStream = null;
    let currentFacingMode = 'environment'; // default rear camera for wounds/injuries

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

    // Trigger Camera capture
    btnTakePhoto.addEventListener('click', (e) => {
        e.stopPropagation();
        clearError();

        // Check if WebRTC getUserMedia is available and supported
        if (navigator.mediaDevices && typeof navigator.mediaDevices.getUserMedia === 'function') {
            startLiveCamera(currentFacingMode);
        } else {
            // Native fallback for mobile browsers without getUserMedia or non-HTTPS
            cameraFileInput.click();
        }
    });

    function startLiveCamera(facingMode) {
        if (!cameraModalInstance && typeof bootstrap !== 'undefined') {
            cameraModalInstance = new bootstrap.Modal(cameraModalElem);
        }

        stopActiveCameraStream();
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
            // Handle permission denial or unavailable camera gracefully
            if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
                showError('<strong>Camera access denied.</strong> Please allow camera access in your browser settings, or use the <em>Upload Image</em> button.');
            } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
                showError('<strong>No camera device detected.</strong> Please use the <em>Upload Image</em> button to select an image from your device.');
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
        });
    }

    // Flip Camera button
    btnFlipCamera.addEventListener('click', () => {
        currentFacingMode = (currentFacingMode === 'environment') ? 'user' : 'environment';
        startLiveCamera(currentFacingMode);
    });

    // Snap Photo from camera stream
    btnSnapPhoto.addEventListener('click', () => {
        if (!cameraVideo || !cameraVideo.videoWidth) return;

        cameraCanvas.width = cameraVideo.videoWidth;
        cameraCanvas.height = cameraVideo.videoHeight;
        const ctx = cameraCanvas.getContext('2d');
        ctx.drawImage(cameraVideo, 0, 0, cameraCanvas.width, cameraCanvas.height);

        cameraCanvas.toBlob(blob => {
            if (!blob) return;
            const capturedFile = new File([blob], 'camera_photo_' + Date.now() + '.jpg', { type: 'image/jpeg' });
            if (cameraModalInstance) {
                cameraModalInstance.hide();
            }
            stopActiveCameraStream();
            handleFileSelect(capturedFile);
        }, 'image/jpeg', 0.92);
    });

    // Drag and Drop
    dropZone.addEventListener('click', () => {
        imageFileInput.click();
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
            showError('<strong>Unsupported file type.</strong> Please upload a JPG, JPEG, PNG, or WEBP image.');
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

            // Reset result panel when new image loaded
            resultContent.classList.add('d-none');
            idleState.classList.remove('d-none');
        };
        reader.readAsDataURL(file);
    }

    // Remove selected image
    btnRemoveImage.addEventListener('click', () => {
        resetScannerState();
    });

    btnScanAnother.addEventListener('click', () => {
        resetScannerState();
    });

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

        // Reset Results view
        resultContent.classList.add('d-none');
        idleState.classList.remove('d-none');
    }

    // Execute scan
    btnScanImage.addEventListener('click', function() {
        if (!currentSelectedFile) {
            showError('Please choose or photograph an image first.');
            return;
        }

        clearError();

        // 1. Enter Scanning State
        btnScanImage.setAttribute('disabled', 'disabled');
        btnScanImage.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Processing...';
        previewActions.classList.add('d-none');
        scanningState.classList.remove('d-none');
        previewFrame.classList.add('scanning-active');

        // Progress text animation with real sequential progression
        const steps = [
            "Preparing image for analysis...",
            "Computing spectrophotometric erythema index...",
            "Analyzing surface texture & edge roughness...",
            "Evaluating chromatic dispersion & color variance...",
            "Checking focus sharpness and exposure balance...",
            "Generating preliminary assessment..."
        ];
        let stepIdx = 0;
        scanningStatusText.textContent = steps[0];
        scanProgressBar.style.width = '15%';

        scanAnimationTimer = setInterval(() => {
            stepIdx++;
            if (stepIdx < steps.length) {
                scanningStatusText.textContent = steps[stepIdx];
                scanProgressBar.style.width = Math.min(90, 15 + stepIdx * 15) + '%';
            }
        }, 300);

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

                // Check for real failure (do not display empty fake result)
                if (!data || data.success === false) {
                    showError('<strong>Image analysis could not be completed.</strong><br>Reason: ' + (data.error || 'Image processing service unavailable. Please ensure the backend is running.'));
                    resultContent.classList.add('d-none');
                    idleState.classList.remove('d-none');
                } else {
                    displayResult(data);
                }
            }, 350);
        })
        .catch(err => {
            clearInterval(scanAnimationTimer);
            previewFrame.classList.remove('scanning-active');
            scanningState.classList.add('d-none');
            previewActions.classList.remove('d-none');
            btnScanImage.removeAttribute('disabled');
            btnScanImage.innerHTML = '<i class="bi bi-cpu me-1"></i> Scan Image';
            showError('<strong>Analysis unavailable:</strong> Unable to connect to the image analysis service. ' + err.message);
            resultContent.classList.add('d-none');
            idleState.classList.remove('d-none');
        });
    });

    function displayResult(res) {
        idleState.classList.add('d-none');
        resultContent.classList.remove('d-none');

        const category = res.category || 'Unable to Assess';
        resultCategoryText.textContent = category;

        // Reset badge classes
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

        // Mandatory educational cautious phrasing
        resultSummaryHeading.textContent = "Visual indicators may be consistent with " + category.toLowerCase();

        // Metrics: Use calculated values or display "Not available"
        const metrics = res.metrics || {};
        valErythema.textContent = (metrics.erythema_index !== undefined) ? metrics.erythema_index : 'Not available';
        
        const roughnessVal = (metrics.surface_roughness !== undefined) 
            ? metrics.surface_roughness 
            : ((metrics.roughness_score !== undefined) ? metrics.roughness_score : 'Not available');
        valRoughness.textContent = roughnessVal;

        const chromaVal = (metrics.chromatic_variance !== undefined) 
            ? metrics.chromatic_variance 
            : ((metrics.color_variance !== undefined) ? metrics.color_variance : 'Not available');
        valChroma.textContent = chromaVal;

        // Correlation Score Counter
        const score = (typeof res.confidence_score === 'number') ? res.confidence_score : 0;
        resultScoreText.textContent = score.toFixed(1) + '%';
        resultScoreBar.style.width = Math.min(100, Math.max(0, score)) + '%';

        // Observations List
        resultFindingsList.innerHTML = '';
        if (res.findings && res.findings.length) {
            res.findings.forEach(f => {
                const li = document.createElement('li');
                li.className = 'mb-1';
                li.innerHTML = f;
                resultFindingsList.appendChild(li);
            });
        } else {
            resultFindingsList.innerHTML = '<li>Visual observation metrics recorded within standard baseline range.</li>';
        }

        // Recommendations List
        resultRecsList.innerHTML = '';
        if (res.recommendations && res.recommendations.length) {
            res.recommendations.forEach(r => {
                const li = document.createElement('li');
                li.className = 'mb-1';
                li.innerHTML = r;
                resultRecsList.appendChild(li);
            });
        } else {
            resultRecsList.innerHTML = '<li>Maintain standard hygiene and monitor for worsening symptoms.</li>';
        }

        // Scroll result into view on mobile
        if (window.innerWidth < 992) {
            document.getElementById('resultCardContainer').scrollIntoView({ behavior: 'smooth' });
        }
    }
});
</script>

<?php require_once __DIR__ . '/includes/footer.php'; ?>
