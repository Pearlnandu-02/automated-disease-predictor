<?php
require_once __DIR__ . '/includes/functions.php';
require_once __DIR__ . '/includes/auth.php';
require_once __DIR__ . '/includes/ml_bridge.php';
require_once __DIR__ . '/services/symptom_prediction.php';

$pdo = get_db_connection();

// Load symptoms and diseases from structured datasets
$all_symptoms = SymptomPredictionService::getSymptoms();
$all_diseases = SymptomPredictionService::getDiseases();

$selected_keys = [];
$server_result = null;

// Pre-selection via GET query parameter (e.g. from Symptoms Guide)
if (isset($_GET['symptom']) && !empty($_GET['symptom'])) {
    $clean_get = preg_replace('/[^a-zA-Z0-9_]/', '', trim($_GET['symptom']));
    if (!empty($clean_get)) {
        $selected_keys[] = $clean_get;
    }
}

// Handle traditional form submission POST (fallback if JS disabled)
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $raw_symptoms = $_POST['symptoms'] ?? [];
    if (!is_array($raw_symptoms)) {
        $raw_symptoms = [$raw_symptoms];
    }
    
    $selected_keys = [];
    foreach ($raw_symptoms as $sk) {
        $clean = preg_replace('/[^a-zA-Z0-9_]/', '', trim($sk));
        if (!empty($clean)) {
            $selected_keys[] = $clean;
        }
    }
    $selected_keys = array_values(array_unique($selected_keys));

    if (count($selected_keys) >= 2) {
        $context = [
            'ageGroup' => $_POST['age_group'] ?? 'adult',
            'duration' => $_POST['duration'] ?? '1_3_days',
            'severity' => $_POST['severity'] ?? 'moderate',
            'trajectory' => $_POST['trajectory'] ?? 'same'
        ];
        $server_result = SymptomPredictionService::matchSymptoms($selected_keys, $context);
        
        // Save to DB history if user logged in
        if (is_logged_in() && $pdo && !empty($server_result['conditions'])) {
            try {
                $user = get_logged_in_user();
                $sym_str = implode(', ', array_map(function($k) { return ucwords(str_replace('_', ' ', $k)); }, $selected_keys));
                $top = $server_result['conditions'][0];
                $stmt = $pdo->prepare("INSERT INTO prediction_history (user_id, symptoms_selected, predicted_disease, confidence) VALUES (?, ?, ?, ?)");
                $stmt->execute([
                    $user['id'],
                    $sym_str,
                    $top['name'],
                    $top['score']
                ]);
            } catch (Exception $e) {
                // Silently bypass history logging error
            }
        }
    }
}

$page_title = 'MediSense AI | Symptom-Based Disease Prediction';
require_once __DIR__ . '/includes/header.php';
?>

<div class="container py-4">
    <!-- Breadcrumb -->
    <nav aria-label="breadcrumb" class="mb-3">
        <ol class="breadcrumb">
            <li class="breadcrumb-item"><a href="index.php" class="text-decoration-none text-info">Home</a></li>
            <li class="breadcrumb-item active" aria-current="page">AI Prediction</li>
        </ol>
    </nav>

    <!-- Header Section -->
    <div class="row align-items-center mb-4">
        <div class="col-lg-8">
            <span class="badge hero-badge px-3 py-2 rounded-pill fw-bold mb-2">
                <i class="bi bi-cpu-fill me-1"></i> CLINICAL DECISION SUPPORT
            </span>
            <h1 class="display-5 fw-extrabold mb-2">Symptom-Based Disease Prediction</h1>
            <p class="lead text-muted mb-0">
                Select or type your active symptoms to receive an educational evaluation of possible health conditions based on transparent clinical co-occurrence models.
            </p>
        </div>
        <div class="col-lg-4 text-lg-end mt-3 mt-lg-0">
            <button type="button" class="btn btn-outline-info rounded-pill px-3 py-2 fw-semibold" data-bs-toggle="modal" data-bs-target="#methodologyModal">
                <i class="bi bi-info-circle me-1"></i> Data & Methodology
            </button>
        </div>
    </div>

    <div class="row g-4">
        <!-- LEFT COLUMN: SYMPTOM INPUT, SEARCH, TILES & CONTEXT -->
        <div class="col-lg-6">
            <div class="card-custom p-4 mb-4">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h4 class="fw-bold mb-0 d-flex align-items-center">
                        <i class="bi bi-search text-info me-2"></i> Search & Select Symptoms
                    </h4>
                    <span class="badge bg-secondary bg-opacity-50 text-muted" id="selectedCountBadge">
                        0 symptoms selected
                    </span>
                </div>

                <!-- Natural Language Search Input -->
                <div class="position-relative mb-3">
                    <div class="input-group">
                        <span class="input-group-text bg-card-subtle text-info border">
                            <i class="bi bi-search"></i>
                        </span>
                        <input 
                            type="text" 
                            id="symptomSearchInput" 
                            class="form-control" 
                            placeholder="Type a symptom (e.g., headache, fever, fatigue, vomiting)..."
                            autocomplete="off"
                        >
                    </div>
                    <!-- Autocomplete Dropdown List -->
                    <div id="symptomAutocompleteList" class="list-group position-absolute w-100 shadow-lg mt-1 z-3" style="display: none; max-height: 280px; overflow-y: auto;">
                    </div>
                </div>

                <!-- Quick-Add Popular Symptoms -->
                <div class="mb-4">
                    <span class="small text-muted d-block mb-2 fw-semibold">Quick-Add Common Symptoms:</span>
                    <div class="d-flex flex-wrap gap-2">
                        <button type="button" class="btn btn-sm btn-outline-secondary symptom-popular-pill rounded-pill" data-symptom="fever">
                            + Fever
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-secondary symptom-popular-pill rounded-pill" data-symptom="cough_with_sputum">
                            + Cough
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-secondary symptom-popular-pill rounded-pill" data-symptom="headache">
                            + Headache
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-secondary symptom-popular-pill rounded-pill" data-symptom="fatigue">
                            + Fatigue
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-secondary symptom-popular-pill rounded-pill" data-symptom="sore_throat">
                            + Sore Throat
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-secondary symptom-popular-pill rounded-pill" data-symptom="shortness_of_breath">
                            + Shortness of Breath
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-secondary symptom-popular-pill rounded-pill" data-symptom="nausea">
                            + Nausea
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-secondary symptom-popular-pill rounded-pill" data-symptom="dizziness">
                            + Dizziness
                        </button>
                    </div>
                </div>

                <!-- Selected Symptoms Removable Chips Box -->
                <div class="p-3 bg-card-subtle rounded-3 border mb-4">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <span class="fw-bold small text-info">
                            <i class="bi bi-tags-fill me-1"></i> Selected Symptoms (Chips):
                        </span>
                        <button type="button" class="btn btn-sm btn-link text-muted p-0 text-decoration-none" id="clearSymptomsBtn">
                            <i class="bi bi-trash3 me-1"></i> Clear All
                        </button>
                    </div>
                    
                    <div id="selectedSymptomChips" class="d-flex flex-wrap gap-2 min-h-40 align-items-center">
                        <!-- Chips rendered dynamically via JS -->
                    </div>

                    <div id="emptyChipsNotice" class="text-muted small py-2 text-center" style="display: block;">
                        <i class="bi bi-hand-index-thumb me-1"></i> Select at least 2 symptoms from above or browse categories below.
                    </div>
                </div>

                <!-- Optional Clinical Context (Accordion) -->
                <div class="accordion accordion-flush mb-4" id="clinicalContextAccordion">
                    <div class="accordion-item bg-transparent border-0">
                        <h2 class="accordion-header" id="contextHeading">
                            <button class="accordion-button collapsed bg-card-subtle rounded-3 p-3 text-info fw-bold small shadow-none border" type="button" data-bs-toggle="collapse" data-bs-target="#contextCollapse">
                                <i class="bi bi-sliders2 me-2"></i> Optional Clinical Context (Age, Duration, Severity)
                            </button>
                        </h2>
                        <div id="contextCollapse" class="accordion-collapse collapse" data-bs-parent="#clinicalContextAccordion">
                            <div class="accordion-body px-0 pt-3 pb-0">
                                <div class="row g-3">
                                    <div class="col-6 col-md-3">
                                        <label class="form-label small text-muted mb-1" for="contextAgeGroup">Age Group</label>
                                        <select class="form-select form-select-sm" id="contextAgeGroup">
                                            <option value="child">Child (0-12)</option>
                                            <option value="teen">Teen (13-17)</option>
                                            <option value="adult" selected>Adult (18-64)</option>
                                            <option value="older_adult">Older Adult (65+)</option>
                                            <option value="unspecified">Prefer not to say</option>
                                        </select>
                                    </div>
                                    <div class="col-6 col-md-3">
                                        <label class="form-label small text-muted mb-1" for="contextDuration">Duration</label>
                                        <select class="form-select form-select-sm" id="contextDuration">
                                            <option value="less_1_day">Less than 24h</option>
                                            <option value="1_3_days" selected>1–3 days</option>
                                            <option value="4_7_days">4–7 days</option>
                                            <option value="more_1_week">1–2 weeks</option>
                                            <option value="more_2_weeks">&gt; 2 weeks</option>
                                        </select>
                                    </div>
                                    <div class="col-6 col-md-3">
                                        <label class="form-label small text-muted mb-1" for="contextSeverity">Severity</label>
                                        <select class="form-select form-select-sm" id="contextSeverity">
                                            <option value="mild">Mild (Noticeable)</option>
                                            <option value="moderate" selected>Moderate (Disruptive)</option>
                                            <option value="severe">Severe (Incapacitating)</option>
                                        </select>
                                    </div>
                                    <div class="col-6 col-md-3">
                                        <label class="form-label small text-muted mb-1" for="contextTrajectory">Progression</label>
                                        <select class="form-select form-select-sm" id="contextTrajectory">
                                            <option value="better">Getting better</option>
                                            <option value="same" selected>Staying same</option>
                                            <option value="worse">Getting worse</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Body Systems Filter Bar -->
                <div class="mb-3">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <span class="fw-bold small text-muted">Browse by Body System:</span>
                    </div>
                    <div class="d-flex flex-wrap gap-1 mb-3">
                        <button type="button" class="btn btn-sm symptom-category-pill active btn-info text-white" data-category="all">All</button>
                        <button type="button" class="btn btn-sm symptom-category-pill btn-outline-secondary" data-category="general">General</button>
                        <button type="button" class="btn btn-sm symptom-category-pill btn-outline-secondary" data-category="respiratory">Respiratory</button>
                        <button type="button" class="btn btn-sm symptom-category-pill btn-outline-secondary" data-category="cardiovascular">Cardio</button>
                        <button type="button" class="btn btn-sm symptom-category-pill btn-outline-secondary" data-category="gastrointestinal">Digestive</button>
                        <button type="button" class="btn btn-sm symptom-category-pill btn-outline-secondary" data-category="neurological">Neuro</button>
                        <button type="button" class="btn btn-sm symptom-category-pill btn-outline-secondary" data-category="dermatological">Skin</button>
                        <button type="button" class="btn btn-sm symptom-category-pill btn-outline-secondary" data-category="endocrine">Endocrine</button>
                        <button type="button" class="btn btn-sm symptom-category-pill btn-outline-secondary" data-category="musculoskeletal">Musculo</button>
                    </div>

                    <!-- Scrollable Symptom Tiles Grid -->
                    <div id="symptomBrowserContainer" class="symptom-browser-grid p-2 rounded-3 border bg-card-subtle" style="max-height: 240px; overflow-y: auto;">
                        <!-- Rendered by JS -->
                    </div>
                </div>

                <!-- Animated Loading State (Multi-step) -->
                <div id="ai-loading-state" class="ai-loading-container mb-4" style="display: none;">
                    <div class="ai-spinner"></div>
                    <h5 class="fw-bold mb-2">Analyzing Symptom Profile...</h5>
                    <p class="small text-muted mb-3">Evaluating clinical co-occurrence patterns across 73 conditions</p>
                    <div class="ai-loading-steps">
                        <div class="ai-loading-step active" id="loading-step-1">
                            <span class="ai-step-dot"></span>
                            <span>Analyzing selected symptoms...</span>
                        </div>
                        <div class="ai-loading-step" id="loading-step-2">
                            <span class="ai-step-dot"></span>
                            <span>Comparing symptom patterns across 73 conditions...</span>
                        </div>
                        <div class="ai-loading-step" id="loading-step-3">
                            <span class="ai-step-dot"></span>
                            <span>Evaluating differential criteria & weighting...</span>
                        </div>
                        <div class="ai-loading-step" id="loading-step-4">
                            <span class="ai-step-dot"></span>
                            <span>Preparing ranked possible conditions...</span>
                        </div>
                    </div>
                </div>

                <!-- Analyze Button -->
                <button type="button" class="btn btn-primary-custom btn-lg w-100 py-3 fw-bold" id="analyzeSymptomsBtn">
                    <i class="bi bi-cpu-fill me-2"></i> Analyze Symptoms
                </button>
            </div>
        </div>

        <!-- RIGHT COLUMN: RESULTS, OVERLAPPING ADVISORY & FOLLOW-UP QUESTIONS -->
        <div class="col-lg-6">
            <!-- Emergency Alert Box (renders if red flags present) -->
            <div id="emergencyAlertContainer" style="display: none;"></div>

            <!-- Follow-up Questions Container (Refine symptoms) -->
            <div id="refineQuestionsContainer" style="display: none;"></div>

            <!-- Main Results Container -->
            <div id="symptomResultsContainer" style="display: none;">
                <!-- Dynamically filled by JS -->
            </div>

            <!-- Empty State / Awaiting Selection -->
            <div id="emptyResultsContainer" class="card-custom p-5 text-center h-100 d-flex flex-column justify-content-center align-items-center">
                <div class="p-4 bg-info bg-opacity-10 text-info rounded-circle mb-3">
                    <i class="bi bi-activity display-3"></i>
                </div>
                <h4 class="fw-bold mb-2">Awaiting Symptom Selection</h4>
                <p class="text-muted small mb-4" style="max-width: 420px;">
                    Select at least 2 symptoms from the panel on the left. Our clinical co-occurrence matching engine will evaluate overlapping conditions and provide an educational assessment.
                </p>
                <div class="p-3 bg-card-subtle rounded-3 border text-start small w-100" style="max-width: 440px;">
                    <strong class="text-info d-block mb-2"><i class="bi bi-shield-check me-1"></i> System Guardrails:</strong>
                    <ul class="text-muted mb-0 ps-3">
                        <li class="mb-1">Transparent, explainable clinical match scores (not fake probability).</li>
                        <li class="mb-1">Ranks top 3–5 possible conditions considering overlapping symptoms.</li>
                        <li>Identifies emergency red-flag indicators requiring immediate medical care.</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- DATA & METHODOLOGY MODAL -->
<div class="modal fade" id="methodologyModal" tabindex="-1" aria-labelledby="methodologyModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content bg-card border">
            <div class="modal-header border-bottom">
                <h5 class="modal-title fw-bold" id="methodologyModalLabel">
                    <i class="bi bi-diagram-3-fill text-info me-2"></i> Data & Methodology Transparency
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body p-4 text-muted small" style="line-height: 1.6;">
                <h6 class="fw-bold text-primary-theme mb-2">1. Clinical Dataset Provenance</h6>
                <p>
                    The MediSense AI disease catalog incorporates 73 verified clinical conditions and 58 standardized symptom indicators. Clinical feature sets and symptom frequencies are synthesized from evidence-based publications including the <em>Centers for Disease Control and Prevention (CDC) Clinical Guidelines</em>, <em>World Health Organization (WHO) Clinical Practice Handbook</em>, and <em>Harrison's Principles of Internal Medicine</em>.
                </p>

                <h6 class="fw-bold text-primary-theme mb-2">2. Symptom Normalization (Natural Language Processing)</h6>
                <p>
                    Free-form user queries (such as "head ache", "throwing up", or "cold chills") are mapped to standardized clinical symptom keys using a tolerant multi-tier normalization algorithm incorporating synonym indexing, prefix matching, and substring alignment.
                </p>

                <h6 class="fw-bold text-primary-theme mb-2">3. Deterministic Match Scoring Engine</h6>
                <p>
                    Rather than outputting arbitrary probability claims, the matching algorithm computes a calibrated overlap score based on clinical feature weights:
                </p>
                <ul>
                    <li><strong>Characteristic / Core Symptoms:</strong> Weighted at 3.0 points.</li>
                    <li><strong>Secondary / Less-Common Symptoms:</strong> Weighted at 1.5 points.</li>
                    <li><strong>Mismatch Penalty:</strong> Non-matching symptoms reduce precision by 2.0 points.</li>
                    <li><strong>Balanced F0.8 Formulation:</strong> Harmonizes sensitivity and specificity, normalized from 0 to 100.</li>
                </ul>

                <h6 class="fw-bold text-primary-theme mb-2">4. What the Match Score Means (and Does NOT Mean)</h6>
                <p>
                    A score of "85/100" signifies high educational alignment between the patient's reported symptoms and standard medical descriptions of that condition. It is <strong>NOT</strong> a 85% probability of disease. Symptom checkers cannot evaluate physical exam findings, vital signs, or laboratory pathology.
                </p>

                <h6 class="fw-bold text-primary-theme mb-2">5. Handling Overlapping Conditions</h6>
                <p>
                    Because infections, auto-immune conditions, and metabolic disorders frequently share early constitutional symptoms (e.g. fever, fatigue, malaise), MediSense AI displays multiple ranked possibilities and provides differential guidance to assist clinical discussions.
                </p>
            </div>
            <div class="modal-footer border-top">
                <button type="button" class="btn btn-info text-white rounded-pill px-4" data-bs-dismiss="modal">Close</button>
            </div>
        </div>
    </div>
</div>

<script src="assets/js/symptom_prediction.js"></script>

<?php
require_once __DIR__ . '/includes/footer.php';
?>
