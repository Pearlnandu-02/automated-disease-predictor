<?php
require_once __DIR__ . '/includes/header.php';
?>

<div class="row py-3">
    <div class="col-lg-12 text-center mb-4">
        <span class="badge bg-info text-white px-3 py-2 rounded-pill fw-bold mb-2">COLLEGE PROJECT OVERVIEW</span>
        <h1 class="display-5 fw-extrabold mb-2">AI Healthcare – Intelligent Disease Prediction & Health Assistance System</h1>
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
                <li>Demonstrate how Artificial Intelligence and Machine Learning analyze symptom profiles to predict likely health conditions.</li>
                <li>Implement a modular, decoupled web architecture separating database, web backend, and ML inference services.</li>
                <li>Provide structured health education across 25 common medical diseases without prescribing dangerous treatment.</li>
                <li>Demonstrate scalable handling of large healthcare datasets using offline preprocessing, indexed databases, and batch training.</li>
            </ul>
        </div>
    </div>

    <div class="col-md-6">
        <div class="card-custom p-4 h-100">
            <h4 class="fw-bold mb-3"><i class="bi bi-layers-fill text-success me-2"></i> Technology Stack</h4>
            <ul class="text-muted small mb-0 lh-lg">
                <li><strong>Frontend:</strong> HTML5, CSS3, Bootstrap 5, Vanilla JavaScript, Chart.js</li>
                <li><strong>Backend:</strong> PHP 8 (PDO / MySQLi), Flask WSGI (Vercel Serverless API)</li>
                <li><strong>Database:</strong> MySQL / MariaDB (`ai_healthcare` database schema)</li>
                <li><strong>Machine Learning:</strong> Python 3.12, Scikit-Learn (Logistic Regression, Decision Trees, Random Forest, Naive Bayes), Pandas, NumPy, Joblib</li>
                <li><strong>Computer Vision:</strong> PIL, NumPy, SciPy (Erythema Spectrophotometry & Sobel Roughness)</li>
                <li><strong>Environment:</strong> XAMPP for local PHP/MySQL development & Vercel for cloud deployment</li>
            </ul>
        </div>
    </div>
</div>

<div class="card-custom p-4 p-md-5 mb-4">
    <h4 class="fw-bold mb-3"><i class="bi bi-diagram-3-fill text-warning me-2"></i> System Architecture Flow</h4>
    <div class="p-4 bg-card-subtle rounded border text-center font-monospace text-info small">
        Browser Client (HTML/JS) ➔ PHP / Flask Web Server ➔ Python ML & CV REST API ➔ Serialized Joblib Model / Vision Analysis ➔ Structured JSON Response
    </div>
</div>

<div class="disclaimer-banner p-4 text-center">
    <i class="bi bi-exclamation-triangle-fill fs-4 me-2"></i>
    <strong>Educational Project Disclaimer:</strong> This project is created for college final-year presentation purposes only. AI predictions are strictly educational and must NOT be interpreted as a medical diagnosis or replacement for a certified doctor.
</div>

<?php
require_once __DIR__ . '/includes/footer.php';
?>
