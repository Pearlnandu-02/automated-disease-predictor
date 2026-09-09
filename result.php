<?php
// result.php
require_once __DIR__ . '/includes/auth.php';

require_login();

$assessment_id = intval($_GET['id'] ?? 0);
$user_id = $_SESSION['user_id'];

if ($assessment_id <= 0) {
    set_flash_message('danger', 'Invalid assessment reference.');
    redirect('dashboard.php');
}

$db = Database::getInstance();
$stmt = $db->prepare("SELECT * FROM health_assessments WHERE id = ? AND user_id = ?");
$stmt->execute([$assessment_id, $user_id]);
$record = $stmt->fetch();

if (!$record) {
    set_flash_message('danger', 'Assessment record not found or access denied.');
    redirect('dashboard.php');
}

$input_data = json_decode($record['input_data'], true) ?: [];
$feature_importance = json_decode($record['feature_importance'], true) ?: [];
$recommendations = json_decode($record['recommendations'], true) ?: [];

$risk_level = strtoupper($record['risk_level']);
$probability = floatval($record['probability']);

$gauge_color = '#10b981'; // Green LOW
if ($risk_level === 'MODERATE') {
    $gauge_color = '#f59e0b'; // Amber MODERATE
} elseif ($risk_level === 'HIGH') {
    $gauge_color = '#ef4444'; // Red HIGH
}

require_once __DIR__ . '/includes/header.php';
?>

<div class="row justify-content-center py-4">
    <div class="col-lg-10">
        <!-- Top Status Card -->
        <div class="card card-custom p-4 p-md-5 mb-4 shadow-lg">
            <div class="row align-items-center">
                <div class="col-md-7 border-end-md mb-4 mb-md-0">
                    <div class="d-flex align-items-center mb-2">
                        <span class="badge bg-secondary me-2"><?= sanitize($record['disease']) ?> Assessment</span>
                        <small class="text-muted"><i class="bi bi-clock me-1"></i><?= date('M d, Y - h:i A', strtotime($record['created_at'])) ?></small>
                    </div>
                    <h2 class="fw-bold mb-3">Predicted Risk Level: 
                        <span class="badge-risk-<?= $risk_level ?>"><?= $risk_level ?></span>
                    </h2>
                    <p class="text-muted mb-0">
                        Based on the clinical parameters provided, the Machine Learning classifier calculated a statistical probability score of <strong><?= number_format($probability, 1) ?>%</strong> for potential risk factors.
                    </p>
                </div>
                <div class="col-md-5 d-flex flex-column align-items-center justify-content-center">
                    <div class="gauge-container mb-2" style="--gauge-percent: <?= $probability * 3.6 ?>deg; --gauge-color: <?= $gauge_color ?>;">
                        <div class="gauge-inner">
                            <span class="gauge-value"><?= number_format($probability, 0) ?>%</span>
                            <span class="gauge-label">Probability</span>
                        </div>
                    </div>
                    <small class="text-muted font-weight-bold">Statistical Risk Model Score</small>
                </div>
            </div>
        </div>

        <!-- Explainable AI (XAI) Section -->
        <div class="card card-custom p-4 p-md-5 mb-4 shadow-sm">
            <h4 class="fw-bold mb-3 d-flex align-items-center">
                <i class="bi bi-bar-chart-line-fill text-info me-2"></i> Explainable AI (XAI): Model Feature Influence
            </h4>
            <p class="text-muted small mb-4">
                The chart below displays the relative weight and importance of your input parameters in driving the ML model's prediction result.
            </p>

            <div class="row align-items-center">
                <div class="col-lg-7 mb-4 mb-lg-0">
                    <canvas id="featureChart" height="240"></canvas>
                </div>
                <div class="col-lg-5">
                    <h6 class="fw-bold mb-3">Input Parameter Breakdown:</h6>
                    <ul class="list-group list-group-flush small">
                        <?php foreach ($input_data as $key => $val): ?>
                            <li class="list-group-item d-flex justify-content-between align-items-center bg-transparent border-secondary border-opacity-25">
                                <span class="fw-semibold text-secondary"><?= sanitize($key) ?></span>
                                <span class="badge bg-info bg-opacity-10 text-info border border-info border-opacity-25 fw-bold"><?= sanitize($val) ?></span>
                            </li>
                        <?php endforeach; ?>
                    </ul>
                </div>
            </div>
        </div>

        <!-- Personalized Preventive Guidance -->
        <div class="card card-custom p-4 p-md-5 mb-4 shadow-sm">
            <h4 class="fw-bold mb-3 d-flex align-items-center">
                <i class="bi bi-shield-check text-success me-2"></i> General Personalized Preventive Guidance
            </h4>
            <p class="text-muted small mb-4">
                Rule-based wellness suggestions tailored to your reported metrics:
            </p>
            <div class="row g-3">
                <?php foreach ($recommendations as $index => $tip): ?>
                    <div class="col-md-6">
                        <div class="p-3 rounded-3 bg-secondary bg-opacity-10 border border-secondary border-opacity-25 h-100 d-flex align-items-start">
                            <i class="bi bi-check-circle-fill text-success fs-5 me-3 mt-1"></i>
                            <span class="small fw-medium"><?= sanitize($tip) ?></span>
                        </div>
                    </div>
                <?php endforeach; ?>
            </div>
        </div>

        <!-- Mandatory Disclaimer -->
        <div class="disclaimer-banner mb-4">
            <i class="bi bi-exclamation-triangle-fill me-1"></i>
            <strong>Educational Disclaimer:</strong> Predictions and recommendations generated by HealthRisk AI are strictly for preliminary assessment and academic study. They do not constitute formal medical diagnosis or treatment advice.
        </div>

        <!-- Actions -->
        <div class="d-flex flex-wrap gap-3 justify-content-between align-items-center">
            <a href="assessment.php" class="btn btn-outline-secondary rounded-pill px-4">
                <i class="bi bi-arrow-left me-1"></i> New Assessment
            </a>
            <div class="d-flex gap-2">
                <a href="simulator.php?from=<?= $assessment_id ?>" class="btn btn-info text-white rounded-pill px-4 shadow-sm">
                    <i class="bi bi-sliders me-1"></i> Launch What-If Simulator
                </a>
                <a href="report.php?id=<?= $assessment_id ?>" target="_blank" class="btn btn-dark rounded-pill px-4 shadow-sm">
                    <i class="bi bi-printer me-1"></i> Print PDF Report
                </a>
            </div>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const ctx = document.getElementById('featureChart').getContext('2d');
    const featureData = <?= json_encode($feature_importance) ?>;
    
    const labels = Object.keys(featureData);
    const dataValues = Object.values(featureData).map(val => (val * 100).toFixed(1));

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Relative Importance (%)',
                data: dataValues,
                backgroundColor: 'rgba(13, 148, 136, 0.75)',
                borderColor: '#0d9488',
                borderWidth: 1.5,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: 'Importance Weight (%)' }
                }
            }
        }
    });
});
</script>

<?php require_once __DIR__ . '/includes/footer.php'; ?>
