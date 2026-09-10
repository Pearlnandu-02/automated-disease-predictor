<?php
require_once __DIR__ . '/includes/functions.php';
require_once __DIR__ . '/includes/auth.php';
require_once __DIR__ . '/includes/ml_bridge.php';

$pdo = get_db_connection();

// Fetch symptoms from DB
$symptoms = [];
if ($pdo) {
    try {
        $stmt = $pdo->query("SELECT * FROM symptoms ORDER BY body_system, name ASC");
        $symptoms = $stmt->fetchAll();
    } catch (PDOException $e) {
        $symptoms = [];
    }
}

// Fallback symptoms list if database connection is unavailable
if (empty($symptoms)) {
    $fallback_keys = [
        'high_blood_sugar' => ['High Blood Sugar / Thirst', 'Endocrine'],
        'frequent_urination' => ['Frequent Urination', 'Renal'],
        'high_blood_pressure' => ['High Blood Pressure', 'Cardiovascular'],
        'chest_pain' => ['Chest Pain / Tightness', 'Cardiovascular'],
        'shortness_of_breath' => ['Shortness of Breath / Dyspnea', 'Respiratory'],
        'cough_with_sputum' => ['Persistent Cough with Sputum', 'Respiratory'],
        'hemoptysis' => ['Hemoptysis (Coughing Blood)', 'Respiratory'],
        'fever' => ['Fever (>100.4°F)', 'Systemic'],
        'chills' => ['Severe Chills / Rigors', 'Systemic'],
        'joint_pain' => ['Severe Joint / Bone Pain', 'Musculoskeletal'],
        'headache' => ['Severe Throbbing Headache', 'Neurological'],
        'seizures' => ['Involuntary Electrical Seizures', 'Neurological'],
        'resting_tremor' => ['Resting Hand Tremors', 'Neurological'],
        'memory_loss' => ['Progressive Memory Loss', 'Neurological'],
        'wheezing' => ['Respiratory Wheezing', 'Respiratory'],
        'heartburn' => ['Gastric Heartburn / Acid Reflux', 'Gastrointestinal'],
        'jaundice' => ['Jaundice (Yellowing Eyes/Skin)', 'Hepatic'],
        'right_upper_quadrant_pain' => ['Right Upper Quadrant Abdominal Pain', 'Hepatic'],
        'flank_pain' => ['Flank / Low Back Pain', 'Renal'],
        'dysuria' => ['Dysuria (Painful Urination)', 'Renal'],
        'fatigue' => ['Chronic Lethargy & Fatigue', 'Systemic'],
        'cold_intolerance' => ['Cold Intolerance', 'Endocrine'],
        'heat_intolerance' => ['Heat Intolerance / Sweating', 'Endocrine'],
        'palpitations' => ['Rapid Heart Palpitations', 'Cardiovascular'],
        'weight_loss' => ['Unexplained Rapid Weight Loss', 'Systemic'],
        'sweats' => ['Drenching Night Sweats', 'Systemic']
    ];
    foreach ($fallback_keys as $k => $info) {
        $symptoms[] = [
            'symptom_key' => $k,
            'name' => $info[0],
            'body_system' => $info[1]
        ];
    }
}

// Group symptoms by body_system
$grouped_symptoms = [];
foreach ($symptoms as $sym) {
    $sys = $sym['body_system'];
    $grouped_symptoms[$sys][] = $sym;
}

$prediction_result = null;
$selected_keys = [];

// Check for pre-selection via URL parameter (e.g. from Symptoms Guide)
if (isset($_GET['symptom']) && !empty($_GET['symptom'])) {
    $clean_get = preg_replace('/[^a-zA-Z0-9_]/', '', trim($_GET['symptom']));
    if (!empty($clean_get)) {
        $selected_keys[] = $clean_get;
    }
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $raw_symptoms = $_POST['symptoms'] ?? [];
    if (!is_array($raw_symptoms)) {
        $raw_symptoms = [$raw_symptoms];
    }
    
    // Sanitize symptom keys (alphanumeric and underscores only)
    $selected_keys = [];
    foreach ($raw_symptoms as $sk) {
        $clean = preg_replace('/[^a-zA-Z0-9_]/', '', trim($sk));
        if (!empty($clean)) {
            $selected_keys[] = $clean;
        }
    }
    $selected_keys = array_values(array_unique($selected_keys));

    if (!empty($selected_keys)) {
        $prediction_result = call_symptom_prediction($selected_keys);
        
        // Save to DB history if user logged in
        if (is_logged_in() && $pdo) {
            try {
                $user = get_logged_in_user();
                $sym_str = implode(', ', array_map(function($k) { return ucwords(str_replace('_', ' ', $k)); }, $selected_keys));
                $stmt = $pdo->prepare("INSERT INTO prediction_history (user_id, symptoms_selected, predicted_disease, confidence) VALUES (?, ?, ?, ?)");
                $stmt->execute([
                    $user['id'],
                    $sym_str,
                    $prediction_result['prediction'] ?? 'Unknown',
                    $prediction_result['probability'] ?? 0.0
                ]);
            } catch (Exception $e) {
                // Silently bypass history logging error
            }
        }
    } else {
        set_flash_message('warning', 'Please select at least 1 symptom tile below to run the AI model prediction.');
    }
}

$selected_lookup = array_flip($selected_keys);

$page_title = 'MediSense AI | AI Prediction';
require_once __DIR__ . '/includes/header.php';
?>

<div class="row py-3">
    <div class="col-lg-12 text-center mb-4">
        <span class="badge hero-badge px-3 py-2 rounded-pill fw-bold mb-2">AI SYMPTOM CHECKER</span>
        <h1 class="display-5 fw-extrabold mb-2">Intelligent Multi-Symptom Disease Prediction</h1>
        <p class="lead text-muted mx-auto" style="max-width: 750px;">
            Click the symptom tiles below to select your present indicators. Our clinical classification model evaluates co-occurrence patterns to estimate potential conditions.
        </p>
    </div>
</div>

<div class="row g-4">
    <!-- Form Column with Matte/Glossy Symptom Tiles -->
    <div class="col-lg-7">
        <div class="card-custom p-4 p-md-5">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h4 class="fw-bold mb-0 d-flex align-items-center">
                    <i class="bi bi-grid-3x3-gap-fill text-info me-2"></i> Select Present Symptoms
                </h4>
                <span class="badge bg-secondary bg-opacity-50 text-muted small" id="selected-count-badge">
                    Click tiles to select
                </span>
            </div>
            <p class="small text-muted mb-4">
                Click any tile to toggle. Unselected tiles are matte; selected tiles illuminate with a glossy finish (no conventional checkboxes):
            </p>

            <form method="POST" action="prediction.php" class="prediction-form" id="predictionForm">
                <?php foreach ($grouped_symptoms as $system => $sym_list): ?>
                    <div class="mb-4">
                        <h6 class="text-info text-uppercase fw-bold small tracking-wider mb-3 pb-1 border-bottom border-secondary border-opacity-25 d-flex align-items-center">
                            <i class="bi bi-activity me-2"></i> <?= sanitize($system) ?> System
                        </h6>
                        <div class="symptom-grid">
                            <?php foreach ($sym_list as $s): ?>
                                <?php $is_checked = isset($selected_lookup[$s['symptom_key']]); ?>
                                <label class="symptom-tile <?= $is_checked ? 'selected' : '' ?>" tabindex="0" role="checkbox" aria-checked="<?= $is_checked ? 'true' : 'false' ?>" id="tile_<?= sanitize($s['symptom_key']) ?>">
                                    <input 
                                        type="checkbox" 
                                        name="symptoms[]" 
                                        value="<?= sanitize($s['symptom_key']) ?>" 
                                        id="sym_<?= sanitize($s['symptom_key']) ?>" 
                                        class="symptom-checkbox visually-hidden"
                                        <?= $is_checked ? 'checked' : '' ?>
                                    >
                                    <div class="symptom-tile-gloss"></div>
                                    <span class="symptom-tile-name"><?= sanitize($s['name']) ?></span>
                                </label>
                            <?php endforeach; ?>
                        </div>
                    </div>
                <?php endforeach; ?>

                <div class="disclaimer-banner my-4">
                    <i class="bi bi-info-circle-fill me-1 text-info"></i> Predictions are generated using an automated Random Forest classifier trained on clinical co-occurrence patterns. Results are strictly educational.
                </div>

                <!-- Animated Loading State (Multi-step) -->
                <div id="ai-loading-state" class="ai-loading-container mb-4" style="display: none;">
                    <div class="ai-spinner"></div>
                    <h5 class="fw-bold mb-2">Analyzing Symptom Profile...</h5>
                    <p class="small text-muted mb-3">Evaluating clinical features through the diagnostic classifier</p>
                    <div class="ai-loading-steps">
                        <div class="ai-loading-step active" id="loading-step-1">
                            <span class="ai-step-dot"></span>
                            <span>Analyzing selected symptoms...</span>
                        </div>
                        <div class="ai-loading-step" id="loading-step-2">
                            <span class="ai-step-dot"></span>
                            <span>Processing symptom pattern...</span>
                        </div>
                        <div class="ai-loading-step" id="loading-step-3">
                            <span class="ai-step-dot"></span>
                            <span>Generating model prediction...</span>
                        </div>
                        <div class="ai-loading-step" id="loading-step-4">
                            <span class="ai-step-dot"></span>
                            <span>Preparing result...</span>
                        </div>
                    </div>
                </div>

                <button type="submit" class="btn btn-primary-custom btn-lg w-100 py-3" id="predictSubmitBtn">
                    <i class="bi bi-cpu-fill me-2"></i> Submit Symptoms & Predict Condition
                </button>
            </form>
        </div>
    </div>

    <!-- Prediction Results Column -->
    <div class="col-lg-5">
        <?php if ($prediction_result): ?>
            <?php if (isset($prediction_result['error'])): ?>
                <div class="card-custom p-4 text-center border-danger mb-4">
                    <i class="bi bi-exclamation-triangle-fill text-warning display-4 mb-3"></i>
                    <h4 class="fw-bold">Service Notice</h4>
                    <p class="text-muted small mb-0">
                        <?= sanitize($prediction_result['error']) ?>
                    </p>
                </div>
            <?php elseif (($prediction_result['status'] ?? '') === 'insufficient_information' || ($prediction_result['prediction'] ?? '') === 'Insufficient Information'): ?>
                <div class="card-custom p-4 p-md-5 text-center border-warning mb-4">
                    <span class="badge bg-warning bg-opacity-20 text-warning border border-warning border-opacity-25 mb-3 px-3 py-1 fw-bold">
                        <i class="bi bi-exclamation-circle-fill me-1"></i> INSUFFICIENT INFORMATION
                    </span>
                    <h3 class="fw-bold mb-2">Additional Symptoms Needed</h3>
                    <p class="text-muted small mb-4">
                        <?= sanitize($prediction_result['message'] ?? 'A single symptom or non-specific combination does not provide enough statistical evidence across our 65 condition categories. Please select 2 or more symptoms to evaluate.') ?>
                    </p>

                    <div class="p-3 bg-card-subtle rounded border border-secondary border-opacity-25 text-start small mb-4">
                        <strong class="text-info d-block mb-2"><i class="bi bi-lightbulb-fill me-1"></i> Suggested Actions:</strong>
                        <ul class="mb-0 ps-3 text-muted">
                            <li class="mb-1">Select additional active symptoms from the tiles on the left.</li>
                            <li class="mb-1">Explore our <a href="symptoms_guide.php" class="text-info text-decoration-underline">Symptoms Guide</a> to view commonly associated signs.</li>
                            <li>For any concerning symptoms, consult a qualified physician or healthcare professional.</li>
                        </ul>
                    </div>

                    <div class="d-flex justify-content-between align-items-center text-muted small border-top border-secondary border-opacity-25 pt-3">
                        <span><i class="bi bi-cpu me-1"></i> <?= sanitize($prediction_result['model_version'] ?? 'Multi-Disease Prediction Model v2') ?></span>
                        <span class="badge bg-secondary bg-opacity-25 text-info">65 Supported Conditions</span>
                    </div>
                </div>

                <div class="disclaimer-banner p-4 text-start">
                    <h6 class="fw-bold mb-2 text-warning"><i class="bi bi-shield-exclamation me-1"></i> Important Medical Disclaimer</h6>
                    <p class="small mb-0 text-muted">
                        <?= sanitize($prediction_result['disclaimer'] ?? 'These results are educational predictions based on the information provided and are not a medical diagnosis. Symptoms can have many causes. Please consult a qualified healthcare professional for proper diagnosis and treatment.') ?>
                    </p>
                </div>
            <?php else: ?>
                <div class="card-custom p-4 text-center border-info mb-4">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <span class="badge bg-secondary px-3 py-1">AI MODEL OUTPUT</span>
                        <span class="badge bg-info bg-opacity-20 text-info border border-info border-opacity-25 small">
                            <?= sanitize($prediction_result['model_version'] ?? 'Multi-Disease Model v2') ?>
                        </span>
                    </div>
                    <h5 class="text-muted text-uppercase fw-bold small mt-2">Most Likely Condition (AI Classification)</h5>
                    <h2 class="display-6 fw-bold my-2"><?= sanitize($prediction_result['prediction']) ?></h2>
                    
                    <div class="my-3 py-2 border-top border-bottom border-secondary border-opacity-25">
                        <span 
                            class="display-3 fw-extrabold text-info counter-text animate-counter" 
                            data-target="<?= htmlspecialchars(number_format((float)$prediction_result['probability'], 1, '.', '')) ?>"
                        >
                            00.0%
                        </span>
                        <p class="small text-muted mb-0 mt-1">Calculated model likelihood score across 65 conditions</p>
                    </div>

                    <?php if (!empty($prediction_result['influencing_symptoms'])): ?>
                        <div class="p-3 bg-card-subtle rounded border border-secondary border-opacity-25 my-3 text-start small">
                            <strong class="text-primary-theme d-block mb-1">
                                <i class="bi bi-bounding-box-circles me-1 text-info"></i> Influencing Symptoms Detected:
                            </strong>
                            <div class="d-flex flex-wrap gap-1 mt-2">
                                <?php foreach ($prediction_result['influencing_symptoms'] as $inf): ?>
                                    <span class="badge bg-info bg-opacity-20 text-info border border-info border-opacity-25 px-2 py-1">
                                        <?= sanitize(ucwords(str_replace('_', ' ', $inf))) ?>
                                    </span>
                                <?php endforeach; ?>
                            </div>
                        </div>
                    <?php endif; ?>

                    <?php if (!empty($prediction_result['runner_ups'])): ?>
                        <div class="p-3 bg-card-subtle rounded border border-secondary border-opacity-25 my-3 text-start small">
                            <strong class="text-primary-theme d-block mb-2">
                                <i class="bi bi-bar-chart me-1 text-warning"></i> Other Possible Matches Considered:
                            </strong>
                            <ul class="list-unstyled mb-0">
                                <?php foreach ($prediction_result['runner_ups'] as $rup): ?>
                                    <li class="d-flex justify-content-between py-1 border-bottom border-secondary border-opacity-10 text-muted">
                                        <span><?= sanitize($rup['disease']) ?></span>
                                        <span class="fw-bold text-primary-theme"><?= number_format((float)$rup['probability'], 1) ?>%</span>
                                    </li>
                                <?php endforeach; ?>
                            </ul>
                        </div>
                    <?php endif; ?>

                    <a href="disease_detail.php?name=<?= urlencode($prediction_result['prediction']) ?>" class="btn btn-outline-info rounded-pill px-4 w-100 my-2">
                        <i class="bi bi-book me-1"></i> Learn More About <?= sanitize($prediction_result['prediction']) ?>
                    </a>
                </div>

                <div class="disclaimer-banner p-4 text-start">
                    <h6 class="fw-bold mb-2 text-warning"><i class="bi bi-shield-exclamation me-1"></i> Important Medical Disclaimer</h6>
                    <p class="small mb-0 text-muted">
                        <?= sanitize($prediction_result['disclaimer'] ?? 'These results are educational predictions based on the information provided and are not a medical diagnosis. Symptoms can have many causes. Please consult a qualified healthcare professional for proper diagnosis and treatment.') ?>
                    </p>
                </div>
            <?php endif; ?>

        <?php else: ?>
            <div class="card-custom p-5 text-center h-100 d-flex flex-column justify-content-center align-items-center">
                <i class="bi bi-activity text-info display-1 mb-3 opacity-50"></i>
                <h4 class="fw-bold">Awaiting Symptom Selection</h4>
                <p class="text-muted small max-w-sm mb-0">
                    Click on the symptom tiles on the left to select your active indicators, then click "Submit Symptoms" to evaluate with our AI diagnostic model.
                </p>
            </div>
        <?php endif; ?>
    </div>
</div>

<?php
require_once __DIR__ . '/includes/footer.php';
?>
