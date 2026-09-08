<?php
// assessment.php
require_once __DIR__ . '/includes/auth.php';
require_once __DIR__ . '/includes/ml_bridge.php';

require_login();

$errors = [];
$user_id = $_SESSION['user_id'];

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
    } else {
        $errors[] = "Invalid disease type selected.";
    }

    if (empty($errors)) {
        // Execute ML prediction via bridge
        $ml_result = call_ml_prediction($disease_type, $input_data);

        if (isset($ml_result['error'])) {
            $errors[] = $ml_result['error'];
        } else {
            $disease_title = ($disease_type === 'diabetes') ? 'Diabetes' : 'Heart Disease';
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
    <div class="col-lg-9">
        <div class="card card-custom p-4 p-md-5 shadow-lg">
            <div class="d-flex align-items-center mb-4 pb-3 border-bottom">
                <div class="bg-info bg-opacity-10 p-3 rounded-circle text-info me-3">
                    <i class="bi bi-clipboard-pulse fs-2"></i>
                </div>
                <div>
                    <h3 class="fw-bold mb-0">Health Risk Assessment Form</h3>
                    <p class="text-muted small mb-0">Enter clinical parameters for AI-powered risk evaluation</p>
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

            <form action="assessment.php" method="POST">
                <!-- Disease Selector -->
                <div class="mb-4 bg-light p-3 rounded-3 border">
                    <label for="disease_type" class="form-label fw-bold text-dark fs-5 mb-2">
                        <i class="bi bi-virus me-2 text-info"></i>Select Target Condition
                    </label>
                    <select class="form-select form-select-lg" id="disease_type" name="disease_type">
                        <option value="diabetes" <?= (isset($_POST['disease_type']) && $_POST['disease_type'] === 'diabetes') ? 'selected' : '' ?>>
                            Diabetes Risk Assessment (Pima Clinical Model)
                        </option>
                        <option value="heart" <?= (isset($_POST['disease_type']) && $_POST['disease_type'] === 'heart') ? 'selected' : '' ?>>
                            Heart Disease Risk Assessment (UCI Cardiac Dataset)
                        </option>
                    </select>
                </div>

                <!-- DIABETES INPUT FIELDS -->
                <div id="diabetes_fields">
                    <h5 class="fw-bold text-primary mb-3"><i class="bi bi-droplet-fill me-2 text-danger"></i>Diabetes Health Metrics</h5>
                    <div class="row g-3 mb-4">
                        <div class="col-md-6">
                            <label class="form-label">Glucose Level (mg/dL)</label>
                            <input type="number" step="0.1" name="Glucose" class="form-control" placeholder="e.g. 120" value="<?= sanitize($_POST['Glucose'] ?? '115') ?>" required>
                            <small class="text-muted">Normal: 70-140 mg/dL</small>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Body Mass Index (BMI)</label>
                            <input type="number" step="0.1" name="BMI" class="form-control" placeholder="e.g. 26.5" value="<?= sanitize($_POST['BMI'] ?? '28.4') ?>" required>
                            <small class="text-muted">Healthy: 18.5 - 24.9</small>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Blood Pressure (mm Hg)</label>
                            <input type="number" step="0.1" name="BloodPressure" class="form-control" placeholder="e.g. 75" value="<?= sanitize($_POST['BloodPressure'] ?? '74') ?>" required>
                            <small class="text-muted">Diastolic pressure</small>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Age (Years)</label>
                            <input type="number" name="Age" class="form-control" placeholder="e.g. 45" value="<?= sanitize($_POST['Age'] ?? '42') ?>" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Number of Pregnancies</label>
                            <input type="number" name="Pregnancies" class="form-control" value="<?= sanitize($_POST['Pregnancies'] ?? '1') ?>" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Insulin Level (mu U/ml)</label>
                            <input type="number" step="0.1" name="Insulin" class="form-control" value="<?= sanitize($_POST['Insulin'] ?? '80') ?>" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Skin Thickness (mm)</label>
                            <input type="number" step="0.1" name="SkinThickness" class="form-control" value="<?= sanitize($_POST['SkinThickness'] ?? '22') ?>" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Diabetes Pedigree Function</label>
                            <input type="number" step="0.001" name="DiabetesPedigreeFunction" class="form-control" value="<?= sanitize($_POST['DiabetesPedigreeFunction'] ?? '0.47') ?>" required>
                            <small class="text-muted">Genetic risk score (0.08 - 2.4)</small>
                        </div>
                    </div>
                </div>

                <!-- HEART DISEASE INPUT FIELDS -->
                <div id="heart_fields" style="display: none;">
                    <h5 class="fw-bold text-primary mb-3"><i class="bi bi-heart-pulse-fill me-2 text-danger"></i>Heart Disease Clinical Metrics</h5>
                    <div class="row g-3 mb-4">
                        <div class="col-md-6">
                            <label class="form-label">Age (Years)</label>
                            <input type="number" name="age" class="form-control" value="<?= sanitize($_POST['age'] ?? '52') ?>">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Sex</label>
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
                            <label class="form-label">ST Depression (Oldpeak)</label>
                            <input type="number" step="0.1" name="oldpeak" class="form-control" value="<?= sanitize($_POST['oldpeak'] ?? '1.2') ?>">
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">Slope of Peak Exercise ST</label>
                            <select name="slope" class="form-select">
                                <option value="0">Upsloping (0)</option>
                                <option value="1">Flat (1)</option>
                                <option value="2">Downsloping (2)</option>
                            </select>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">Major Vessels (0-4)</label>
                            <input type="number" name="ca" class="form-control" value="<?= sanitize($_POST['ca'] ?? '0') ?>">
                        </div>
                        <div class="col-md-4">
                            <label class="form-label">Thalassemia (Thal)</label>
                            <select name="thal" class="form-select">
                                <option value="1">Normal (1)</option>
                                <option value="2">Fixed Defect (2)</option>
                                <option value="3">Reversible Defect (3)</option>
                            </select>
                        </div>
                    </div>
                </div>

                <div class="disclaimer-banner mb-4">
                    <i class="bi bi-shield-exclamation me-1"></i> By clicking calculate, your parameters will be evaluated by an educational Machine Learning model.
                </div>

                <button type="submit" class="btn btn-primary-custom btn-lg w-100 shadow">
                    <i class="bi bi-cpu-fill me-2"></i> Run AI Risk Assessment
                </button>
            </form>
        </div>
    </div>
</div>

<?php require_once __DIR__ . '/includes/footer.php'; ?>
