<?php
// simulator.php
require_once __DIR__ . '/includes/auth.php';
require_once __DIR__ . '/includes/ml_bridge.php';

require_login();

$user_id = $_SESSION['user_id'];
$from_id = intval($_GET['from'] ?? 0);

$disease_type = sanitize($_GET['type'] ?? 'diabetes');
$input_params = [
    'Glucose' => 145,
    'BMI' => 31.0,
    'BloodPressure' => 82,
    'Age' => 45,
    'Pregnancies' => 2,
    'Insulin' => 90,
    'SkinThickness' => 25,
    'DiabetesPedigreeFunction' => 0.52
];

if ($from_id > 0) {
    $db = Database::getInstance();
    $stmt = $db->prepare("SELECT * FROM health_assessments WHERE id = ? AND user_id = ?");
    $stmt->execute([$from_id, $user_id]);
    $base_assessment = $stmt->fetch();
    if ($base_assessment) {
        $dname = strtolower($base_assessment['disease']);
        if (strpos($dname, 'heart') !== false) {
            $disease_type = 'heart';
        } elseif (strpos($dname, 'hyper') !== false) {
            $disease_type = 'hypertension';
        } elseif (strpos($dname, 'resp') !== false || strpos($dname, 'pulm') !== false) {
            $disease_type = 'respiratory';
        } elseif (strpos($dname, 'life') !== false) {
            $disease_type = 'lifestyle';
        } else {
            $disease_type = 'diabetes';
        }
        $saved = json_decode($base_assessment['input_data'], true);
        if ($saved) {
            $input_params = array_merge($input_params, $saved);
        }
    }
}

$simulation_result = null;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $disease_type = sanitize($_POST['disease_type'] ?? 'diabetes');
    
    if ($disease_type === 'diabetes') {
        $input_params = [
            'Pregnancies' => floatval($_POST['Pregnancies'] ?? 2),
            'Glucose' => floatval($_POST['Glucose'] ?? 145),
            'BloodPressure' => floatval($_POST['BloodPressure'] ?? 82),
            'SkinThickness' => floatval($_POST['SkinThickness'] ?? 25),
            'Insulin' => floatval($_POST['Insulin'] ?? 90),
            'BMI' => floatval($_POST['BMI'] ?? 31.0),
            'DiabetesPedigreeFunction' => floatval($_POST['DiabetesPedigreeFunction'] ?? 0.52),
            'Age' => floatval($_POST['Age'] ?? 45),
        ];
    } elseif ($disease_type === 'heart') {
        $input_params = [
            'age' => floatval($_POST['age'] ?? 52),
            'sex' => intval($_POST['sex'] ?? 1),
            'cp' => intval($_POST['cp'] ?? 0),
            'trestbps' => floatval($_POST['trestbps'] ?? 135),
            'chol' => floatval($_POST['chol'] ?? 240),
            'fbs' => intval($_POST['fbs'] ?? 0),
            'restecg' => intval($_POST['restecg'] ?? 0),
            'thalach' => floatval($_POST['thalach'] ?? 145),
            'exang' => intval($_POST['exang'] ?? 0),
            'oldpeak' => floatval($_POST['oldpeak'] ?? 1.2),
            'slope' => intval($_POST['slope'] ?? 1),
            'ca' => intval($_POST['ca'] ?? 0),
            'thal' => intval($_POST['thal'] ?? 2),
        ];
    } elseif ($disease_type === 'hypertension') {
        $input_params = [
            'systolic' => floatval($_POST['systolic'] ?? 135),
            'diastolic' => floatval($_POST['diastolic'] ?? 85),
            'Age' => floatval($_POST['Age'] ?? 48),
            'BMI' => floatval($_POST['BMI'] ?? 27.5),
            'sodium' => floatval($_POST['sodium'] ?? 2900),
            'smoking' => intval($_POST['smoking'] ?? 0),
            'stress' => intval($_POST['stress'] ?? 1),
        ];
    } elseif ($disease_type === 'respiratory') {
        $input_params = [
            'Age' => floatval($_POST['Age'] ?? 48),
            'pack_years' => floatval($_POST['pack_years'] ?? 8),
            'dyspnea' => intval($_POST['dyspnea'] ?? 2),
            'cough_weeks' => floatval($_POST['cough_weeks'] ?? 3),
            'env_exposure' => intval($_POST['env_exposure'] ?? 1),
        ];
    } elseif ($disease_type === 'lifestyle') {
        $input_params = [
            'age_group' => intval($_POST['age_group'] ?? 2),
            'smoking' => intval($_POST['smoking'] ?? 1),
            'physical_activity' => intval($_POST['physical_activity'] ?? 1),
            'family_history' => intval($_POST['family_history'] ?? 1),
            'bp_category' => intval($_POST['bp_category'] ?? 1),
            'bmi_category' => intval($_POST['bmi_category'] ?? 2),
            'blood_sugar' => intval($_POST['blood_sugar'] ?? 1),
            'cholesterol' => intval($_POST['cholesterol'] ?? 1),
            'diet_quality' => intval($_POST['diet_quality'] ?? 1),
            'sleep_stress' => intval($_POST['sleep_stress'] ?? 1),
            'chronic_conditions' => intval($_POST['chronic_conditions'] ?? 0),
        ];
    }

    $simulation_result = call_ml_prediction($disease_type, $input_params);
}

$page_title = 'MediSense AI | Health Simulator';
require_once __DIR__ . '/includes/header.php';
?>

<div class="row justify-content-center py-4">
    <div class="col-lg-10">
        <div class="card card-custom p-4 p-md-5 mb-4 shadow-lg">
            <div class="d-flex align-items-center mb-4 pb-3 border-bottom border-secondary border-opacity-25">
                <div class="bg-primary bg-opacity-10 p-3 rounded-circle text-info me-3">
                    <i class="bi bi-sliders fs-2"></i>
                </div>
                <div>
                    <h3 class="fw-bold mb-0">What-If Health Risk Simulator</h3>
                    <p class="text-muted small mb-0">Modify health parameters interactively to observe real-time hypothetical changes in risk probability</p>
                </div>
            </div>

            <div class="disclaimer-banner mb-4">
                <i class="bi bi-info-circle-fill me-1 text-warning"></i>
                <strong>Hypothetical Simulation Notice:</strong> This simulator demonstrates how mathematical model probabilities shift when biometric parameters vary. Changing these sliders simulates statistical variance and does not replace medical treatment.
            </div>

            <form action="simulator.php<?= $from_id > 0 ? '?from='.$from_id : '' ?>" method="POST" id="simulatorForm">
                <!-- Condition Switcher (5 Rich Options) -->
                <div class="mb-4 p-3 rounded-3 border bg-card-subtle">
                    <label class="form-label fw-bold fs-6 mb-2">
                        <i class="bi bi-activity text-info me-2"></i>Select Target Simulation Model:
                    </label>
                    <select name="disease_type" class="form-select form-select-lg" onchange="window.location.href='simulator.php?type=' + this.value;">
                        <option value="diabetes" <?= $disease_type === 'diabetes' ? 'selected' : '' ?>>
                            1. Type 2 Diabetes Risk Simulator (Glucose, BMI, Blood Pressure, Age)
                        </option>
                        <option value="heart" <?= $disease_type === 'heart' ? 'selected' : '' ?>>
                            2. Coronary Heart Disease Simulator (Cholesterol, Resting BP, Max Heart Rate, Age)
                        </option>
                        <option value="hypertension" <?= $disease_type === 'hypertension' ? 'selected' : '' ?>>
                            3. Hypertension & Vascular Simulator (Systolic BP, Diastolic BP, Sodium, BMI, Age)
                        </option>
                        <option value="respiratory" <?= $disease_type === 'respiratory' ? 'selected' : '' ?>>
                            4. Pulmonary & Respiratory Health Simulator (Smoking Pack-Years, Dyspnea, Cough, Age)
                        </option>
                        <option value="lifestyle" <?= $disease_type === 'lifestyle' ? 'selected' : '' ?>>
                            5. Comprehensive Multi-Factor Chronic Risk Simulator (11 Lifestyle & Biomarker Inputs)
                        </option>
                    </select>
                </div>

                <!-- 1. DIABETES SIMULATOR -->
                <?php if ($disease_type === 'diabetes'): ?>
                    <h5 class="fw-bold text-info mb-3"><i class="bi bi-droplet-fill me-2 text-danger"></i>Adjust Diabetes Health Sliders:</h5>
                    <div class="row g-4 mb-4">
                        <div class="col-md-6">
                            <label class="form-label d-flex justify-content-between align-items-center">
                                <span>Glucose Level (mg/dL)</span>
                                <span class="slider-val-badge" id="val_glucose"><?= $input_params['Glucose'] ?? 145 ?></span>
                            </label>
                            <input type="range" class="form-range sync-slider" data-target="val_glucose" min="70" max="250" step="1" name="Glucose" value="<?= $input_params['Glucose'] ?? 145 ?>">
                        </div>

                        <div class="col-md-6">
                            <label class="form-label d-flex justify-content-between align-items-center">
                                <span>Body Mass Index (BMI)</span>
                                <span class="slider-val-badge" id="val_bmi"><?= $input_params['BMI'] ?? 31.0 ?></span>
                            </label>
                            <input type="range" class="form-range sync-slider" data-target="val_bmi" min="15" max="50" step="0.5" name="BMI" value="<?= $input_params['BMI'] ?? 31.0 ?>">
                        </div>

                        <div class="col-md-6">
                            <label class="form-label d-flex justify-content-between align-items-center">
                                <span>Diastolic Blood Pressure (mm Hg)</span>
                                <span class="slider-val-badge" id="val_bp"><?= $input_params['BloodPressure'] ?? 82 ?></span>
                            </label>
                            <input type="range" class="form-range sync-slider" data-target="val_bp" min="50" max="130" step="1" name="BloodPressure" value="<?= $input_params['BloodPressure'] ?? 82 ?>">
                        </div>

                        <!-- Diabetes Age Slider: Works smoothly, updates live, exact numeric value -->
                        <div class="col-md-6">
                            <label class="form-label d-flex justify-content-between align-items-center">
                                <span>Age (Years)</span>
                                <span class="slider-val-badge" id="val_age"><?= $input_params['Age'] ?? 45 ?></span>
                            </label>
                            <input 
                                type="range" 
                                class="form-range sync-slider" 
                                data-target="val_age" 
                                min="1" 
                                max="100" 
                                step="1" 
                                name="Age" 
                                id="age_slider" 
                                value="<?= $input_params['Age'] ?? 45 ?>"
                            >
                        </div>
                    </div>

                <!-- 2. HEART DISEASE SIMULATOR -->
                <?php elseif ($disease_type === 'heart'): ?>
                    <h5 class="fw-bold text-info mb-3"><i class="bi bi-heart-pulse-fill me-2 text-danger"></i>Adjust Cardiovascular Sliders:</h5>
                    <div class="row g-4 mb-4">
                        <div class="col-md-6">
                            <label class="form-label d-flex justify-content-between align-items-center">
                                <span>Serum Cholesterol (mg/dL)</span>
                                <span class="slider-val-badge" id="val_chol"><?= $input_params['chol'] ?? 240 ?></span>
                            </label>
                            <input type="range" class="form-range sync-slider" data-target="val_chol" min="120" max="400" step="1" name="chol" value="<?= $input_params['chol'] ?? 240 ?>">
                        </div>

                        <div class="col-md-6">
                            <label class="form-label d-flex justify-content-between align-items-center">
                                <span>Resting Blood Pressure (mm Hg)</span>
                                <span class="slider-val-badge" id="val_trestbps"><?= $input_params['trestbps'] ?? 135 ?></span>
                            </label>
                            <input type="range" class="form-range sync-slider" data-target="val_trestbps" min="90" max="200" step="1" name="trestbps" value="<?= $input_params['trestbps'] ?? 135 ?>">
                        </div>

                        <div class="col-md-6">
                            <label class="form-label d-flex justify-content-between align-items-center">
                                <span>Max Heart Rate Achieved (Thalach)</span>
                                <span class="slider-val-badge" id="val_thalach"><?= $input_params['thalach'] ?? 145 ?></span>
                            </label>
                            <input type="range" class="form-range sync-slider" data-target="val_thalach" min="80" max="210" step="1" name="thalach" value="<?= $input_params['thalach'] ?? 145 ?>">
                        </div>

                        <div class="col-md-6">
                            <label class="form-label d-flex justify-content-between align-items-center">
                                <span>Age (Years)</span>
                                <span class="slider-val-badge" id="val_age_h"><?= $input_params['age'] ?? 52 ?></span>
                            </label>
                            <input type="range" class="form-range sync-slider" data-target="val_age_h" min="20" max="90" step="1" name="age" value="<?= $input_params['age'] ?? 52 ?>">
                        </div>
                    </div>

                <!-- 3. HYPERTENSION SIMULATOR -->
                <?php elseif ($disease_type === 'hypertension'): ?>
                    <h5 class="fw-bold text-info mb-3"><i class="bi bi-speedometer2 me-2 text-warning"></i>Adjust Hypertension Sliders:</h5>
                    <div class="row g-4 mb-4">
                        <div class="col-md-6">
                            <label class="form-label d-flex justify-content-between align-items-center">
                                <span>Systolic Blood Pressure (mm Hg)</span>
                                <span class="slider-val-badge" id="val_sys"><?= $input_params['systolic'] ?? 135 ?></span>
                            </label>
                            <input type="range" class="form-range sync-slider" data-target="val_sys" min="90" max="210" step="1" name="systolic" value="<?= $input_params['systolic'] ?? 135 ?>">
                        </div>

                        <div class="col-md-6">
                            <label class="form-label d-flex justify-content-between align-items-center">
                                <span>Diastolic Blood Pressure (mm Hg)</span>
                                <span class="slider-val-badge" id="val_dia"><?= $input_params['diastolic'] ?? 85 ?></span>
                            </label>
                            <input type="range" class="form-range sync-slider" data-target="val_dia" min="50" max="130" step="1" name="diastolic" value="<?= $input_params['diastolic'] ?? 85 ?>">
                        </div>

                        <div class="col-md-6">
                            <label class="form-label d-flex justify-content-between align-items-center">
                                <span>Estimated Daily Sodium Intake (mg)</span>
                                <span class="slider-val-badge" id="val_sod"><?= $input_params['sodium'] ?? 2900 ?></span>
                            </label>
                            <input type="range" class="form-range sync-slider" data-target="val_sod" min="1000" max="6000" step="50" name="sodium" value="<?= $input_params['sodium'] ?? 2900 ?>">
                        </div>

                        <div class="col-md-6">
                            <label class="form-label d-flex justify-content-between align-items-center">
                                <span>Age (Years)</span>
                                <span class="slider-val-badge" id="val_age_hyp"><?= $input_params['Age'] ?? 48 ?></span>
                            </label>
                            <input type="range" class="form-range sync-slider" data-target="val_age_hyp" min="18" max="95" step="1" name="Age" value="<?= $input_params['Age'] ?? 48 ?>">
                        </div>
                    </div>

                <!-- 4. RESPIRATORY SIMULATOR -->
                <?php elseif ($disease_type === 'respiratory'): ?>
                    <h5 class="fw-bold text-info mb-3"><i class="bi bi-lungs me-2 text-info"></i>Adjust Pulmonary Health Parameters:</h5>
                    <div class="row g-4 mb-4">
                        <div class="col-md-6">
                            <label class="form-label d-flex justify-content-between align-items-center">
                                <span>Smoking Pack-Years</span>
                                <span class="slider-val-badge" id="val_pack"><?= $input_params['pack_years'] ?? 8 ?></span>
                            </label>
                            <input type="range" class="form-range sync-slider" data-target="val_pack" min="0" max="50" step="1" name="pack_years" value="<?= $input_params['pack_years'] ?? 8 ?>">
                        </div>

                        <div class="col-md-6">
                            <label class="form-label d-flex justify-content-between align-items-center">
                                <span>Persistent Cough Duration (Weeks)</span>
                                <span class="slider-val-badge" id="val_cough"><?= $input_params['cough_weeks'] ?? 3 ?></span>
                            </label>
                            <input type="range" class="form-range sync-slider" data-target="val_cough" min="0" max="20" step="1" name="cough_weeks" value="<?= $input_params['cough_weeks'] ?? 3 ?>">
                        </div>

                        <div class="col-md-6">
                            <label class="form-label d-flex justify-content-between align-items-center">
                                <span>Dyspnea Grade (0 = Strenuous Only, 4 = Severe)</span>
                                <span class="slider-val-badge" id="val_dyspnea"><?= $input_params['dyspnea'] ?? 2 ?></span>
                            </label>
                            <input type="range" class="form-range sync-slider" data-target="val_dyspnea" min="0" max="4" step="1" name="dyspnea" value="<?= $input_params['dyspnea'] ?? 2 ?>">
                        </div>

                        <div class="col-md-6">
                            <label class="form-label d-flex justify-content-between align-items-center">
                                <span>Age (Years)</span>
                                <span class="slider-val-badge" id="val_age_resp"><?= $input_params['Age'] ?? 48 ?></span>
                            </label>
                            <input type="range" class="form-range sync-slider" data-target="val_age_resp" min="18" max="95" step="1" name="Age" value="<?= $input_params['Age'] ?? 48 ?>">
                        </div>
                    </div>

                <!-- 5. LIFESTYLE MULTI-FACTOR SIMULATOR -->
                <?php elseif ($disease_type === 'lifestyle'): ?>
                    <h5 class="fw-bold text-info mb-3"><i class="bi bi-heart-half me-2 text-success"></i>Adjust Lifestyle Multi-Factor Indicators:</h5>
                    <div class="row g-4 mb-4">
                        <div class="col-md-6">
                            <label class="form-label">Physical Activity Level</label>
                            <select name="physical_activity" class="form-select">
                                <option value="3" <?= ($input_params['physical_activity'] ?? 1) == 3 ? 'selected' : '' ?>>Very Active (>=150m/wk)</option>
                                <option value="2" <?= ($input_params['physical_activity'] ?? 1) == 2 ? 'selected' : '' ?>>Moderate (90-150m/wk)</option>
                                <option value="1" <?= ($input_params['physical_activity'] ?? 1) == 1 ? 'selected' : '' ?>>Light (30-90m/wk)</option>
                                <option value="0" <?= ($input_params['physical_activity'] ?? 1) == 0 ? 'selected' : '' ?>>Sedentary (<30m/wk)</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Smoking Status</label>
                            <select name="smoking" class="form-select">
                                <option value="0" <?= ($input_params['smoking'] ?? 0) == 0 ? 'selected' : '' ?>>Never Smoked</option>
                                <option value="1" <?= ($input_params['smoking'] ?? 0) == 1 ? 'selected' : '' ?>>Former Smoker</option>
                                <option value="2" <?= ($input_params['smoking'] ?? 0) == 2 ? 'selected' : '' ?>>Occasional Smoker</option>
                                <option value="3" <?= ($input_params['smoking'] ?? 0) == 3 ? 'selected' : '' ?>>Daily Active Smoker</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Diet & Nutrition Profile</label>
                            <select name="diet_quality" class="form-select">
                                <option value="0" <?= ($input_params['diet_quality'] ?? 1) == 0 ? 'selected' : '' ?>>Optimal Mediterranean / Whole Foods</option>
                                <option value="1" <?= ($input_params['diet_quality'] ?? 1) == 1 ? 'selected' : '' ?>>Average Mixed Diet</option>
                                <option value="2" <?= ($input_params['diet_quality'] ?? 1) == 2 ? 'selected' : '' ?>>High Sodium & Ultra-Processed</option>
                                <option value="3" <?= ($input_params['diet_quality'] ?? 1) == 3 ? 'selected' : '' ?>>High Sugar & Refined Carbohydrates</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Sleep & Chronic Stress State</label>
                            <select name="sleep_stress" class="form-select">
                                <option value="0" <?= ($input_params['sleep_stress'] ?? 1) == 0 ? 'selected' : '' ?>>Restful 7-9h / Low Stress</option>
                                <option value="1" <?= ($input_params['sleep_stress'] ?? 1) == 1 ? 'selected' : '' ?>>6-7h / Moderate Stress</option>
                                <option value="2" <?= ($input_params['sleep_stress'] ?? 1) == 2 ? 'selected' : '' ?>><6h / Chronic High Stress</option>
                            </select>
                        </div>
                    </div>
                <?php endif; ?>

                <button type="submit" class="btn btn-primary-custom btn-lg w-100 shadow py-3">
                    <i class="bi bi-arrow-repeat me-2"></i> Recalculate Simulated Risk Score
                </button>
            </form>
        </div>

        <!-- Simulation Results Section -->
        <?php if ($simulation_result && !isset($simulation_result['error'])): ?>
            <div class="card card-custom p-4 p-md-5 mb-4 shadow-lg border-info">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <span class="badge bg-secondary px-3 py-1">SIMULATION OUTPUT</span>
                    <span class="badge-risk-<?= strtoupper($simulation_result['risk_level']) ?>">
                        Risk Category: <?= strtoupper($simulation_result['risk_level']) ?>
                    </span>
                </div>

                <div class="text-center my-3">
                    <h5 class="text-muted text-uppercase fw-bold small"><?= sanitize($simulation_result['disease']) ?></h5>
                    <h1 class="display-3 fw-extrabold text-info my-2 counter-text animate-counter" data-target="<?= number_format($simulation_result['probability'], 1) ?>">
                        <?= number_format($simulation_result['probability'], 1) ?>%
                    </h1>
                    <p class="small text-muted mb-0">Model Confidence / Statistical Risk Probability</p>
                </div>

                <div class="disclaimer-banner my-3 text-start small">
                    <i class="bi bi-info-circle-fill me-1 text-warning"></i>
                    <?= sanitize($simulation_result['disclaimer']) ?>
                </div>

                <div class="d-flex gap-2 justify-content-end mt-4">
                    <a href="assessment.php?type=<?= urlencode($disease_type) ?>" class="btn btn-outline-info rounded-pill px-4">
                        <i class="bi bi-clipboard2-pulse me-1"></i> Full Clinical Assessment
                    </a>
                </div>
            </div>
        <?php endif; ?>
    </div>
</div>

<?php require_once __DIR__ . '/includes/footer.php'; ?>
