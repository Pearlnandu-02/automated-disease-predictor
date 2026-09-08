<?php
// simulator.php
require_once __DIR__ . '/includes/auth.php';
require_once __DIR__ . '/includes/ml_bridge.php';

require_login();

$user_id = $_SESSION['user_id'];
$from_id = intval($_GET['from'] ?? 0);

$base_assessment = null;
$disease_type = 'diabetes';
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
        $disease_type = (strtolower($base_assessment['disease']) === 'heart disease') ? 'heart' : 'diabetes';
        $input_params = json_decode($base_assessment['input_data'], true) ?: $input_params;
    }
}

$simulation_result = null;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $disease_type = sanitize($_POST['disease_type'] ?? 'diabetes');
    
    if ($disease_type === 'diabetes') {
        $input_params = [
            'Pregnancies' => floatval($_POST['Pregnancies'] ?? 0),
            'Glucose' => floatval($_POST['Glucose'] ?? 0),
            'BloodPressure' => floatval($_POST['BloodPressure'] ?? 0),
            'SkinThickness' => floatval($_POST['SkinThickness'] ?? 0),
            'Insulin' => floatval($_POST['Insulin'] ?? 0),
            'BMI' => floatval($_POST['BMI'] ?? 0),
            'DiabetesPedigreeFunction' => floatval($_POST['DiabetesPedigreeFunction'] ?? 0),
            'Age' => floatval($_POST['Age'] ?? 0),
        ];
    } else {
        $input_params = [
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
    }

    $simulation_result = call_ml_prediction($disease_type, $input_params);
}

require_once __DIR__ . '/includes/header.php';
?>

<div class="row justify-content-center py-4">
    <div class="col-lg-10">
        <div class="card card-custom p-4 p-md-5 mb-4 shadow-lg">
            <div class="d-flex align-items-center mb-4 pb-3 border-bottom">
                <div class="bg-primary bg-opacity-10 p-3 rounded-circle text-primary me-3">
                    <i class="bi bi-sliders fs-2"></i>
                </div>
                <div>
                    <h3 class="fw-bold mb-0">What-If Health Risk Simulator</h3>
                    <p class="text-muted small mb-0">Modify health parameters interactively to observe hypothetical changes in risk probability</p>
                </div>
            </div>

            <div class="disclaimer-banner mb-4">
                <i class="bi bi-info-circle-fill me-1"></i>
                <strong>Hypothetical Simulation Disclaimer:</strong> This simulator demonstrates how ML mathematical probabilities shift when inputs are adjusted. Changing these sliders does NOT guarantee actual clinical real-world outcomes.
            </div>

            <form action="simulator.php<?= $from_id > 0 ? '?from='.$from_id : '' ?>" method="POST">
                <input type="hidden" name="disease_type" value="<?= $disease_type ?>">

                <h5 class="fw-bold text-dark mb-3">Adjust Parameters for <?= ucfirst($disease_type) ?> Simulation:</h5>

                <?php if ($disease_type === 'diabetes'): ?>
                    <div class="row g-4 mb-4">
                        <div class="col-md-6">
                            <label class="form-label d-flex justify-content-between">
                                <span>Glucose Level (mg/dL)</span>
                                <span class="fw-bold text-teal" id="val_glucose"><?= $input_params['Glucose'] ?? 140 ?></span>
                            </label>
                            <input type="range" class="form-range sync-slider" data-target="val_glucose" min="70" max="220" step="1" name="Glucose" value="<?= $input_params['Glucose'] ?? 140 ?>">
                        </div>

                        <div class="col-md-6">
                            <label class="form-label d-flex justify-content-between">
                                <span>Body Mass Index (BMI)</span>
                                <span class="fw-bold text-teal" id="val_bmi"><?= $input_params['BMI'] ?? 30 ?></span>
                            </label>
                            <input type="range" class="form-range sync-slider" data-target="val_bmi" min="15" max="50" step="0.5" name="BMI" value="<?= $input_params['BMI'] ?? 30 ?>">
                        </div>

                        <div class="col-md-6">
                            <label class="form-label d-flex justify-content-between">
                                <span>Blood Pressure (mm Hg)</span>
                                <span class="fw-bold text-teal" id="val_bp"><?= $input_params['BloodPressure'] ?? 80 ?></span>
                            </label>
                            <input type="range" class="form-range sync-slider" data-target="val_bp" min="50" max="130" step="1" name="BloodPressure" value="<?= $input_params['BloodPressure'] ?? 80 ?>">
                        </div>

                        <div class="col-md-6">
                            <label class="form-label d-flex justify-content-between">
                                <span>Age (Years)</span>
                                <span class="fw-bold text-teal" id="val_age"><?= $input_params['Age'] ?? 45 ?></span>
                            </label>
                            <input type="range" class="form-range sync-slider" data-target="val_age" min="20" max="80" step="1" name="Age" value="<?= $input_params['Age'] ?? 45 ?>">
                        </div>
                    </div>
                <?php else: ?>
                    <div class="row g-4 mb-4">
                        <div class="col-md-6">
                            <label class="form-label d-flex justify-content-between">
                                <span>Serum Cholesterol (mg/dL)</span>
                                <span class="fw-bold text-teal" id="val_chol"><?= $input_params['chol'] ?? 240 ?></span>
                            </label>
                            <input type="range" class="form-range sync-slider" data-target="val_chol" min="120" max="400" step="1" name="chol" value="<?= $input_params['chol'] ?? 240 ?>">
                        </div>

                        <div class="col-md-6">
                            <label class="form-label d-flex justify-content-between">
                                <span>Resting Blood Pressure (mm Hg)</span>
                                <span class="fw-bold text-teal" id="val_trestbps"><?= $input_params['trestbps'] ?? 135 ?></span>
                            </label>
                            <input type="range" class="form-range sync-slider" data-target="val_trestbps" min="90" max="200" step="1" name="trestbps" value="<?= $input_params['trestbps'] ?? 135 ?>">
                        </div>

                        <div class="col-md-6">
                            <label class="form-label d-flex justify-content-between">
                                <span>Max Heart Rate (Thalach)</span>
                                <span class="fw-bold text-teal" id="val_thalach"><?= $input_params['thalach'] ?? 145 ?></span>
                            </label>
                            <input type="range" class="form-range sync-slider" data-target="val_thalach" min="80" max="200" step="1" name="thalach" value="<?= $input_params['thalach'] ?? 145 ?>">
                        </div>

                        <div class="col-md-6">
                            <label class="form-label d-flex justify-content-between">
                                <span>Age (Years)</span>
                                <span class="fw-bold text-teal" id="val_age_h"><?= $input_params['age'] ?? 52 ?></span>
                            </label>
                            <input type="range" class="form-range sync-slider" data-target="val_age_h" min="25" max="80" step="1" name="age" value="<?= $input_params['age'] ?? 52 ?>">
                        </div>
                    </div>
                <?php endif; ?>

                <button type="submit" class="btn btn-primary-custom btn-lg w-100 shadow">
                    <i class="bi bi-play-circle-fill me-2"></i> Run What-If Simulation
                </button>
            </form>
        </div>

        <?php if ($simulation_result && !isset($simulation_result['error'])): ?>
            <div class="card card-custom p-4 p-md-5 bg-white shadow-lg">
                <h4 class="fw-bold mb-4 text-success d-flex align-items-center">
                    <i class="bi bi-check2-circle me-2"></i> Simulation Results
                </h4>

                <div class="row align-items-center">
                    <div class="col-md-6 text-center border-end">
                        <small class="text-muted uppercase fw-bold">Simulated Risk Level</small>
                        <h2 class="fw-bold mt-2">
                            <span class="badge-risk-<?= strtoupper($simulation_result['risk_level']) ?>">
                                <?= strtoupper($simulation_result['risk_level']) ?>
                            </span>
                        </h2>
                    </div>

                    <div class="col-md-6 text-center">
                        <small class="text-muted uppercase fw-bold">Simulated Risk Probability</small>
                        <h1 class="display-4 fw-bold text-dark mt-1">
                            <?= number_format($simulation_result['probability'], 1) ?>%
                        </h1>
                    </div>
                </div>
            </div>
        <?php endif; ?>
    </div>
</div>

<?php require_once __DIR__ . '/includes/footer.php'; ?>
