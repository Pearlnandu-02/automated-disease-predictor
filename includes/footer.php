<?php
// includes/footer.php
?>
        </div>
    </main>

    <!-- Footer -->
    <footer class="mt-auto">
        <div class="container">
            <div class="row gy-4 mb-4">
                <div class="col-lg-4">
                    <h5 class="font-weight-bold mb-3 d-flex align-items-center">
                        <i class="bi bi-heart-pulse-fill text-info me-2"></i> MediSense<span class="text-info"> AI</span>
                    </h5>
                    <p class="small text-muted mb-2 fw-semibold text-info">
                        Smarter Insights. Better Health.
                    </p>
                    <p class="small text-muted mb-3">
                        MediSense AI is a web-based AI healthcare platform that provides educational disease prediction, clinical risk assessment, health simulation, disease and symptom information, preventive health guidance, and AI-assisted preliminary visual assessment of infections and injuries.
                    </p>
                    <div class="disclaimer-banner small">
                        <i class="bi bi-exclamation-triangle-fill me-1"></i> <strong>Academic Disclaimer:</strong> This system provides preliminary educational assessments and risk scores. It does NOT provide medical diagnoses or prescriptions. Always consult a qualified healthcare professional.
                    </div>
                </div>
                <div class="col-lg-2 col-6 col-sm-4 ms-auto">
                    <h6 class="mb-3 fw-bold text-primary-theme">Explore</h6>
                    <ul class="list-unstyled small">
                        <li class="mb-2"><a href="index.php">Home</a></li>
                        <li class="mb-2"><a href="about.php">About</a></li>
                        <li class="mb-2"><a href="prediction.php">AI Prediction</a></li>
                        <li class="mb-2"><a href="image_scanner.php"><i class="bi bi-camera me-1 text-info"></i>Injury Scanner</a></li>
                    </ul>
                </div>
                <div class="col-lg-3 col-6 col-sm-4">
                    <h6 class="mb-3 fw-bold text-primary-theme">Clinical Tools</h6>
                    <ul class="list-unstyled small">
                        <li class="mb-2"><a href="assessment.php">Clinical Risk Assessment</a></li>
                        <li class="mb-2"><a href="simulator.php">Health Simulator</a></li>
                        <li class="mb-2"><a href="assessment.php?type=diabetes">Diabetes Assessment</a></li>
                    </ul>
                </div>
                <div class="col-lg-3 col-6 col-sm-4">
                    <h6 class="mb-3 fw-bold text-primary-theme">Health Library</h6>
                    <ul class="list-unstyled small">
                        <li class="mb-2"><a href="diseases.php">Diseases Library</a></li>
                        <li class="mb-2"><a href="symptoms_guide.php">Symptoms Guide</a></li>
                        <li class="mb-2"><a href="prevention.php">Prevention</a></li>
                    </ul>
                </div>
            </div>
            <hr class="border-secondary opacity-25">
            <div class="d-flex flex-column flex-sm-row justify-content-between align-items-center small text-muted">
                <p class="mb-0">&copy; <?= date('Y') ?> MediSense AI – Smarter Insights. Better Health.</p>
                <p class="mb-0">Built with PHP, MySQL & Machine Learning</p>
            </div>
        </div>
    </footer>

    <!-- Bootstrap 5 Bundle JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <!-- Custom JS -->
    <script src="assets/js/app.js?v=<?= file_exists(__DIR__ . '/../assets/js/app.js') ? filemtime(__DIR__ . '/../assets/js/app.js') : '2' ?>"></script>
</body>
</html>
