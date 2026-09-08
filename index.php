<?php
// index.php
require_once __DIR__ . '/includes/header.php';
?>

<!-- Hero Banner -->
<div class="row align-items-center my-4 py-5 px-4 rounded-4 bg-dark text-white shadow-lg position-relative overflow-hidden" style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);">
    <div class="col-lg-7 z-1">
        <span class="badge bg-info text-dark font-weight-bold px-3 py-2 rounded-pill mb-3">
            <i class="bi bi-cpu me-1"></i> AI & ML Healthcare Technology
        </span>
        <h1 class="display-4 fw-extrabold mb-3">Personalized Healthcare Risk Assessment</h1>
        <p class="lead text-light mb-4 opacity-90">
            Assess your risk levels for <strong>Diabetes</strong> and <strong>Heart Disease</strong> using machine learning models trained on verified medical datasets. Get instant feature breakdowns and personalized preventative advice.
        </p>
        <div class="d-flex flex-wrap gap-3">
            <?php if (is_logged_in()): ?>
                <a href="assessment.php" class="btn btn-info btn-lg text-white rounded-pill px-4 shadow">
                    <i class="bi bi-play-circle-fill me-2"></i> Start Risk Assessment
                </a>
                <a href="dashboard.php" class="btn btn-outline-light btn-lg rounded-pill px-4">
                    <i class="bi bi-speedometer2 me-2"></i> View Dashboard
                </a>
            <?php else: ?>
                <a href="register.php" class="btn btn-info btn-lg text-white rounded-pill px-4 shadow">
                    <i class="bi bi-person-plus-fill me-2"></i> Create Free Account
                </a>
                <a href="login.php" class="btn btn-outline-light btn-lg rounded-pill px-4">
                    <i class="bi bi-box-arrow-in-right me-2"></i> Login to Platform
                </a>
            <?php endif; ?>
        </div>
    </div>
    <div class="col-lg-5 text-center mt-4 mt-lg-0 z-1">
        <div class="card-custom p-4 bg-white text-dark shadow-lg">
            <h5 class="fw-bold mb-3 text-primary"><i class="bi bi-shield-check me-2"></i>Supported ML Assessments</h5>
            <div class="d-flex align-items-center p-3 mb-3 bg-light rounded-3">
                <i class="bi bi-droplet-fill text-danger fs-2 me-3"></i>
                <div class="text-start">
                    <h6 class="mb-0 fw-bold">Diabetes Risk Assessment</h6>
                    <small class="text-muted">Pima Indians Clinical Model (Glucose, BMI, Age, Insulin)</small>
                </div>
            </div>
            <div class="d-flex align-items-center p-3 bg-light rounded-3">
                <i class="bi bi-heart-pulse-fill text-danger fs-2 me-3"></i>
                <div class="text-start">
                    <h6 class="mb-0 fw-bold">Heart Disease Assessment</h6>
                    <small class="text-muted">UCI Cardiac Dataset (BP, Cholesterol, Thalach, ST Peak)</small>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Mandatory Educational Disclaimer -->
<div class="disclaimer-banner my-4 shadow-sm">
    <div class="d-flex align-items-center">
        <i class="bi bi-info-circle-fill fs-4 me-3 text-warning"></i>
        <div>
            <strong class="d-block text-dark">Important Academic Disclaimer:</strong>
            This platform is developed exclusively for educational research and academic demonstration. All predictions generated are statistical likelihoods produced by Machine Learning classifiers (Logistic Regression & Random Forest) and must not be used as medical diagnoses or therapeutic instructions.
        </div>
    </div>
</div>

<!-- Features Section -->
<div class="row py-4 g-4">
    <div class="col-md-4">
        <div class="card card-custom h-100 p-4 border-0 shadow-sm">
            <div class="bg-info bg-opacity-10 p-3 rounded-circle d-inline-block mb-3 text-info" style="width: 56px; height: 56px;">
                <i class="bi bi-cpu-fill fs-3"></i>
            </div>
            <h5 class="fw-bold mb-2">Dual ML Architecture</h5>
            <p class="text-muted small mb-0">
                Utilizes trained Scikit-Learn pipelines evaluated across Logistic Regression, Decision Trees, and Random Forests with verified accuracy metrics.
            </p>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card card-custom h-100 p-4 border-0 shadow-sm">
            <div class="bg-primary bg-opacity-10 p-3 rounded-circle d-inline-block mb-3 text-primary" style="width: 56px; height: 56px;">
                <i class="bi bi-bar-chart-line-fill fs-3"></i>
            </div>
            <h5 class="fw-bold mb-2">Explainable AI (XAI)</h5>
            <p class="text-muted small mb-0">
                Transparently breakdown which specific body parameters (e.g. Glucose level or BMI) influenced your risk prediction probability most.
            </p>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card card-custom h-100 p-4 border-0 shadow-sm">
            <div class="bg-success bg-opacity-10 p-3 rounded-circle d-inline-block mb-3 text-success" style="width: 56px; height: 56px;">
                <i class="bi bi-sliders fs-3"></i>
            </div>
            <h5 class="fw-bold mb-2">What-If Health Simulator</h5>
            <p class="text-muted small mb-0">
                Simulate potential health improvements interactively (e.g., lower BMI or Glucose) to visualize how parameter adjustments impact risk score.
            </p>
        </div>
    </div>
</div>

<?php require_once __DIR__ . '/includes/footer.php'; ?>
