<?php
require_once __DIR__ . '/includes/auth.php';
require_once __DIR__ . '/includes/functions.php';

require_login();

$user = get_logged_in_user();
$user_id = $user['id'];

$pdo = get_db_connection();

$total_predictions = 0;
$recent_predictions = [];

$disease_count = 65;
$symptom_count = 58;
$mapping_count = 250;
$model_name = "Multi-Disease Prediction Model v2";
$model_accuracy = "75.2%";

if ($pdo) {
    try {
        $stmt = $pdo->prepare("SELECT COUNT(*) AS total FROM prediction_history WHERE user_id = ?");
        $stmt->execute([$user_id]);
        $total_predictions = $stmt->fetch()['total'];

        $stmt = $pdo->prepare("SELECT * FROM prediction_history WHERE user_id = ? ORDER BY created_at DESC LIMIT 5");
        $stmt->execute([$user_id]);
        $recent_predictions = $stmt->fetchAll();

        $d_res = (int)$pdo->query("SELECT COUNT(*) FROM diseases")->fetchColumn();
        if ($d_res > 0) $disease_count = $d_res;
        $s_res = (int)$pdo->query("SELECT COUNT(*) FROM symptoms")->fetchColumn();
        if ($s_res > 0) $symptom_count = $s_res;
        $m_res = (int)$pdo->query("SELECT COUNT(*) FROM disease_symptoms")->fetchColumn();
        if ($m_res > 0) $mapping_count = $m_res;
    } catch (PDOException $e) {
        $total_predictions = 0;
    }
}

$eval_path = __DIR__ . '/ml/evaluation_results.json';
if (file_exists($eval_path)) {
    $eval_data = json_decode(file_get_contents($eval_path), true);
    if (!empty($eval_data['symptom_disease']['models']['Random Forest']['accuracy'])) {
        $model_accuracy = number_format($eval_data['symptom_disease']['models']['Random Forest']['accuracy'] * 100, 1) . '%';
    }
    if (!empty($eval_data['model_metadata']['model_name'])) {
        $model_name = $eval_data['model_metadata']['model_name'];
    }
}

require_once __DIR__ . '/includes/header.php';
?>

<div class="row gy-4 py-3">
    <!-- Welcome Header -->
    <div class="col-12">
        <div class="card-custom p-4 p-md-5 hero-banner">
            <div class="row align-items-center">
                <div class="col-lg-8">
                    <span class="badge hero-badge px-3 py-1 mb-2 fw-bold">User Dashboard</span>
                    <h2 class="fw-extrabold hero-heading mb-2">Welcome back, <?= sanitize($user['name']) ?>!</h2>
                    <p class="hero-lead mb-3">
                        Access your previous AI disease predictions, check current health symptoms across <?= $disease_count ?> conditions, explore disease details, and run simulations.
                    </p>
                    <div class="d-flex flex-wrap gap-2">
                        <a href="prediction.php" class="btn btn-primary-custom rounded-pill px-4">
                            <i class="bi bi-cpu-fill me-1"></i> AI Symptom Checker
                        </a>
                        <a href="diseases.php" class="btn btn-outline-info rounded-pill px-4">
                            <i class="bi bi-journal-medical me-1"></i> Explore <?= $disease_count ?> Diseases
                        </a>
                    </div>
                </div>
                <div class="col-lg-4 text-center mt-4 mt-lg-0">
                    <div class="p-3 bg-card-subtle rounded-4 border border-secondary border-opacity-25">
                        <small class="text-uppercase fw-bold text-muted">Total AI Predictions</small>
                        <h1 class="display-3 fw-extrabold text-info mb-0"><?= number_format($total_predictions) ?></h1>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Live System Overview Card -->
    <div class="col-12">
        <div class="card-custom p-4">
            <div class="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-3">
                <h5 class="fw-bold mb-0 d-flex align-items-center">
                    <i class="bi bi-cpu text-info me-2"></i> Live ML Platform Statistics & Versioning
                </h5>
                <span class="badge bg-success bg-opacity-20 text-success border border-success border-opacity-25 px-3 py-1">
                    <i class="bi bi-check-circle-fill me-1"></i> Model: <?= sanitize($model_name) ?>
                </span>
            </div>
            <div class="row g-3 text-center">
                <div class="col-md-3 col-6">
                    <div class="p-3 bg-card-subtle rounded border">
                        <h3 class="fw-extrabold text-info mb-0"><?= $disease_count ?></h3>
                        <small class="text-muted">Supported Conditions</small>
                    </div>
                </div>
                <div class="col-md-3 col-6">
                    <div class="p-3 bg-card-subtle rounded border">
                        <h3 class="fw-extrabold text-success mb-0"><?= $symptom_count ?></h3>
                        <small class="text-muted">Clinical Symptoms</small>
                    </div>
                </div>
                <div class="col-md-3 col-6">
                    <div class="p-3 bg-card-subtle rounded border">
                        <h3 class="fw-extrabold text-warning mb-0"><?= $mapping_count ?></h3>
                        <small class="text-muted">Mapped Relationships</small>
                    </div>
                </div>
                <div class="col-md-3 col-6">
                    <div class="p-3 bg-card-subtle rounded border">
                        <h3 class="fw-extrabold text-primary-theme mb-0"><?= $model_accuracy ?></h3>
                        <small class="text-muted">Empirical Accuracy</small>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Quick Access Cards -->
    <div class="col-lg-3 col-md-6">
        <div class="card card-custom p-4 h-100">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h5 class="fw-bold mb-0">AI Symptom Check</h5>
                <i class="bi bi-cpu text-info fs-3"></i>
            </div>
            <p class="text-muted small mb-3">Select symptoms and execute machine learning classification model inference.</p>
            <a href="prediction.php" class="btn btn-outline-info btn-sm rounded-pill mt-auto">Run Symptom Check</a>
        </div>
    </div>

    <div class="col-lg-3 col-md-6">
        <div class="card card-custom p-4 h-100">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h5 class="fw-bold mb-0">Injury Scanner</h5>
                <i class="bi bi-camera text-info fs-3"></i>
            </div>
            <p class="text-muted small mb-3">Upload a skin photo for educational preliminary visual erythema & edge analysis.</p>
            <a href="image_scanner.php" class="btn btn-outline-info btn-sm rounded-pill mt-auto">Launch Scanner</a>
        </div>
    </div>

    <div class="col-lg-3 col-md-6">
        <div class="card card-custom p-4 h-100">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h5 class="fw-bold mb-0">Disease Database</h5>
                <i class="bi bi-search text-warning fs-3"></i>
            </div>
            <p class="text-muted small mb-3">Explore <?= $disease_count ?> comprehensive medical conditions, causes, and prevention strategies.</p>
            <a href="diseases.php" class="btn btn-outline-warning btn-sm rounded-pill mt-auto">Browse <?= $disease_count ?> Diseases</a>
        </div>
    </div>

    <div class="col-lg-3 col-md-6">
        <div class="card card-custom p-4 h-100">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h5 class="fw-bold mb-0">What-If Simulator</h5>
                <i class="bi bi-sliders text-success fs-3"></i>
            </div>
            <p class="text-muted small mb-3">Simulate metric adjustments and recalculate statistical risk scores.</p>
            <a href="simulator.php" class="btn btn-outline-success btn-sm rounded-pill mt-auto">Open Simulator</a>
        </div>
    </div>

    <!-- Recent Predictions Table -->
    <div class="col-12">
        <div class="card card-custom p-4">
            <h4 class="fw-bold mb-3 d-flex align-items-center">
                <i class="bi bi-clock-history text-info me-2"></i> Previous AI Predictions & Symptom Checks
            </h4>

            <?php if (!empty($recent_predictions)): ?>
                <div class="table-responsive">
                    <table class="table table-custom table-hover align-middle small">
                        <thead>
                            <tr class="text-info">
                                <th>Date & Time</th>
                                <th>Selected Symptoms</th>
                                <th>Predicted Condition</th>
                                <th>AI Model Confidence</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php foreach ($recent_predictions as $p): ?>
                                <tr>
                                    <td><?= date('M d, Y H:i', strtotime($p['created_at'])) ?></td>
                                    <td><span class="text-truncate d-inline-block" style="max-width: 250px;"><?= sanitize($p['symptoms_selected']) ?></span></td>
                                    <td class="fw-bold"><?= sanitize($p['predicted_disease']) ?></td>
                                    <td class="text-info fw-bold"><?= number_format($p['confidence'], 1) ?>%</td>
                                    <td>
                                        <a href="disease_detail.php?name=<?= urlencode($p['predicted_disease']) ?>" class="btn btn-sm btn-outline-info rounded-pill px-3">
                                            Learn More
                                        </a>
                                    </td>
                                </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                </div>
            <?php else: ?>
                <div class="text-center py-4 text-muted">
                    <i class="bi bi-info-circle fs-3 d-block mb-2"></i>
                    <p class="mb-2">No previous predictions recorded yet.</p>
                    <a href="prediction.php" class="btn btn-primary-custom btn-sm rounded-pill px-4">Start First Symptom Check</a>
                </div>
            <?php endif; ?>
        </div>
    </div>

    <!-- User Profile Section -->
    <div class="col-12">
        <div class="card card-custom p-4">
            <h5 class="fw-bold mb-3"><i class="bi bi-person-circle text-info me-2"></i> Account Profile Information</h5>
            <div class="row g-3 text-muted small">
                <div class="col-md-4">
                    <strong>Full Name:</strong> <span class="text-primary-theme fw-semibold"><?= sanitize($user['name']) ?></span>
                </div>
                <div class="col-md-4">
                    <strong>Email Address:</strong> <span class="text-primary-theme fw-semibold"><?= sanitize($user['email']) ?></span>
                </div>
                <div class="col-md-4">
                    <strong>Account Status:</strong> <span class="badge bg-success bg-opacity-20 text-success border border-success border-opacity-25">Active Student Account</span>
                </div>
            </div>
        </div>
    </div>
</div>

<?php
require_once __DIR__ . '/includes/footer.php';
?>
