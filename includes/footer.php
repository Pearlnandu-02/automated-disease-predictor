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
                        <li class="mb-2"><a href="risk_calculator.php">Health Risk Calculator</a></li>
                        <li class="mb-2"><a href="prediction.php">AI Symptom Checker</a></li>
                        <li class="mb-2"><a href="simulator.php">Health Simulator</a></li>
                        <li class="mb-2"><a href="report.php">Health Reports</a></li>
                    </ul>
                </div>
                <div class="col-lg-3 col-6 col-sm-4">
                    <h6 class="mb-3 fw-bold text-primary-theme">Health Library</h6>
                    <ul class="list-unstyled small">
                        <li class="mb-2"><a href="diseases.php">Disease Library</a></li>
                        <li class="mb-2"><a href="symptoms_guide.php">Symptoms Guide</a></li>
                        <li class="mb-2"><a href="prevention.php">Prevention Center</a></li>
                        <li class="mb-2"><a href="education.php">Health Education Hub</a></li>
                        <li class="mb-2"><a href="emergency.php" class="text-danger fw-semibold"><i class="bi bi-exclamation-triangle me-1"></i>Emergency Guide</a></li>
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

    <!-- Global Search Modal (Section 14) -->
    <div class="modal fade" id="globalSearchModal" tabindex="-1" aria-labelledby="globalSearchModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered modal-lg">
            <div class="modal-content border-0 shadow-lg" style="background: var(--card-bg, #1e293b); color: var(--text-primary, #f8fafc); border-radius: 20px;">
                <div class="modal-header border-bottom border-secondary border-opacity-25 px-4 pt-4 pb-3">
                    <div class="input-group input-group-lg w-100">
                        <span class="input-group-text bg-transparent border-0 text-info ps-0">
                            <i class="bi bi-search fs-4"></i>
                        </span>
                        <input type="text" id="globalSearchInput" class="form-control bg-transparent border-0 text-body fs-5 shadow-none" placeholder="Search diseases, symptoms, clinical tools, prevention..." aria-label="Search">
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                </div>
                <div class="modal-body p-4" style="max-height: 60vh; overflow-y: auto;">
                    <div id="searchQuickPills" class="d-flex flex-wrap gap-2 mb-3">
                        <span class="small text-muted me-1 align-self-center">Quick Suggestions:</span>
                        <button type="button" class="btn btn-sm btn-outline-info rounded-pill py-0 px-2 quick-search-chip" data-term="Diabetes">Diabetes</button>
                        <button type="button" class="btn btn-sm btn-outline-info rounded-pill py-0 px-2 quick-search-chip" data-term="Hypertension">Hypertension</button>
                        <button type="button" class="btn btn-sm btn-outline-info rounded-pill py-0 px-2 quick-search-chip" data-term="Chest Pain">Chest Pain</button>
                        <button type="button" class="btn btn-sm btn-outline-info rounded-pill py-0 px-2 quick-search-chip" data-term="Fever">Fever</button>
                        <button type="button" class="btn btn-sm btn-outline-info rounded-pill py-0 px-2 quick-search-chip" data-term="Risk Calculator">Risk Calculator</button>
                    </div>
                    <div id="searchResultsContainer">
                        <div class="text-center py-4 text-muted">
                            <i class="bi bi-search fs-1 opacity-25 d-block mb-2"></i>
                            Type at least 2 characters to search across MediSense AI...
                        </div>
                    </div>
                </div>
                <div class="modal-footer border-top border-secondary border-opacity-25 px-4 py-2 d-flex justify-content-between small text-muted">
                    <div>
                        <span class="badge bg-secondary-subtle text-secondary me-1">ESC</span> to close
                    </div>
                    <div>
                        <a href="diseases.php" class="text-info text-decoration-none">Browse all conditions &rarr;</a>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Bootstrap 5 Bundle JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <!-- Custom JS -->
    <script src="assets/js/app.js?v=<?= file_exists(__DIR__ . '/../assets/js/app.js') ? filemtime(__DIR__ . '/../assets/js/app.js') : '2' ?>"></script>
</body>
</html>
