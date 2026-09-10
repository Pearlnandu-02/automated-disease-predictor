<?php
$page_title = 'MediSense AI | About';
require_once __DIR__ . '/includes/header.php';
?>

<div class="row align-items-center py-4">
    <div class="col-lg-7">
        <span class="badge hero-badge px-3 py-2 rounded-pill fw-bold mb-3">ABOUT MEDISENSE AI</span>
        <h1 class="display-4 fw-extrabold mb-3">Intelligent Healthcare Powered by Machine Learning</h1>
        <p class="lead text-muted mb-4">
            MediSense AI is a web-based AI healthcare platform that provides educational disease prediction, clinical risk assessment, health simulation, disease and symptom information, preventive health guidance, and AI-assisted preliminary visual assessment of infections and injuries.
        </p>
    </div>
    <div class="col-lg-5 text-center">
        <div class="card-custom p-4 text-center border-info">
            <i class="bi bi-cpu-fill display-1 text-info mb-3"></i>
            <h4 class="fw-bold">Educational Project</h4>
            <p class="small text-muted mb-0">Designed for academic presentation demonstrating decoupled ML prediction microservices.</p>
        </div>
    </div>
</div>

<div class="row g-4 my-4">
    <div class="col-md-4">
        <div class="card-custom p-4 h-100">
            <div class="p-3 bg-info bg-opacity-10 text-info rounded-circle d-inline-block mb-3">
                <i class="bi bi-robot fs-3"></i>
            </div>
            <h4 class="fw-bold mb-2">AI Symptom Analysis</h4>
            <p class="text-muted small">Multi-label classification trained on structured symptom-disease matrices to evaluate statistical likelihoods.</p>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card-custom h-100 p-4">
            <div class="p-3 bg-success bg-opacity-10 text-success rounded-circle d-inline-block mb-3">
                <i class="bi bi-journal-medical fs-3"></i>
            </div>
            <h4 class="fw-bold mb-2">Comprehensive Clinical Library</h4>
            <p class="text-muted small">Clinical reference index mapping 65 medical conditions, 58 symptoms, and evidence-based prevention guidelines.</p>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card-custom h-100 p-4">
            <div class="p-3 bg-warning bg-opacity-10 text-warning rounded-circle d-inline-block mb-3">
                <i class="bi bi-shield-exclamation fs-3"></i>
            </div>
            <h4 class="fw-bold mb-2">Medical Safety First</h4>
            <p class="text-muted small">Prominent educational disclaimers ensure users consult certified medical professionals for clinical diagnosis.</p>
        </div>
    </div>
</div>

<div class="disclaimer-banner my-4 p-4 text-center">
    <i class="bi bi-exclamation-triangle-fill fs-4 me-2"></i>
    <strong>Medical Disclaimer:</strong> This system provides educational/informational AI predictions only and is not a medical diagnosis. Symptoms can have many causes. Please consult a qualified healthcare professional for proper diagnosis and treatment.
</div>

<?php
require_once __DIR__ . '/includes/footer.php';
?>
