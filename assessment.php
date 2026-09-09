<?php
// assessment.php
require_once __DIR__ . '/includes/auth.php';
require_once __DIR__ . '/includes/ml_bridge.php';

require_login();

$errors = [];
$user_id = $_SESSION['user_id'];
$disease_type = sanitize($_POST['disease_type'] ?? ($_GET['type'] ?? 'diabetes'));

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $disease_type = sanitize($_POST['disease_type'] ?? 'diabetes');
    $input_data = [];

    if ($disease_type === 'diabetes') {
        $input_data = [
            'Pregnancies' => floatval($_POST['Pregnancies'] ?? 0),
            'Glucose' => floatval($_POST['Glucose'] ?? 0),
            'BloodPressure' => floatval($_POST['BloodPressure'] ?? 0),
            'SkinThickness' => floatval($_POST['SkinThickness'] ?? 0),
            'Insulin' => floatval($_POST['Insulin'] ?? 0),
            'BMI' => floatval($_POST['BMI'] ?? 0),
            'DiabetesPedigreeFunction' => floatval($_POST['DiabetesPedigreeFunction'] ?? 0),
            'Age' => floatval($_POST['Age'] ?? 0),
        ];

        if ($input_data['Glucose'] < 40 || $input_data['Glucose'] > 300) {
            $errors[] = "Glucose level must be between 40 and 300 mg/dL.";
        }
        if ($input_data['BMI'] < 10 || $input_data['BMI'] > 70) {
            $errors[] = "BMI must be between 10 and 70.";
        }
        if ($input_data['Age'] < 1 || $input_data['Age'] > 120) {
            $errors[] = "Age must be between 1 and 120 years.";
        }
    } elseif ($disease_type === 'heart') {
        $input_data = [
            'age' => floatval($_POST['age'] ?? 0),
            'sex' => intval($_POST['sex'] ?? 0),
            'cp' => intval($_POST['cp'] ?? 0),
            'trestbps' => floatval($_POST['trestbps'] ?? 0),
            'chol' => floatval($_POST['chol'] ?? 0),
            'fbs' => intval($_POST['fbs'] ?? 0),
            'restecg' => intval($_POST['restecg'] ?? 0),
            'thalach' => floatval($_POST['thalach'] ?? 0),
            'exang' => intval($_POST['exang'] ?? 0),
            'oldpeak' => floatval($_POST['oldpeak'] ?? 0),
            'slope' => intval($_POST['slope'] ?? 0),
            'ca' => intval($_POST['ca'] ?? 0),
            'thal' => intval($_POST['thal'] ?? 0),
        ];

        if ($input_data['age'] < 1 || $input_data['age'] > 120) {
            $errors[] = "Age must be between 1 and 120 years.";
        }
        if ($input_data['trestbps'] < 70 || $input_data['trestbps'] > 240) {
            $errors[] = "Resting blood pressure must be between 70 and 240 mm Hg.";
        }
        if ($input_data['chol'] < 100 || $input_data['chol'] > 600) {
            $errors[] = "Cholesterol must be between 100 and 600 mg/dL.";
        }
    } elseif ($disease_type === 'hypertension') {
        $input_data = [
            'systolic' => floatval($_POST['systolic'] ?? 130),
            'diastolic' => floatval($_POST['diastolic'] ?? 82),
            'Age' => floatval($_POST['Age'] ?? 45),
            'BMI' => floatval($_POST['BMI'] ?? 26.5),
            'sodium' => floatval($_POST['sodium'] ?? 2800),
            'smoking' => intval($_POST['smoking'] ?? 0),
            'stress' => intval($_POST['stress'] ?? 1),
        ];
    } elseif ($disease_type === 'respiratory') {
        $input_data = [
            'Age' => floatval($_POST['Age'] ?? 48),
            'pack_years' => floatval($_POST['pack_years'] ?? 5),
            'dyspnea' => intval($_POST['dyspnea'] ?? 1),
            'cough_weeks' => floatval($_POST['cough_weeks'] ?? 2),
            'env_exposure' => intval($_POST['env_exposure'] ?? 1),
        ];
    } elseif ($disease_type === 'lifestyle') {
        $input_data = [
            'age_group' => intval($_POST['age_group'] ?? 2),
            'smoking' => intval($_POST['smoking'] ?? 0),
            'physical_activity' => intval($_POST['physical_activity'] ?? 1),
            'family_history' => intval($_POST['family_history'] ?? 0),
            'bp_category' => intval($_POST['bp_category'] ?? 1),
            'bmi_category' => intval($_POST['bmi_category'] ?? 2),
            'blood_sugar' => intval($_POST['blood_sugar'] ?? 1),
            'cholesterol' => intval($_POST['cholesterol'] ?? 1),
            'diet_quality' => intval($_POST['diet_quality'] ?? 1),
            'sleep_stress' => intval($_POST['sleep_stress'] ?? 1),
            'chronic_conditions' => intval($_POST['chronic_conditions'] ?? 0),
        ];
    } else {
        $errors[] = "Invalid disease type selected.";
    }

    if (empty($errors)) {
        // Execute ML / Risk assessment evaluation
        $ml_result = call_ml_prediction($disease_type, $input_data);

        if (isset($ml_result['error'])) {
            $errors[] = $ml_result['error'];
        } else {
            $titles = [
                'diabetes' => 'Diabetes Risk',
                'heart' => 'Heart Disease Risk',
                'hypertension' => 'Hypertension & Vascular Health',
                'respiratory' => 'Pulmonary & Respiratory Health',
                'lifestyle' => 'Multi-Factor Lifestyle & Chronic Risk'
            ];
            $disease_title = $titles[$disease_type] ?? ucfirst($disease_type);

            $db = Database::getInstance();
            $stmt = $db->prepare("INSERT INTO health_assessments 
                (user_id, disease, input_data, risk_level, probability, feature_importance, recommendations) 
                VALUES (?, ?, ?, ?, ?, ?, ?)");

            $success = $stmt->execute([
                $user_id,
                $disease_title,
                json_encode($input_data),
                $ml_result['risk_level'],
                $ml_result['probability'],
                json_encode($ml_result['feature_importance']),
                json_encode($ml_result['recommendations'])
            ]);

            if ($success) {
                $assessment_id = $db->lastInsertId();
                redirect("result.php?id=" . $assessment_id);
            } else {
                $errors[] = "Failed to save assessment results.";
            }
        }
    }
}

require_once __DIR__ . '/includes/header.php';
?>

<div class="row justify-content-center py-4">
    <div class="col-lg-10">
        <div class="card card-custom p-4 p-md-5 shadow-lg">
            <div class="d-flex align-items-center mb-4 pb-3 border-bottom border-secondary border-opacity-25">
                <div class="bg-info bg-opacity-10 p-3 rounded-circle text-info me-3">
                    <i class="bi bi-clipboard-pulse fs-2"></i>
                </div>
                <div>
                    <h3 class="fw-bold mb-0">Clinical Health Risk Assessment</h3>
                    <p class="text-muted small mb-0">Enter clinical biomarkers or lifestyle parameters for evidence-based risk analysis</p>
                </div>
            </div>

            <?php if (!empty($errors)): ?>
                <div class="alert alert-danger shadow-sm">
                    <ul class="mb-0 ps-3">
                        <?php foreach ($errors as $error): ?>
                            <li><?= sanitize($error) ?></li>
                        <?php endforeach; ?>
                    </ul>
                </div>
            <?php endif; ?>

            <form action="assessment.php" method="POST" id="assessmentForm">
                <!-- Disease Target Selector (5 Comprehensive Options) -->
                <div class="mb-4 p-3 rounded-3 border bg-card-subtle">
                    <label for="disease_type" class="form-label fw-bold fs-6 mb-2">
                        <i class="bi bi-diagram-3-fill me-2 text-info"></i>Select Target Health Assessment:
                    </label>
                    <select class="form-select form-select-lg" id="disease_type" name="disease_type">
                        <option value="diabetes" <?= $disease_type === 'diabetes' ? 'selected' : '' ?>>
                            1. Type 2 Diabetes & Metabolic Risk Assessment (Pima Clinical Model)
                        </option>
                        <option value="heart" <?= $disease_type === 'heart' ? 'selected' : '' ?>>
                            2. Coronary Heart Disease Risk Assessment (Cleveland Cardiac Dataset)
                        </option>
                        <option value="hypertension" <?= $disease_type === 'hypertension' ? 'selected' : '' ?>>
                            3. Hypertension & Vascular Risk Assessment (Arterial Pressure Profile)
                        </option>
                        <option value="respiratory" <?= $disease_type === 'respiratory' ? 'selected' : '' ?>>
                            4. Pulmonary & Respiratory Health Assessment (Dyspnea & Exposure Scale)
                        </option>
                        <option value="lifestyle" <?= $disease_type === 'lifestyle' ? 'selected' : '' ?>>
                            5. Comprehensive Multi-Factor Chronic Risk Assessment (11 Lifestyle Indicators)
                        </option>
                    </select>
                </div>

                <!-- 1. DIABETES INPUT FIELDS -->
                <div id="diabetes_fields" style="display: <?= $disease_type === 'diabetes' ? 'block' : 'none' ?>;">
                    <h5 class="fw-bold text-info mb-3"><i class="bi bi-droplet-fill me-2 text-danger"></i>Diabetes Health Biomarkers</h5>
                    <div class="row g-3 mb-4">
                        <div class="col-md-6">
                            <label class="form-label">Glucose Level (mg/dL)</label>
                            <input type="number" step="0.1" name="Glucose" class="form-control" placeholder="e.g. 120" value="<?= sanitize($_POST['Glucose'] ?? '115') ?>" required>
                            <small class="text-muted">Fasting normal: 70 - 100 mg/dL, Pre-diabetes: 100 - 125 mg/dL</small>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Body Mass Index (BMI)</label>
                            <input type="number" step="0.1" name="BMI" class="form-control" placeholder="e.g. 28.4" value="<?= sanitize($_POST['BMI'] ?? '28.4') ?>" required>
                            <small class="text-muted">Healthy: 18.5 - 24.9 | Overweight: 25 - 29.9</small>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Diastolic Blood Pressure (mm Hg)</label>
                            <input type="number" step="0.1" name="BloodPressure" class="form-control" placeholder="e.g. 74" value="<?= sanitize($_POST['BloodPressure'] ?? '74') ?>" required>
                        </div>

                        <!-- Diabetes Age Slider: Synced bidirectional control -->
                        <div class="col-md-6">
                            <label class="form-label d-flex justify-content-between align-items-center mb-1">
                                <span>Age (Years)</span>
                                <span class="slider-val-badge" id="val_age_disp"><?= sanitize($_POST['Age'] ?? '42') ?></span>
                            </label>
                            <input 
                                type="range" 
                                class="form-range sync-slider mb-2" 
                                data-target="val_age_disp" 
                                min="1" 
                                max="100" 
                                step="1" 
                                name="Age" 
                                id="age_slider" 
                                value="<?= sanitize($_POST['Age'] ?? '42') ?>"
                            >
                            <input 
                                type="number" 
                                name="Age" 
                                id="age_num" 
                                class="form-control" 
                                value="<?= sanitize($_POST['Age'] ?? '42') ?>" 
                                min="1" 
                                max="100" 
                                required
                            >
                        </div>

                        <div class="col-md-6">
                            <label class="form-label">Number of Pregnancies</label>
                            <input type="number" name="Pregnancies" class="form-control" value="<?= sanitize($_POST['Pregnancies'] ?? '1') ?>" min="0">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Serum Insulin Level (mu U/ml)</label>
                            <input type="number" step="0.1" name="Insulin" class="form-control" value="<?= sanitize($_POST['Insulin'] ?? '80') ?>">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Triceps Skin Thickness (mm)</label>
                            <input type="number" step="0.1" name="SkinThickness" class="form-control" value="<?= sanitize($_POST['SkinThickness'] ?? '22') ?>">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Diabetes Pedigree Function</label>
                            <input type="number" step="0.001" name="DiabetesPedigreeFunction" class="form-control" value="<?= sanitize($_POST['DiabetesPedigreeFunction'] ?? '0.47') ?>">
                            <small class="text-muted">Genetic susceptibility metric (0.08 - 2.4)</small>
                        </div>
                    </div>
                </div>

                <!-- 2. HEART DISEASE INPUT FIELDS -->
                <div id="heart_fields" style="display: <?= $disease_type === 'heart' ? 'block' : 'none' ?>;">
                    <h5 class="fw-bold text-info mb-3"><i class="bi bi-heart-pulse-fill me-2 text-danger"></i>Heart Disease Clinical Biomarkers</h5>
                    <div class="row g-3 mb-4">
                        <div class="col-md-6">
                            <label class="form-label d-flex justify-content-between align-items-center">
                                <span>Age (Years)</span>
                                <span class="slider-val-badge" id="val_age_heart"><?= sanitize($_POST['age'] ?? '52') ?></span>
                            </label>
                            <input type="range" class="form-range sync-slider mb-2" data-target="val_age_heart" min="20" max="95" step="1" name="age" value="<?= sanitize($_POST['age'] ?? '52') ?>">
                            <input type="number" name="age" class="form-control" value="<?= sanitize($_POST['age'] ?? '52') ?>">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Biological Sex</label>
                            <select name="sex" class="form-select">
                                <option value="1">Male</option>
                                <option value="0">Female</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Chest Pain Type (CP)</label>
                            <select name="cp" class="form-select">
                                <option value="0">Typical Angina (0)</option>
                                <option value="1">Atypical Angina (1)</option>
                                <option value="2">Non-anginal Pain (2)</option>
                                <option value="3">Asymptomatic (3)</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Resting Blood Pressure (mm Hg)</label>
                            <input type="number" step="0.1" name="trestbps" class="form-control" value="<?= sanitize($_POST['trestbps'] ?? '132') ?>">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Serum Cholesterol (mg/dL)</label>
                            <input type="number" step="0.1" name="chol" class="form-control" value="<?= sanitize($_POST['chol'] ?? '235') ?>">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Fasting Blood Sugar > 120 mg/dL</label>
                            <select name="fbs" class="form-select">
                                <option value="0">False (<= 120 mg/dL)</option>
                                <option value="1">True (> 120 mg/dL)</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Resting ECG Results</label>
                            <select name="restecg" class="form-select">
                                <option value="0">Normal (0)</option>
                                <option value="1">ST-T Wave Abnormality (1)</option>
                                <option value="2">Left Ventricular Hypertrophy (2)</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Max Heart Rate Achieved (Thalach)</label>
                            <input type="number" step="0.1" name="thalach" class="form-control" value="<?= sanitize($_POST['thalach'] ?? '150') ?>">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Exercise Induced Angina</label>
                            <select name="exang" class="form-select">
                                <option value="0">No (0)</option>
                                <option value="1">Yes (1)</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">ST Depression Induced by Exercise (Oldpeak)</label>
                            <input type="number" step="0.1" name="oldpeak" class="form-control" value="<?= sanitize($_POST['oldpeak'] ?? '1.2') ?>">
                        </div>
                    </div>
                </div>

                <!-- 3. HYPERTENSION INPUT FIELDS -->
                <div id="hypertension_fields" style="display: <?= $disease_type === 'hypertension' ? 'block' : 'none' ?>;">
                    <h5 class="fw-bold text-info mb-3"><i class="bi bi-speedometer2 me-2 text-warning"></i>Hypertension & Arterial Health Parameters</h5>
                    <div class="row g-3 mb-4">
                        <div class="col-md-6">
                            <label class="form-label">Systolic Blood Pressure (mm Hg)</label>
                            <input type="number" name="systolic" class="form-control" value="<?= sanitize($_POST['systolic'] ?? '135') ?>" required>
                            <small class="text-muted">Normal: < 120 | Elevated: 120-129 | Stage 1: 130-139</small>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Diastolic Blood Pressure (mm Hg)</label>
                            <input type="number" name="diastolic" class="form-control" value="<?= sanitize($_POST['diastolic'] ?? '85') ?>" required>
                            <small class="text-muted">Normal: < 80 | Stage 1: 80-89 | Stage 2: >= 90</small>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label d-flex justify-content-between align-items-center">
                                <span>Age (Years)</span>
                                <span class="slider-val-badge" id="val_age_hyp"><?= sanitize($_POST['Age'] ?? '48') ?></span>
                            </label>
                            <input type="range" class="form-range sync-slider mb-2" data-target="val_age_hyp" min="18" max="95" step="1" name="Age" value="<?= sanitize($_POST['Age'] ?? '48') ?>">
                            <input type="number" name="Age" class="form-control" value="<?= sanitize($_POST['Age'] ?? '48') ?>">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Estimated Daily Sodium Intake (mg/day)</label>
                            <input type="number" name="sodium" class="form-control" value="<?= sanitize($_POST['sodium'] ?? '2800') ?>">
                            <small class="text-muted">AHA recommended maximum: 2,300 mg/day</small>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Smoking Status</label>
                            <select name="smoking" class="form-select">
                                <option value="0">Non-Smoker</option>
                                <option value="1">Former Smoker</option>
                                <option value="2">Active Smoker</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Chronic Stress Level</label>
                            <select name="stress" class="form-select">
                                <option value="0">Low / Manageable</option>
                                <option value="1">Moderate</option>
                                <option value="2">High / Severe Daily Stress</option>
                            </select>
                        </div>
                    </div>
                </div>

                <!-- 4. RESPIRATORY INPUT FIELDS -->
                <div id="respiratory_fields" style="display: <?= $disease_type === 'respiratory' ? 'block' : 'none' ?>;">
                    <h5 class="fw-bold text-info mb-3"><i class="bi bi-lungs me-2 text-info"></i>Pulmonary & Airway Health Indicators</h5>
                    <div class="row g-3 mb-4">
                        <div class="col-md-6">
                            <label class="form-label">Dyspnea / Breathlessness Scale</label>
                            <select name="dyspnea" class="form-select">
                                <option value="0">Grade 0: Only on strenuous exertion</option>
                                <option value="1">Grade 1: Short of breath when hurrying</option>
                                <option value="2">Grade 2: Walks slower than peers on level ground</option>
                                <option value="3">Grade 3: Stops for breath after 100 meters</option>
                                <option value="4">Grade 4: Too breathless to leave house or dress</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Tobacco Smoking History (Pack-Years)</label>
                            <input type="number" step="0.5" name="pack_years" class="form-control" value="<?= sanitize($_POST['pack_years'] ?? '4') ?>" min="0">
                            <small class="text-muted">Packs per day multiplied by years smoked</small>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Persistent Cough Duration (Weeks)</label>
                            <input type="number" step="1" name="cough_weeks" class="form-control" value="<?= sanitize($_POST['cough_weeks'] ?? '2') ?>" min="0">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Environmental Air Quality Exposure</label>
                            <select name="env_exposure" class="form-select">
                                <option value="0">Clean Rural / Minimal Dust</option>
                                <option value="1">Suburban / Moderate Traffic</option>
                                <option value="2">Urban Dense / Biomass / Industrial</option>
                            </select>
                        </div>
                    </div>
                </div>

                <!-- 5. COMPREHENSIVE MULTI-FACTOR LIFESTYLE RISK ASSESSMENT (11 Risk Factors) -->
                <div id="lifestyle_fields" style="display: <?= $disease_type === 'lifestyle' ? 'block' : 'none' ?>;">
                    <h5 class="fw-bold text-info mb-3"><i class="bi bi-heart-half me-2 text-success"></i>11 Multi-Factor Health & Chronic Disease Indicators</h5>
                    <div class="row g-3 mb-4">
                        <div class="col-md-6">
                            <label class="form-label">1. Age Group</label>
                            <select name="age_group" class="form-select">
                                <option value="1">Young Adult (18 - 35 years)</option>
                                <option value="2" selected>Middle-Aged (36 - 50 years)</option>
                                <option value="3">Mature Adult (51 - 65 years)</option>
                                <option value="4">Senior (65+ years)</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">2. Tobacco Smoking Status</label>
                            <select name="smoking" class="form-select">
                                <option value="0">Never Smoked</option>
                                <option value="1">Former Smoker (Quit > 1 year ago)</option>
                                <option value="2">Occasional / Social Smoker</option>
                                <option value="3">Daily Active Smoker</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">3. Weekly Physical Activity</label>
                            <select name="physical_activity" class="form-select">
                                <option value="3">Very Active (>= 150 mins aerobic + strength)</option>
                                <option value="2">Moderate (90 - 150 mins/week)</option>
                                <option value="1" selected>Light (30 - 90 mins/week)</option>
                                <option value="0">Sedentary (< 30 mins/week)</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">4. Family History of Chronic Illness</label>
                            <select name="family_history" class="form-select">
                                <option value="0">No known chronic illness in immediate family</option>
                                <option value="1">First-degree relative with Type 2 Diabetes</option>
                                <option value="2">First-degree relative with Coronary Heart Disease</option>
                                <option value="3">Multiple family members with cardiometabolic disease</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">5. Blood Pressure Category</label>
                            <select name="bp_category" class="form-select">
                                <option value="0">Normal (< 120/80 mm Hg)</option>
                                <option value="1" selected>Elevated (120-129 / < 80 mm Hg)</option>
                                <option value="2">Stage 1 Hypertension (130-139 / 80-89 mm Hg)</option>
                                <option value="3">Stage 2 Hypertension (>= 140 / >= 90 mm Hg)</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">6. Body Mass Index (BMI) Category</label>
                            <select name="bmi_category" class="form-select">
                                <option value="0">Underweight (< 18.5)</option>
                                <option value="1">Normal Weight (18.5 - 24.9)</option>
                                <option value="2" selected>Overweight (25.0 - 29.9)</option>
                                <option value="3">Obese Class I (30.0 - 34.9)</option>
                                <option value="4">Obese Class II+ (>= 35.0)</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">7. Fasting Blood Glucose Level</label>
                            <select name="blood_sugar" class="form-select">
                                <option value="0">Optimal / Normal (< 100 mg/dL)</option>
                                <option value="1" selected>Impaired Fasting Glucose / Pre-diabetes (100 - 125 mg/dL)</option>
                                <option value="2">Elevated / Diabetic Range (>= 126 mg/dL)</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">8. Serum Cholesterol Profile</label>
                            <select name="cholesterol" class="form-select">
                                <option value="0">Desirable Total Cholesterol (< 200 mg/dL)</option>
                                <option value="1" selected>Borderline High (200 - 239 mg/dL)</option>
                                <option value="2">High Risk (>= 240 mg/dL)</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">9. Dietary & Nutrition Quality</label>
                            <select name="diet_quality" class="form-select">
                                <option value="0">Whole food, Mediterranean, rich in fiber & greens</option>
                                <option value="1" selected>Average mixed diet with occasional processed food</option>
                                <option value="2">High sodium, saturated fat, and ultra-processed food</option>
                                <option value="3">Frequent sugary drinks, fast food, and refined starches</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">10. Sleep Quality & Daily Stress</label>
                            <select name="sleep_stress" class="form-select">
                                <option value="0">Restful 7 - 9 hours sleep / Low manageable stress</option>
                                <option value="1" selected>6 - 7 hours sleep / Moderate daily work stress</option>
                                <option value="2">< 6 hours fragmented sleep / Chronic high stress</option>
                            </select>
                        </div>
                        <div class="col-md-12">
                            <label class="form-label">11. Existing Pre-conditions</label>
                            <select name="chronic_conditions" class="form-select">
                                <option value="0">No existing diagnosed chronic conditions</option>
                                <option value="1">Mild seasonal allergies or well-controlled asthma</option>
                                <option value="2">Metabolic syndrome or elevated triglycerides</option>
                                <option value="3">Diagnosed cardiovascular, renal, or hepatic disease</option>
                            </select>
                        </div>
                    </div>
                </div>

                <div class="disclaimer-banner my-4">
                    <i class="bi bi-info-circle-fill me-1 text-info"></i>
                    <strong>Educational Disclaimer:</strong> This clinical risk assessment is strictly an educational tool for identifying statistical correlations. It does not provide medical diagnoses or prescribe clinical therapies.
                </div>

                <button type="submit" class="btn btn-primary-custom btn-lg w-100 py-3">
                    <i class="bi bi-cpu-fill me-2"></i> Compute Personalized Risk Assessment
                </button>
            </form>
        </div>
    </div>
</div>

<?php
require_once __DIR__ . '/includes/footer.php';
?>
