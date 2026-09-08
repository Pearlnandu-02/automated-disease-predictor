<?php
// includes/footer.php
?>
        </div>
    </main>

    <!-- Footer -->
    <footer class="mt-auto">
        <div class="container">
            <div class="row gy-4 mb-4">
                <div class="col-lg-5">
                    <h5 class="text-white font-weight-bold mb-3 d-flex align-items-center">
                        <i class="bi bi-heart-pulse-fill text-info me-2"></i> HealthRisk<span class="text-info">AI</span>
                    </h5>
                    <p class="small text-muted mb-3">
                        An Academic Machine Learning project dedicated to personalized preventative health risk assessments for Diabetes and Heart Disease using Logistic Regression & Random Forest classifiers.
                    </p>
                    <div class="disclaimer-banner small">
                        <i class="bi bi-exclamation-triangle-fill me-1"></i> <strong>Academic Disclaimer:</strong> This system provides preliminary statistical risk scores for educational purposes only. It does NOT provide medical diagnoses or prescriptions.
                    </div>
                </div>
                <div class="col-lg-3 col-6 ms-auto">
                    <h6 class="text-white mb-3">Quick Navigation</h6>
                    <ul class="list-unstyled small">
                        <li class="mb-2"><a href="index.php" class="text-muted text-decoration-none">Home Overview</a></li>
                        <li class="mb-2"><a href="assessment.php" class="text-muted text-decoration-none">Risk Assessment</a></li>
                        <li class="mb-2"><a href="simulator.php" class="text-muted text-decoration-none">What-If Simulator</a></li>
                        <li class="mb-2"><a href="dashboard.php" class="text-muted text-decoration-none">User Dashboard</a></li>
                    </ul>
                </div>
                <div class="col-lg-3 col-6">
                    <h6 class="text-white mb-3">Technology Stack</h6>
                    <ul class="list-unstyled small text-muted">
                        <li class="mb-1"><i class="bi bi-check-circle me-1 text-info"></i> PHP 8 & MySQL PDO</li>
                        <li class="mb-1"><i class="bi bi-check-circle me-1 text-info"></i> Python Scikit-Learn</li>
                        <li class="mb-1"><i class="bi bi-check-circle me-1 text-info"></i> Bootstrap 5 & Chart.js</li>
                        <li class="mb-1"><i class="bi bi-check-circle me-1 text-info"></i> Joblib ML Pipelines</li>
                    </ul>
                </div>
            </div>
            <hr class="border-secondary opacity-25">
            <div class="d-flex flex-column flex-sm-row justify-content-between align-items-center small text-muted">
                <p class="mb-0">&copy; <?= date('Y') ?> HealthRisk AI - College Academic Project.</p>
                <p class="mb-0">Built with PHP, MySQL & Machine Learning</p>
            </div>
        </div>
    </footer>

    <!-- Bootstrap 5 Bundle JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <!-- Custom JS -->
    <script src="assets/js/app.js"></script>
</body>
</html>
