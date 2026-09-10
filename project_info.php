<?php
$page_title = 'MediSense AI | Project Info';
require_once __DIR__ . '/includes/header.php';
?>

<div class="row py-3">
    <div class="col-lg-12 text-center mb-4">
        <span class="badge hero-badge px-3 py-2 rounded-pill fw-bold mb-2">COLLEGE PROJECT OVERVIEW</span>
        <h1 class="display-5 fw-extrabold mb-2">MediSense AI – Intelligent Disease Prediction & Health Assistance System</h1>
        <p class="lead text-muted mx-auto" style="max-width: 800px;">
            An academic web application demonstrating the practical integration of Machine Learning classification algorithms with full-stack web technologies.
        </p>
    </div>
</div>

<div class="row g-4 mb-4">
    <div class="col-md-6">
        <div class="card-custom p-4 h-100">
            <h4 class="fw-bold mb-3"><i class="bi bi-bullseye text-info me-2"></i> Project Objectives</h4>
            <ul class="text-muted small mb-0 lh-lg">
                <li>Demonstrate how Artificial Intelligence and Machine Learning analyze symptom profiles to predict likely health conditions across 65 clinical categories.</li>
                <li>Implement a modular, decoupled web architecture separating database, web backend, and ML inference microservices.</li>
                <li>Provide structured health education across 65 common medical conditions across 11 clinical domains without prescribing dangerous treatment.</li>
                <li>Demonstrate scalable handling of high-volume healthcare datasets (7,800 records) using offline preprocessing, indexed databases, and batch training.</li>
            </ul>
        </div>
    </div>

    <div class="col-md-6">
        <div class="card-custom p-4 h-100">
            <h4 class="fw-bold mb-3"><i class="bi bi-layers-fill text-success me-2"></i> Technology Stack</h4>
            <ul class="text-muted small mb-0 lh-lg">
                <li><strong>Frontend:</strong> HTML5, CSS3, Bootstrap 5, Vanilla JavaScript, Chart.js, Theme Engine</li>
                <li><strong>Backend:</strong> PHP 8 (PDO / MySQLi), Flask WSGI (Vercel Serverless API)</li>
                <li><strong>Database:</strong> MySQL / MariaDB (`ai_healthcare` schema: 65 diseases, 58 symptoms, 250 mappings)</li>
                <li><strong>Machine Learning:</strong> Python 3.12, Scikit-Learn (Random Forest v2, Decision Trees, Naive Bayes, Logistic Regression), Pandas, NumPy, Joblib</li>
                <li><strong>Computer Vision:</strong> PIL, NumPy, SciPy (Erythema Spectrophotometry & Sobel Gradient Roughness)</li>
                <li><strong>Environment:</strong> XAMPP for local PHP/MySQL development & Vercel for cloud deployment</li>
            </ul>
        </div>
    </div>
</div>

<div class="card-custom p-4 p-md-5 mb-4">
    <h4 class="fw-bold mb-4"><i class="bi bi-diagram-3-fill text-warning me-2"></i> Platform System Architecture Flows</h4>
    
    <div class="row g-4 text-center small">
        <div class="col-lg-6">
            <div class="p-3 bg-card-subtle rounded border h-100">
                <h6 class="fw-bold text-info mb-3">1. Multi-Symptom Disease Prediction Flow</h6>
                <div class="d-flex flex-column align-items-center gap-1 font-monospace">
                    <span class="badge bg-secondary py-2 px-3">User Client</span>
                    <span class="text-muted">↓</span>
                    <span class="badge bg-secondary py-2 px-3">Symptom / Health Input</span>
                    <span class="text-muted">↓</span>
                    <span class="badge bg-primary py-2 px-3">PHP Web Interface</span>
                    <span class="text-muted">↓</span>
                    <span class="badge bg-info text-dark py-2 px-3">Prediction API Microservice</span>
                    <span class="text-muted">↓</span>
                    <span class="badge bg-warning text-dark py-2 px-3">Machine Learning Model (v2 - 65 Classes)</span>
                    <span class="text-muted">↓</span>
                    <span class="badge bg-success py-2 px-3">Disease Prediction & Confidence</span>
                    <span class="text-muted">↓</span>
                    <span class="badge bg-info py-2 px-3">Structured Educational Guidance</span>
                </div>
            </div>
        </div>

        <div class="col-lg-6">
            <div class="p-3 bg-card-subtle rounded border h-100">
                <h6 class="fw-bold text-warning mb-3">2. Computer Vision Assessment Flow</h6>
                <div class="d-flex flex-column align-items-center gap-1 font-monospace">
                    <span class="badge bg-secondary py-2 px-3">Uploaded Photo / Camera</span>
                    <span class="text-muted">↓</span>
                    <span class="badge bg-secondary py-2 px-3">Image Preprocessing & Normalization</span>
                    <span class="text-muted">↓</span>
                    <span class="badge bg-primary py-2 px-3">Image Scanner Endpoint (/scan-image)</span>
                    <span class="text-muted">↓</span>
                    <span class="badge bg-warning text-dark py-2 px-3">Visual Feature Extraction (Erythema & Texture)</span>
                    <span class="text-muted">↓</span>
                    <span class="badge bg-success py-2 px-3">Visual Feature Assessment Prototype</span>
                    <span class="text-muted">↓</span>
                    <span class="badge bg-info py-2 px-3">Educational First-Aid Guidance</span>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="disclaimer-banner p-4 text-center">
    <i class="bi bi-exclamation-triangle-fill fs-4 me-2"></i>
    <strong>Educational Project Disclaimer:</strong> This project is created for college final-year academic presentation purposes only. AI predictions and vision assessments are strictly educational triage prototypes and must NOT be interpreted as a medical diagnosis or replacement for a certified physician.
</div>

<?php
require_once __DIR__ . '/includes/footer.php';
?>
