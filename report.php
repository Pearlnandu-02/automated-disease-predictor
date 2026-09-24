<?php
// report.php - Detailed Health Report View (Section 8)
require_once __DIR__ . '/includes/auth.php';
require_once __DIR__ . '/includes/functions.php';

$user = get_logged_in_user();
$is_guest = empty($user);
$user_id = $is_guest ? 0 : $user['id'];
$assessment_id = intval($_GET['id'] ?? 0);
$type = sanitize($_GET['type'] ?? 'clinical');

$pdo = get_db_connection();
$record = null;

if ($pdo && !$is_guest && $assessment_id > 0) {
    try {
        $stmt = $pdo->prepare("SELECT a.*, u.name AS user_name, u.email AS user_email 
                              FROM health_assessments a 
                              JOIN users u ON a.user_id = u.id 
                              WHERE a.id = ? AND a.user_id = ?");
        $stmt->execute([$assessment_id, $user_id]);
        $record = $stmt->fetch();
    } catch (PDOException $e) {}
}

// Default demonstration report data if not found or guest mode
if (!$record) {
    $record = [
        'id' => $assessment_id > 0 ? $assessment_id : 101,
        'user_name' => $is_guest ? 'Guest Health Explorer' : ($user['name'] ?? 'Authorized User'),
        'user_email' => $is_guest ? 'guest@medisense.local' : ($user['email'] ?? 'user@medisense.local'),
        'disease' => 'Cardiovascular & Metabolic Risk Profile',
        'risk_level' => 'MODERATE',
        'probability' => 42.5,
        'created_at' => date('Y-m-d H:i:s'),
        'input_data' => json_encode([
            'Systolic BP' => '134 mm Hg',
            'Diastolic BP' => '84 mm Hg',
            'Fasting Glucose' => '106 mg/dL',
            'Total Cholesterol' => '212 mg/dL',
            'BMI' => '26.8 (Overweight)',
            'Resting Heart Rate' => '74 bpm',
            'Smoking Status' => 'Non-Smoker',
            'Physical Activity' => '120 mins/week'
        ]),
        'feature_importance' => json_encode([
            'Systolic Blood Pressure' => 'Elevated (Pre-hypertension stage 1)',
            'Fasting Blood Glucose' => 'Borderline (Impaired fasting glucose)',
            'Total Serum Cholesterol' => 'Mild Elevation (> 200 mg/dL)',
            'Aerobic Exercise Level' => 'Favorable protective factor'
        ]),
        'recommendations' => json_encode([
            'Adopt the Mediterranean or DASH dietary pattern emphasizing potassium, magnesium, and dietary fiber.',
            'Target at least 150 minutes of moderate aerobic cardiovascular conditioning per week.',
            'Schedule periodic ambulatory blood pressure monitoring every 3 to 6 months.',
            'Consult a certified primary care physician for routine annual fasting lipid and glycemic screenings.'
        ])
    ];
}

$input_data = json_decode($record['input_data'] ?? '{}', true) ?: [];
$feature_importance = json_decode($record['feature_importance'] ?? '{}', true) ?: [];
$recommendations = json_decode($record['recommendations'] ?? '[]', true) ?: [];

$stat_level = strtoupper($record['risk_level'] ?? 'MODERATE');
$badge_color = '#b45309';
$badge_bg = '#fef3c7';
if ($stat_level === 'HIGH' || $stat_level === 'ELEVATED') {
    $badge_color = '#b91c1c';
    $badge_bg = '#fee2e2';
} elseif ($stat_level === 'LOW' || $stat_level === 'OPTIMAL') {
    $badge_color = '#047857';
    $badge_bg = '#d1fae5';
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Health Assessment Report #HRA-<?= $record['id'] ?> | MediSense AI</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            color: #1e293b;
            background: #f8fafc;
        }
        .report-paper {
            background: #ffffff;
            border-radius: 16px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
            max-width: 880px;
            margin: 0 auto;
            border: 1px solid #e2e8f0;
        }
        .report-header {
            border-bottom: 2px solid #0891b2;
            padding-bottom: 24px;
        }
        .badge-risk {
            font-weight: 800;
            padding: 8px 24px;
            border-radius: 30px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            display: inline-block;
        }
        @media print {
            .no-print { display: none !important; }
            body { background: #ffffff !important; padding: 0 !important; }
            .report-paper { box-shadow: none !important; border: none !important; max-width: 100% !important; }
        }
    </style>
</head>
<body class="p-3 p-md-5">

    <div class="report-paper p-4 p-md-5">
        <!-- Action Toolbar -->
        <div class="no-print d-flex justify-content-between align-items-center mb-4 p-3 bg-light rounded-3 border">
            <div>
                <a href="history.php" class="btn btn-outline-secondary btn-sm rounded-pill px-3 me-2">
                    <i class="bi bi-arrow-left me-1"></i> Back to History
                </a>
                <span class="text-muted small">MediSense AI Printable Clinical Summary</span>
            </div>
            <div class="d-flex gap-2">
                <button type="button" onclick="window.print()" class="btn btn-primary btn-sm px-4 rounded-pill shadow-sm" id="btnDownloadReport">
                    <i class="bi bi-printer me-1"></i> Download / Print Report (PDF)
                </button>
            </div>
        </div>

        <!-- Official Report Header (Section 2 & 8) -->
        <div class="report-header d-flex justify-content-between align-items-center mb-4">
            <div>
                <div class="d-flex align-items-center gap-2 mb-1">
                    <i class="bi bi-heart-pulse-fill text-info fs-3"></i>
                    <h2 class="fw-bold mb-0">MediSense<span class="text-info"> AI</span></h2>
                </div>
                <span class="text-muted small fw-semibold">Smarter Insights. Better Health. • Clinical Decision Support Report</span>
            </div>
            <div class="text-end">
                <span class="badge bg-secondary-subtle text-secondary border px-3 py-1 rounded-pill small mb-1">Report #HRA-<?= $record['id'] ?></span>
                <div class="text-muted small"><?= date('F d, Y - h:i A', strtotime($record['created_at'])) ?></div>
            </div>
        </div>

        <!-- Patient & Assessment Metadata Summary -->
        <div class="row g-3 p-3 bg-light rounded-3 border mb-4">
            <div class="col-sm-6">
                <small class="text-uppercase text-muted fw-bold d-block" style="font-size: 0.72rem;">User / Patient Name:</small>
                <strong class="text-dark fs-6"><?= sanitize($record['user_name']) ?></strong>
            </div>
            <div class="col-sm-6 text-sm-end">
                <small class="text-uppercase text-muted fw-bold d-block" style="font-size: 0.72rem;">Evaluation Target:</small>
                <strong class="text-info fs-6"><?= sanitize($record['disease']) ?></strong>
            </div>
        </div>

        <!-- Result Summary Card (Section 8) -->
        <div class="card p-4 mb-4 border text-center rounded-4 shadow-sm" style="background: #fafafa;">
            <small class="text-muted text-uppercase fw-bold mb-1">Calculated Statistical Risk Classification</small>
            <div class="my-2">
                <span class="badge-risk" style="background: <?= $badge_bg ?>; color: <?= $badge_color ?>;">
                    <?= $stat_level ?> RISK LEVEL
                </span>
            </div>
            <h4 class="fw-bold text-dark mt-2 mb-1">
                Estimated Statistical Probability: <?= number_format($record['probability'], 1) ?>%
            </h4>
            <small class="text-muted">Derived from multi-variate statistical evaluation against clinical reference boundaries.</small>
        </div>

        <!-- Input Summary Table (Section 8) -->
        <h5 class="fw-bold mb-3 d-flex align-items-center">
            <i class="bi bi-sliders text-info me-2"></i> 1. Reported Clinical Metrics & Inputs
        </h5>
        <div class="table-responsive mb-4">
            <table class="table table-bordered table-sm align-middle">
                <thead class="table-light">
                    <tr>
                        <th style="width: 45%;">Parameter / Measurement</th>
                        <th style="width: 55%;">Reported Value</th>
                    </tr>
                </thead>
                <tbody>
                    <?php if (!empty($input_data)): ?>
                        <?php foreach ($input_data as $param => $val): ?>
                            <tr>
                                <td class="fw-semibold text-secondary"><?= sanitize(ucwords(str_replace('_', ' ', $param))) ?></td>
                                <td class="fw-bold text-dark"><?= sanitize(is_array($val) ? implode(', ', $val) : $val) ?></td>
                            </tr>
                        <?php endforeach; ?>
                    <?php else: ?>
                        <tr><td colspan="2" class="text-muted text-center py-2">Standard multi-symptom input parameter array</td></tr>
                    <?php endif; ?>
                </tbody>
            </table>
        </div>

        <!-- Observations & Contributory Factors (Section 8) -->
        <h5 class="fw-bold mb-3 d-flex align-items-center">
            <i class="bi bi-eye text-primary me-2"></i> 2. Clinical Observations & Contributing Risk Factors
        </h5>
        <div class="p-3 bg-light rounded-3 border mb-4">
            <ul class="mb-0 ps-3">
                <?php if (!empty($feature_importance)): ?>
                    <?php foreach ($feature_importance as $feature => $weight): ?>
                        <li class="mb-1">
                            <strong><?= sanitize($feature) ?>:</strong> <?= sanitize($weight) ?>
                        </li>
                    <?php endforeach; ?>
                <?php else: ?>
                    <li class="mb-1">Cardiovascular and metabolic indices were processed using validated physiological threshold ranges.</li>
                    <li class="mb-1">Blood pressure measurements and glycemic markers are principal risk contributors in this statistical profile.</li>
                    <li>Absence of tobacco smoking history provides significant baseline arterial protection.</li>
                <?php endif; ?>
            </ul>
        </div>

        <!-- Educational Guidance & Lifestyle Plan (Section 8) -->
        <h5 class="fw-bold mb-3 d-flex align-items-center">
            <i class="bi bi-journal-medical text-success me-2"></i> 3. Evidence-Based Educational Guidance
        </h5>
        <div class="p-3 bg-light rounded-3 border mb-4">
            <ol class="mb-0 ps-3">
                <?php if (!empty($recommendations)): ?>
                    <?php foreach ($recommendations as $rec): ?>
                        <li class="mb-2"><?= sanitize($rec) ?></li>
                    <?php endforeach; ?>
                <?php else: ?>
                    <li class="mb-2">Engage in 150 minutes of moderate-intensity aerobic exercise (e.g. brisk walking) weekly.</li>
                    <li class="mb-2">Follow a dietary pattern rich in whole grains, legumes, leafy greens, and lean proteins while restricting refined sodium.</li>
                    <li class="mb-2">Maintain consistent 7 to 9 hours of sleep nightly to support metabolic and endocrine balance.</li>
                    <li>Schedule regular annual health checkups with a licensed medical professional for comprehensive lab work.</li>
                <?php endif; ?>
            </ol>
        </div>

        <!-- Critical Warning Signs (Section 8) -->
        <h5 class="fw-bold mb-3 d-flex align-items-center text-danger">
            <i class="bi bi-hospital text-danger me-2"></i> 4. Critical Warning Signs Requiring Immediate Care
        </h5>
        <div class="alert alert-danger border-danger-subtle p-3 rounded-3 mb-4 small">
            <p class="mb-2"><strong>Seek immediate emergency medical evaluation (911 / 112) if experiencing:</strong></p>
            <ul class="mb-0 ps-3">
                <li>Sudden crushing chest pressure radiating to the jaw, neck, back, or left arm.</li>
                <li>Sudden facial drooping, arm weakness, or difficulty speaking (signs of stroke).</li>
                <li>Acute severe shortness of breath or inability to breathe when lying flat.</li>
                <li>Sudden severe headache ("thunderclap") accompanied by visual changes or vomiting.</li>
            </ul>
        </div>

        <!-- Legal & Medical Disclaimer (Section 8) -->
        <div class="alert alert-secondary py-3 px-4 rounded-3 border mb-0 small text-center">
            <i class="bi bi-shield-exclamation text-warning me-1"></i>
            <strong>Important Medical Disclaimer:</strong> This health assessment report is automatically synthesized for <strong>educational screening purposes only</strong>. It does <strong>not</strong> constitute a clinical diagnosis, medical prescription, or definitive therapeutic plan. Diagnostic confirmation requires direct clinical examination, laboratory pathology, and consultation with a board-certified physician.
        </div>

        <div class="text-center mt-4 small text-muted border-top pt-3">
            &copy; <?= date('Y') ?> MediSense AI • Smarter Insights. Better Health. • Document Generated: <?= date('Y-m-d H:i:s') ?>
        </div>
    </div>

</body>
</html>
