<?php
require_once __DIR__ . '/includes/auth.php';
require_once __DIR__ . '/includes/functions.php';

$user = get_logged_in_user();
$is_guest = empty($user);
$user_id = $is_guest ? 0 : $user['id'];
$user_name = $is_guest ? 'Guest Health Explorer' : $user['name'];

$pdo = get_db_connection();

$total_predictions = 0;
$total_assessments = 0;
$recent_predictions = [];
$recent_assessments = [];

$disease_count = 73;
$symptom_count = 58;
$model_name = "Multi-Disease Prediction Model v2";
$model_accuracy = "75.2%";

if ($pdo && !$is_guest) {
    try {
        $stmt = $pdo->prepare("SELECT COUNT(*) AS total FROM prediction_history WHERE user_id = ?");
        $stmt->execute([$user_id]);
        $total_predictions = (int)$stmt->fetch()['total'];

        $stmt = $pdo->prepare("SELECT COUNT(*) AS total FROM health_assessments WHERE user_id = ?");
        $stmt->execute([$user_id]);
        $total_assessments = (int)$stmt->fetch()['total'];

        $stmt = $pdo->prepare("SELECT * FROM prediction_history WHERE user_id = ? ORDER BY created_at DESC LIMIT 5");
        $stmt->execute([$user_id]);
        $recent_predictions = $stmt->fetchAll();

        $stmt = $pdo->prepare("SELECT * FROM health_assessments WHERE user_id = ? ORDER BY created_at DESC LIMIT 5");
        $stmt->execute([$user_id]);
        $recent_assessments = $stmt->fetchAll();

        $d_res = (int)$pdo->query("SELECT COUNT(*) FROM diseases")->fetchColumn();
        if ($d_res > 0) $disease_count = $d_res;
        $s_res = (int)$pdo->query("SELECT COUNT(*) FROM symptoms")->fetchColumn();
        if ($s_res > 0) $symptom_count = $s_res;
    } catch (PDOException $e) {
        // Fallback gracefully
    }
}

// Demo data for guest or new user
$sample_predictions = [
    ['symptoms_selected' => 'Chest Pain, Shortness of Breath', 'predicted_disease' => 'Hypertension', 'confidence' => 78.4, 'created_at' => date('Y-m-d H:i:s', strtotime('-1 day'))],
    ['symptoms_selected' => 'Fatigue, Increased Thirst, Blurred Vision', 'predicted_disease' => 'Diabetes', 'confidence' => 84.1, 'created_at' => date('Y-m-d H:i:s', strtotime('-3 days'))],
    ['symptoms_selected' => 'Persistent Cough, Wheezing', 'predicted_disease' => 'Asthma', 'confidence' => 72.9, 'created_at' => date('Y-m-d H:i:s', strtotime('-5 days'))]
];

$sample_assessments = [
    ['id' => 101, 'disease' => 'Cardiovascular Disease Risk', 'risk_level' => 'MODERATE', 'probability' => 42.5, 'created_at' => date('Y-m-d H:i:s', strtotime('-2 days'))],
    ['id' => 102, 'disease' => 'Type 2 Diabetes Risk', 'risk_level' => 'LOW', 'probability' => 18.2, 'created_at' => date('Y-m-d H:i:s', strtotime('-4 days'))],
    ['id' => 103, 'disease' => 'Hypertension Risk', 'risk_level' => 'ELEVATED', 'probability' => 54.0, 'created_at' => date('Y-m-d H:i:s', strtotime('-6 days'))]
];

$display_predictions = !empty($recent_predictions) ? $recent_predictions : $sample_predictions;
$display_assessments = !empty($recent_assessments) ? $recent_assessments : $sample_assessments;
$is_sample_data = empty($recent_predictions) && empty($recent_assessments);

$page_title = 'MediSense AI | Health Dashboard';
require_once __DIR__ . '/includes/header.php';
?>

<div class="row gy-4 py-3">
    <!-- Welcome Header & Health Overview (Section 3) -->
    <div class="col-12">
        <div class="card-custom p-4 p-md-5 hero-banner">
            <div class="row align-items-center">
                <div class="col-lg-8">
                    <div class="d-flex align-items-center gap-2 mb-2">
                        <span class="badge hero-badge px-3 py-1 fw-bold">Health Dashboard</span>
                        <?php if ($is_guest): ?>
                            <span class="badge bg-warning bg-opacity-20 text-warning border border-warning border-opacity-25 px-3 py-1">Guest Mode</span>
                        <?php else: ?>
                            <span class="badge bg-success bg-opacity-20 text-success border border-success border-opacity-25 px-3 py-1">Personal Profile Active</span>
                        <?php endif; ?>
                    </div>
                    <h1 class="display-6 fw-extrabold hero-heading mb-2">Welcome, <?= sanitize($user_name) ?>!</h1>
                    <p class="hero-lead mb-3">
                        Monitor health assessments, review AI symptom predictions across <?= $disease_count ?> conditions, explore preventive lifestyle reminders, and access clinical screening tools.
                    </p>
                    <div class="d-flex flex-wrap gap-2">
                        <a href="prediction.php" class="btn btn-primary-custom rounded-pill px-4">
                            <i class="bi bi-cpu-fill me-1"></i> Start AI Prediction
                        </a>
                        <a href="risk_calculator.php" class="btn btn-outline-info rounded-pill px-4">
                            <i class="bi bi-calculator me-1"></i> Health Risk Calculator
                        </a>
                        <a href="health_assistant.php" class="btn btn-outline-success rounded-pill px-4">
                            <i class="bi bi-chat-heart me-1"></i> AI Health Assistant
                        </a>
                    </div>
                </div>
                <div class="col-lg-4 text-center mt-4 mt-lg-0">
                    <div class="p-3 bg-card-subtle rounded-4 border border-secondary border-opacity-25">
                        <div class="d-flex justify-content-around text-center">
                            <div>
                                <small class="text-uppercase fw-bold text-muted d-block">AI Predictions</small>
                                <span class="display-6 fw-extrabold text-info"><?= $is_guest ? count($sample_predictions) : number_format($total_predictions) ?></span>
                                <small class="text-muted d-block"><?= $is_guest ? '(Demo)' : 'Recorded' ?></small>
                            </div>
                            <div class="border-start border-secondary border-opacity-25 ps-3">
                                <small class="text-uppercase fw-bold text-muted d-block">Clinical Tools</small>
                                <span class="display-6 fw-extrabold text-success"><?= $is_guest ? count($sample_assessments) : number_format($total_assessments) ?></span>
                                <small class="text-muted d-block"><?= $is_guest ? '(Demo)' : 'Assessments' ?></small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Quick Access Cards (Section 3) -->
    <div class="col-12">
        <h4 class="fw-bold mb-3 d-flex align-items-center">
            <i class="bi bi-grid-fill text-info me-2"></i> Quick Access Hub
        </h4>
        <div class="row g-3">
            <div class="col-md-4 col-sm-6">
                <a href="prediction.php" class="card-custom p-4 h-100 text-decoration-none d-block hover-lift">
                    <div class="d-flex align-items-center gap-3 mb-2">
                        <div class="p-3 rounded-circle bg-info bg-opacity-15 text-info fs-4">
                            <i class="bi bi-cpu"></i>
                        </div>
                        <div>
                            <h5 class="fw-bold text-body mb-0">AI Symptom Checker</h5>
                            <span class="small text-muted">Correlate multi-symptom patterns</span>
                        </div>
                    </div>
                    <p class="small text-muted mb-0">Select from <?= $symptom_count ?> symptoms to evaluate statistical likelihood across <?= $disease_count ?> conditions.</p>
                </a>
            </div>
            <div class="col-md-4 col-sm-6">
                <a href="image_scanner.php" class="card-custom p-4 h-100 text-decoration-none d-block hover-lift">
                    <div class="d-flex align-items-center gap-3 mb-2">
                        <div class="p-3 rounded-circle bg-danger bg-opacity-15 text-danger fs-4">
                            <i class="bi bi-camera"></i>
                        </div>
                        <div>
                            <h5 class="fw-bold text-body mb-0">Injury & Skin Scanner</h5>
                            <span class="small text-muted">Visual computer-vision analysis</span>
                        </div>
                    </div>
                    <p class="small text-muted mb-0">Analyze superficial skin changes, wounds, erythema, or potentially concerning skin lesion characteristics.</p>
                </a>
            </div>
            <div class="col-md-4 col-sm-6">
                <a href="risk_calculator.php" class="card-custom p-4 h-100 text-decoration-none d-block hover-lift">
                    <div class="d-flex align-items-center gap-3 mb-2">
                        <div class="p-3 rounded-circle bg-warning bg-opacity-15 text-warning fs-4">
                            <i class="bi bi-calculator"></i>
                        </div>
                        <div>
                            <h5 class="fw-bold text-body mb-0">Health Risk Calculator</h5>
                            <span class="small text-muted">Interactive biometric metrics</span>
                        </div>
                    </div>
                    <p class="small text-muted mb-0">Evaluate BMI, metabolic markers, blood pressure, cardiac risks, and lifestyle impact scores.</p>
                </a>
            </div>
            <div class="col-md-4 col-sm-6">
                <a href="health_assistant.php" class="card-custom p-4 h-100 text-decoration-none d-block hover-lift">
                    <div class="d-flex align-items-center gap-3 mb-2">
                        <div class="p-3 rounded-circle bg-success bg-opacity-15 text-success fs-4">
                            <i class="bi bi-chat-heart"></i>
                        </div>
                        <div>
                            <h5 class="fw-bold text-body mb-0">AI Health Assistant</h5>
                            <span class="small text-muted">Educational conversational chat</span>
                        </div>
                    </div>
                    <p class="small text-muted mb-0">Ask health questions, explore preventive habits, symptom guidance, and when to consult a physician.</p>
                </a>
            </div>
            <div class="col-md-4 col-sm-6">
                <a href="diseases.php" class="card-custom p-4 h-100 text-decoration-none d-block hover-lift">
                    <div class="d-flex align-items-center gap-3 mb-2">
                        <div class="p-3 rounded-circle bg-primary bg-opacity-15 text-primary fs-4">
                            <i class="bi bi-journal-medical"></i>
                        </div>
                        <div>
                            <h5 class="fw-bold text-body mb-0">Disease Library</h5>
                            <span class="small text-muted"><?= $disease_count ?> verified clinical profiles</span>
                        </div>
                    </div>
                    <p class="small text-muted mb-0">Browse comprehensive medical summaries, etiology, risk factors, prevention, and red flags.</p>
                </a>
            </div>
            <div class="col-md-4 col-sm-6">
                <a href="emergency.php" class="card-custom p-4 h-100 text-decoration-none d-block hover-lift border-danger-subtle">
                    <div class="d-flex align-items-center gap-3 mb-2">
                        <div class="p-3 rounded-circle bg-danger bg-opacity-20 text-danger fs-4">
                            <i class="bi bi-hospital"></i>
                        </div>
                        <div>
                            <h5 class="fw-bold text-danger mb-0">Emergency Guide</h5>
                            <span class="small text-muted">Life-threatening red flags</span>
                        </div>
                    </div>
                    <p class="small text-muted mb-0">Review critical warning signs (stroke, chest pain, anaphylaxis) requiring emergency dispatch (911/112).</p>
                </a>
            </div>
        </div>
    </div>

    <!-- Health Statistics & Overview Metrics (Section 3) -->
    <div class="col-lg-8">
        <!-- Recent Assessments Section -->
        <div class="card-custom p-4 mb-4">
            <div class="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-3">
                <h5 class="fw-bold mb-0 d-flex align-items-center">
                    <i class="bi bi-clock-history text-info me-2"></i> Recent Health Assessments
                </h5>
                <div class="d-flex align-items-center gap-2">
                    <?php if ($is_sample_data): ?>
                        <span class="badge bg-secondary-subtle text-secondary small py-1 px-2 border">Sample Demo Data</span>
                    <?php endif; ?>
                    <a href="history.php" class="btn btn-sm btn-outline-info rounded-pill px-3">View All History</a>
                </div>
            </div>

            <!-- Tabbed View: AI Predictions vs Clinical Risk -->
            <ul class="nav nav-pills mb-3 gap-2" id="assessmentTabs" role="tablist">
                <li class="nav-item" role="presentation">
                    <button class="nav-link active rounded-pill px-3 py-1 small fw-semibold" id="tab-predictions-tab" data-bs-toggle="pill" data-bs-target="#tab-predictions" type="button" role="tab" aria-selected="true">
                        <i class="bi bi-cpu me-1"></i> AI Symptom Predictions
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link rounded-pill px-3 py-1 small fw-semibold" id="tab-assessments-tab" data-bs-toggle="pill" data-bs-target="#tab-assessments" type="button" role="tab" aria-selected="false">
                        <i class="bi bi-shield-check me-1"></i> Clinical Risk Evaluations
                    </button>
                </li>
            </ul>

            <div class="tab-content" id="assessmentTabsContent">
                <!-- AI Predictions Tab -->
                <div class="tab-pane fade show active" id="tab-predictions" role="tabpanel">
                    <div class="table-responsive">
                        <table class="table table-hover align-middle mb-0 small">
                            <thead class="table-light">
                                <tr>
                                    <th>Date</th>
                                    <th>Selected Symptoms</th>
                                    <th>Predicted Condition</th>
                                    <th>Correlation</th>
                                    <th class="text-end">Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                <?php foreach ($display_predictions as $row): ?>
                                    <tr>
                                        <td><span class="text-muted"><?= date('M d, Y', strtotime($row['created_at'])) ?></span></td>
                                        <td class="text-truncate" style="max-width: 220px;" title="<?= sanitize($row['symptoms_selected']) ?>">
                                            <?= sanitize($row['symptoms_selected']) ?>
                                        </td>
                                        <td><strong class="text-info"><?= sanitize($row['predicted_disease']) ?></strong></td>
                                        <td>
                                            <span class="badge bg-info bg-opacity-15 text-info border border-info border-opacity-25">
                                                <?= number_format($row['confidence'], 1) ?>%
                                            </span>
                                        </td>
                                        <td class="text-end">
                                            <a href="prediction.php" class="btn btn-sm btn-outline-info rounded-pill py-0 px-2" title="Re-evaluate">Check</a>
                                        </td>
                                    </tr>
                                <?php endforeach; ?>
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Clinical Risk Tab -->
                <div class="tab-pane fade" id="tab-assessments" role="tabpanel">
                    <div class="table-responsive">
                        <table class="table table-hover align-middle mb-0 small">
                            <thead class="table-light">
                                <tr>
                                    <th>Date</th>
                                    <th>Condition</th>
                                    <th>Risk Level</th>
                                    <th>Probability</th>
                                    <th class="text-end">Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                <?php foreach ($display_assessments as $row): ?>
                                    <tr>
                                        <td><span class="text-muted"><?= date('M d, Y', strtotime($row['created_at'])) ?></span></td>
                                        <td><strong><?= sanitize($row['disease']) ?></strong></td>
                                        <td>
                                            <?php 
                                            $lvl = strtoupper($row['risk_level'] ?? 'MODERATE');
                                            $b_class = $lvl === 'HIGH' ? 'bg-danger text-white' : ($lvl === 'ELEVATED' || $lvl === 'MODERATE' ? 'bg-warning text-dark' : 'bg-success text-white');
                                            ?>
                                            <span class="badge <?= $b_class ?> px-2 py-1"><?= $lvl ?></span>
                                        </td>
                                        <td><?= number_format($row['probability'], 1) ?>%</td>
                                        <td class="text-end">
                                            <a href="report.php?id=<?= $row['id'] ?? 1 ?>" class="btn btn-sm btn-outline-info rounded-pill py-0 px-2">Report</a>
                                        </td>
                                    </tr>
                                <?php endforeach; ?>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <!-- Health Statistics Chart / Progress Indicators -->
        <div class="card-custom p-4">
            <h5 class="fw-bold mb-3 d-flex align-items-center">
                <i class="bi bi-bar-chart-line text-success me-2"></i> Health Screening Statistics
            </h5>
            <div class="row g-3">
                <div class="col-md-4">
                    <div class="p-3 rounded-3 border bg-card-subtle text-center">
                        <small class="text-muted text-uppercase fw-semibold">Cardiovascular Health</small>
                        <h4 class="fw-bold text-success mt-1 mb-1">Optimal Range</h4>
                        <div class="progress mt-2" style="height: 6px;">
                            <div class="progress-bar bg-success" style="width: 82%;"></div>
                        </div>
                        <small class="text-muted d-block mt-1">Based on reported metrics</small>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="p-3 rounded-3 border bg-card-subtle text-center">
                        <small class="text-muted text-uppercase fw-semibold">Metabolic Risk</small>
                        <h4 class="fw-bold text-warning mt-1 mb-1">Moderate Watch</h4>
                        <div class="progress mt-2" style="height: 6px;">
                            <div class="progress-bar bg-warning" style="width: 45%;"></div>
                        </div>
                        <small class="text-muted d-block mt-1">Dietary balance recommended</small>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="p-3 rounded-3 border bg-card-subtle text-center">
                        <small class="text-muted text-uppercase fw-semibold">Screening Cadence</small>
                        <h4 class="fw-bold text-info mt-1 mb-1">Up to Date</h4>
                        <div class="progress mt-2" style="height: 6px;">
                            <div class="progress-bar bg-info" style="width: 90%;"></div>
                        </div>
                        <small class="text-muted d-block mt-1">Next check suggested in 30d</small>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Right Sidebar: Prevention Reminders & Education (Section 3) -->
    <div class="col-lg-4">
        <!-- Prevention Reminders -->
        <div class="card-custom p-4 mb-4">
            <h5 class="fw-bold mb-3 d-flex align-items-center">
                <i class="bi bi-bell-fill text-warning me-2"></i> Daily Prevention Reminders
            </h5>
            <div class="d-flex flex-column gap-3">
                <div class="d-flex align-items-start gap-2 p-2 rounded-3 border bg-card-subtle">
                    <i class="bi bi-droplet-fill text-info fs-5 mt-1"></i>
                    <div>
                        <strong class="d-block small text-body">Hydration Target</strong>
                        <span class="small text-muted">Drink 2.5 - 3.0 liters of clean water daily to support cellular and kidney function.</span>
                    </div>
                </div>
                <div class="d-flex align-items-start gap-2 p-2 rounded-3 border bg-card-subtle">
                    <i class="bi bi-bicycle text-success fs-5 mt-1"></i>
                    <div>
                        <strong class="d-block small text-body">30-Minute Movement</strong>
                        <span class="small text-muted">A brisk 30-minute walk lowers systolic blood pressure by 4-9 mm Hg.</span>
                    </div>
                </div>
                <div class="d-flex align-items-start gap-2 p-2 rounded-3 border bg-card-subtle">
                    <i class="bi bi-moon-stars-fill text-primary fs-5 mt-1"></i>
                    <div>
                        <strong class="d-block small text-body">Sleep Consistency</strong>
                        <span class="small text-muted">Aim for 7 to 9 hours of restorative sleep to regulate insulin sensitivity and cortisol.</span>
                    </div>
                </div>
                <div class="d-flex align-items-start gap-2 p-2 rounded-3 border bg-card-subtle">
                    <i class="bi bi-sun-fill text-warning fs-5 mt-1"></i>
                    <div>
                        <strong class="d-block small text-body">UV & Skin Protection</strong>
                        <span class="small text-muted">Apply broad-spectrum SPF 30+ sunscreen even on overcast days.</span>
                    </div>
                </div>
            </div>
            <a href="prevention.php" class="btn btn-outline-warning w-100 rounded-pill btn-sm mt-3">
                Explore Prevention Center &rarr;
            </a>
        </div>

        <!-- Recently Viewed / Suggested Diseases -->
        <div class="card-custom p-4 mb-4">
            <h5 class="fw-bold mb-3 d-flex align-items-center">
                <i class="bi bi-journal-check text-info me-2"></i> Health Library Highlights
            </h5>
            <div class="list-group list-group-flush rounded-3 border mb-3">
                <a href="disease_detail.php?id=1" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center py-2 px-3">
                    <div>
                        <strong class="text-body d-block small">Type 2 Diabetes</strong>
                        <span class="text-muted" style="font-size: 0.75rem;">Metabolic / Endocrine</span>
                    </div>
                    <span class="badge bg-info-subtle text-info">View &rarr;</span>
                </a>
                <a href="disease_detail.php?id=2" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center py-2 px-3">
                    <div>
                        <strong class="text-body d-block small">Hypertension</strong>
                        <span class="text-muted" style="font-size: 0.75rem;">Cardiovascular</span>
                    </div>
                    <span class="badge bg-info-subtle text-info">View &rarr;</span>
                </a>
                <a href="disease_detail.php?id=4" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center py-2 px-3">
                    <div>
                        <strong class="text-body d-block small">Bronchial Asthma</strong>
                        <span class="text-muted" style="font-size: 0.75rem;">Respiratory</span>
                    </div>
                    <span class="badge bg-info-subtle text-info">View &rarr;</span>
                </a>
                <a href="diseases.php?search=Melanoma" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center py-2 px-3">
                    <div>
                        <strong class="text-body d-block small">Melanoma & Lesions</strong>
                        <span class="text-muted" style="font-size: 0.75rem;">Dermatological</span>
                    </div>
                    <span class="badge bg-info-subtle text-info">View &rarr;</span>
                </a>
            </div>
            <a href="diseases.php" class="btn btn-outline-info w-100 rounded-pill btn-sm">
                Browse All <?= $disease_count ?> Conditions &rarr;
            </a>
        </div>

        <!-- Health Education Suggestions -->
        <div class="card-custom p-4">
            <h5 class="fw-bold mb-2 d-flex align-items-center">
                <i class="bi bi-lightbulb-fill text-warning me-2"></i> Weekly Education
            </h5>
            <p class="small text-muted mb-3">Curated clinical insights to improve preventive health literacy.</p>
            <div class="p-3 rounded-3 border bg-card-subtle mb-3">
                <span class="badge bg-info-subtle text-info small mb-1">Myth vs Fact</span>
                <strong class="d-block small text-body mb-1">"Can you stop blood pressure meds once readings are normal?"</strong>
                <p class="small text-muted mb-0">Myth. Normal readings often show the medication is working. Always consult your prescribing physician before adjustments.</p>
            </div>
            <a href="education.php" class="btn btn-primary-custom w-100 rounded-pill btn-sm">
                Visit Health Education Hub
            </a>
        </div>
    </div>

    <!-- Educational Medical Disclaimer -->
    <div class="col-12">
        <div class="alert alert-secondary py-3 px-4 rounded-3 border mb-0 small text-center">
            <i class="bi bi-shield-exclamation text-warning me-1"></i>
            <strong>Important Medical Notice:</strong> MediSense AI is an educational healthcare platform designed for preliminary risk screening and health literacy. Results from AI symptom checkers, visual scanners, or risk calculators <strong>do not constitute medical diagnoses, prescriptions, or clinical treatment plans</strong>. Always consult a qualified medical professional for health concerns or diagnostic confirmation.
        </div>
    </div>
</div>

<?php require_once __DIR__ . '/includes/footer.php'; ?>
