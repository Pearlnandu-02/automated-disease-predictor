<?php
require_once __DIR__ . '/includes/header.php';
require_once __DIR__ . '/includes/functions.php';
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

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['symptoms'])) {
    $selected_keys = $_POST['symptoms'];
    if (is_array($selected_keys) && count($selected_keys) > 0) {
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
                    $prediction_result['prediction'],
                    $prediction_result['probability']
                ]);
            } catch (Exception $e) {
                // Ignore DB error for presentation
            }
        }
    } else {
        set_flash_message("Please select at least 1 symptom to run the AI prediction.", "warning");
    }
}
?>

<div class="row py-3">
    <div class="col-lg-12 text-center mb-4">
        <span class="badge bg-info text-dark px-3 py-2 rounded-pill fw-bold mb-2">AI SYMPTOM CHECKER</span>
        <h1 class="display-5 fw-extrabold text-white">Intelligent Multi-Symptom Disease Prediction</h1>
        <p class="lead text-muted mx-auto" style="max-width: 750px;">
            Select your experienced health symptoms below to evaluate potential condition matches using our trained Machine Learning classification pipeline.
        </p>
    </div>
</div>

<div class="row g-4">
    <!-- Form Column -->
    <div class="col-lg-7">
        <div class="card-custom p-4 p-md-5">
            <h4 class="fw-bold text-white mb-3 d-flex align-items-center">
                <i class="bi bi-ui-checks text-info me-2"></i> Select Present Symptoms
            </h4>
            <p class="small text-muted mb-4">Check all symptoms you are currently experiencing:</p>

            <form method="POST" action="prediction.php">
                <?php foreach ($grouped_symptoms as $system => $sym_list): ?>
                    <div class="mb-4">
                        <h6 class="text-info text-uppercase fw-bold small tracking-wider mb-3 pb-1 border-bottom border-secondary border-opacity-25">
                            <i class="bi bi-activity me-1"></i> <?= sanitize($system) ?> System
                        </h6>
                        <div class="row g-2">
                            <?php foreach ($sym_list as $s): ?>
                                <div class="col-md-6">
                                    <div class="form-check p-2 rounded bg-dark bg-opacity-40 border border-secondary border-opacity-25">
                                        <input class="form-check-input ms-1" type="checkbox" name="symptoms[]" value="<?= sanitize($s['symptom_key']) ?>" id="sym_<?= sanitize($s['symptom_key']) ?>">
                                        <label class="form-check-label text-white small ms-2 cursor-pointer" for="sym_<?= sanitize($s['symptom_key']) ?>">
                                            <?= sanitize($s['name']) ?>
                                        </label>
                                    </div>
                                </div>
                            <?php endforeach; ?>
                        </div>
                    </div>
                <?php endforeach; ?>

                <div class="disclaimer-banner my-4">
                    <i class="bi bi-info-circle-fill me-1"></i> By submitting, your selections will be processed through our ML model. AI predictions are strictly educational.
                </div>

                <button type="submit" class="btn btn-primary-custom btn-lg w-100 py-3">
                    <i class="bi bi-cpu-fill me-2"></i> Submit Symptoms & Predict Condition
                </button>
            </form>
        </div>
    </div>

    <!-- Prediction Results Column -->
    <div class="col-lg-5">
        <?php if ($prediction_result): ?>
            <div class="card-custom p-4 text-center border-info mb-4">
                <span class="badge bg-secondary mb-2">AI MODEL OUTPUT</span>
                <h5 class="text-muted text-uppercase fw-bold small">Most Likely Condition</h5>
                <h2 class="display-6 fw-bold text-white my-2"><?= sanitize($prediction_result['prediction']) ?></h2>
                
                <div class="my-3">
                    <span class="display-3 fw-extrabold text-info"><?= $prediction_result['probability'] ?>%</span>
                    <p class="small text-muted mb-0">Model Confidence Probability</p>
                </div>

                <div class="p-3 bg-dark bg-opacity-60 rounded border border-secondary border-opacity-25 my-3 text-start small">
                    <strong class="text-white d-block mb-1"><i class="bi bi-bounding-box-circles me-1 text-info"></i> Influencing Symptoms:</strong>
                    <div class="d-flex flex-wrap gap-1 mt-1">
                        <?php foreach ($prediction_result['influencing_symptoms'] as $inf): ?>
                            <span class="badge bg-info bg-opacity-20 text-info border border-info border-opacity-25"><?= sanitize($inf) ?></span>
                        <?php endforeach; ?>
                    </div>
                </div>

                <?php if (!empty($prediction_result['runner_ups'])): ?>
                    <div class="p-3 bg-dark bg-opacity-40 rounded border border-secondary border-opacity-25 my-3 text-start small">
                        <strong class="text-white d-block mb-2"><i class="bi bi-bar-chart me-1 text-warning"></i> Alternative Possibilities:</strong>
                        <ul class="list-unstyled mb-0">
                            <?php foreach ($prediction_result['runner_ups'] as $rup): ?>
                                <li class="d-flex justify-content-between py-1 border-bottom border-secondary border-opacity-10 text-muted">
                                    <span><?= sanitize($rup['disease']) ?></span>
                                    <span class="fw-bold text-white"><?= $rup['probability'] ?>%</span>
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
                <h6 class="fw-bold mb-2"><i class="bi bi-shield-exclamation text-warning me-1"></i> Important Medical Disclaimer</h6>
                <p class="small mb-0"><?= sanitize($prediction_result['disclaimer']) ?></p>
            </div>

        <?php else: ?>
            <div class="card-custom p-5 text-center h-100 d-flex flex-column justify-content-center align-items-center">
                <i class="bi bi-activity text-info display-1 mb-3 opacity-50"></i>
                <h4 class="text-white fw-bold">Awaiting Symptom Submission</h4>
                <p class="text-muted small max-w-sm mb-0">
                    Select your symptoms from the list on the left and click "Submit Symptoms" to launch the prediction analysis.
                </p>
            </div>
        <?php endif; ?>
    </div>
</div>

<?php
require_once __DIR__ . '/includes/footer.php';
?>
