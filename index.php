<?php
// index.php - AI Healthcare Landing Page
require_once __DIR__ . '/includes/header.php';
?>

<!-- Hero Section -->
<div class="hero-banner p-4 p-md-5 mb-5 text-center position-relative">
    <div class="row align-items-center py-4">
        <div class="col-lg-7 text-lg-start z-1">
            <span class="badge bg-white text-dark fw-bold px-3 py-2 rounded-pill mb-3 shadow-sm">
                <i class="bi bi-stars text-info me-1"></i> AI & ML Healthcare Decision Support
            </span>
            <h1 class="display-4 fw-extrabold text-white mb-3">Smarter Healthcare Powered by Artificial Intelligence</h1>
            <p class="lead text-white-50 mb-4">
                Explore intelligent multi-symptom disease predictions, clinical chronic disease risk assessments, what-if health parameter simulations, and computer vision infection & injury scanning.
            </p>
            <div class="d-flex flex-wrap gap-3 justify-content-center justify-content-lg-start">
                <a href="prediction.php" class="btn btn-primary-custom btn-lg">
                    <i class="bi bi-cpu-fill me-2"></i> Run AI Symptom Check
                </a>
                <a href="image_scanner.php" class="btn btn-outline-light btn-lg rounded-pill px-4">
                    <i class="bi bi-camera me-2"></i> Injury Image Scanner
                </a>
                <a href="diseases.php" class="btn btn-outline-light btn-lg rounded-pill px-4">
                    <i class="bi bi-journal-medical me-2"></i> Explore 25 Diseases
                </a>
            </div>
        </div>
        <div class="col-lg-5 text-center mt-4 mt-lg-0 z-1">
            <div class="card-custom p-4 text-center border-info">
                <i class="bi bi-heart-pulse-fill display-1 text-info mb-3"></i>
                <h4 class="fw-bold mb-2">25 Diseases Covered</h4>
                <p class="small text-muted mb-3">Structured disease descriptions, common symptoms, causes, risk factors, and medical care advice.</p>
                <div class="d-flex justify-content-around text-center pt-3 border-top border-secondary border-opacity-25">
                    <div>
                        <h3 class="fw-bold text-info mb-0">30</h3>
                        <small class="text-muted">Symptoms</small>
                    </div>
                    <div>
                        <h3 class="fw-bold text-success mb-0">84.1%</h3>
                        <small class="text-muted">ML Accuracy</small>
                    </div>
                    <div>
                        <h3 class="fw-bold text-warning mb-0">5,000+</h3>
                        <small class="text-muted">Records</small>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Mandatory Educational Safety Disclaimer -->
<div class="disclaimer-banner my-4 shadow-sm p-4">
    <div class="d-flex align-items-center">
        <i class="bi bi-exclamation-triangle-fill fs-3 me-3 text-warning"></i>
        <div>
            <strong class="d-block mb-1">Educational & Informational Disclaimer:</strong>
            This system provides educational/informational AI predictions only and is not a medical diagnosis. Symptoms can have many causes. Please consult a qualified healthcare professional for proper diagnosis and treatment.
        </div>
    </div>
</div>

<!-- Statistics Cards -->
<div class="row g-4 my-2">
    <div class="col-md-3 col-6">
        <div class="card-custom text-center p-3">
            <h2 class="fw-extrabold text-info mb-1">25</h2>
            <p class="small text-muted mb-0">Diseases Modeled</p>
        </div>
    </div>
    <div class="col-md-3 col-6">
        <div class="card-custom text-center p-3">
            <h2 class="fw-extrabold text-success mb-1">30</h2>
            <p class="small text-muted mb-0">Clinical Symptoms</p>
        </div>
    </div>
    <div class="col-md-3 col-6">
        <div class="card-custom text-center p-3">
            <h2 class="fw-extrabold text-warning mb-1">4</h2>
            <p class="small text-muted mb-0">ML Architectures</p>
        </div>
    </div>
    <div class="col-md-3 col-6">
        <div class="card-custom text-center p-3">
            <h2 class="fw-extrabold text-danger mb-1">100%</h2>
            <p class="small text-muted mb-0">Decoupled API</p>
        </div>
    </div>
</div>

<!-- How It Works Section -->
<div class="card-custom p-4 p-md-5 my-4">
    <h3 class="fw-bold mb-4 text-center">How AI Healthcare Works</h3>
    <div class="row g-4 text-center">
        <div class="col-md-4">
            <div class="p-3 bg-card-subtle rounded border border-secondary border-opacity-25 h-100">
                <div class="display-5 text-info mb-2">1</div>
                <h5 class="fw-bold">Select Symptoms</h5>
                <p class="small text-muted mb-0">Choose present symptoms from our interactive categorized body systems tiles.</p>
            </div>
        </div>
        <div class="col-md-4">
            <div class="p-3 bg-card-subtle rounded border border-secondary border-opacity-25 h-100">
                <div class="display-5 text-success mb-2">2</div>
                <h5 class="fw-bold">AI Model Inference</h5>
                <p class="small text-muted mb-0">Scikit-Learn classification algorithms evaluate probability across 25 disease targets.</p>
            </div>
        </div>
        <div class="col-md-4">
            <div class="p-3 bg-card-subtle rounded border border-secondary border-opacity-25 h-100">
                <div class="display-5 text-warning mb-2">3</div>
                <h5 class="fw-bold">Review Guidance</h5>
                <p class="small text-muted mb-0">View predicted condition, animated confidence, influencing factors, and health guidance.</p>
            </div>
        </div>
    </div>
</div>

<!-- Features Section -->
<div class="row py-3 g-4">
    <div class="col-md-3 col-sm-6">
        <div class="card-custom h-100 p-4">
            <div class="bg-info bg-opacity-10 p-3 rounded-circle d-inline-block mb-3 text-info">
                <i class="bi bi-cpu-fill fs-3"></i>
            </div>
            <h5 class="fw-bold mb-2">Multi-Label ML Model</h5>
            <p class="text-muted small mb-0">
                Utilizes Random Forest & Logistic Regression classifiers trained on clinical symptom matrices.
            </p>
        </div>
    </div>
    <div class="col-md-3 col-sm-6">
        <div class="card-custom h-100 p-4">
            <div class="bg-primary bg-opacity-10 p-3 rounded-circle d-inline-block mb-3 text-info">
                <i class="bi bi-camera-fill fs-3"></i>
            </div>
            <h5 class="fw-bold mb-2">AI Image Scanner</h5>
            <p class="text-muted small mb-0">
                Computer vision erythema indexing and edge roughness analysis for wounds, rashes, and swelling.
            </p>
        </div>
    </div>
    <div class="col-md-3 col-sm-6">
        <div class="card-custom h-100 p-4">
            <div class="bg-warning bg-opacity-10 p-3 rounded-circle d-inline-block mb-3 text-warning">
                <i class="bi bi-database-check fs-3"></i>
            </div>
            <h5 class="fw-bold mb-2">Large Dataset Scaling</h5>
            <p class="text-muted small mb-0">
                Data preprocessing occurs offline before model training; web client receives serialized inference responses.
            </p>
        </div>
    </div>
    <div class="col-md-3 col-sm-6">
        <div class="card-custom h-100 p-4">
            <div class="bg-success bg-opacity-10 p-3 rounded-circle d-inline-block mb-3 text-success">
                <i class="bi bi-sliders fs-3"></i>
            </div>
            <h5 class="fw-bold mb-2">What-If Risk Simulator</h5>
            <p class="text-muted small mb-0">
                Interactively adjust biological health parameters to observe real-time recalculations of risk probability.
            </p>
        </div>
    </div>
</div>

<?php
require_once __DIR__ . '/includes/footer.php';
?>
