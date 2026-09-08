<?php
// report.php
require_once __DIR__ . '/includes/auth.php';

require_login();

$assessment_id = intval($_GET['id'] ?? 0);
$user_id = $_SESSION['user_id'];

$db = Database::getInstance();
$stmt = $db->prepare("SELECT a.*, u.name AS user_name, u.email AS user_email 
                      FROM health_assessments a 
                      JOIN users u ON a.user_id = u.id 
                      WHERE a.id = ? AND a.user_id = ?");
$stmt->execute([$assessment_id, $user_id]);
$record = $stmt->fetch();

if (!$record) {
    die("Report not found or access denied.");
}

$input_data = json_decode($record['input_data'], true) ?: [];
$feature_importance = json_decode($record['feature_importance'], true) ?: [];
$recommendations = json_decode($record['recommendations'], true) ?: [];
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Health Assessment Report #HRA-<?= $record['id'] ?></title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { font-family: 'Helvetica Neue', Arial, sans-serif; color: #1e293b; background: #fff; }
        .report-header { border-bottom: 2px solid #0d9488; padding-bottom: 20px; margin-bottom: 30px; }
        .badge-risk { font-weight: bold; padding: 6px 16px; border-radius: 20px; text-transform: uppercase; }
        .badge-LOW { background: #d1fae5; color: #047857; }
        .badge-MODERATE { background: #fef3c7; color: #b45309; }
        .badge-HIGH { background: #fee2e2; color: #b91c1c; }
        @media print {
            .no-print { display: none !important; }
            body { padding: 0; }
        }
    </style>
</head>
<body class="p-4 p-md-5">

    <div class="container" style="max-width: 850px;">
        <!-- Print Header & Controls -->
        <div class="no-print d-flex justify-content-between align-items-center mb-4 p-3 bg-light rounded border">
            <div>
                <strong class="text-dark">Printable Assessment PDF Report</strong>
                <span class="text-muted ms-2 small">Click the button to open browser print/save dialog.</span>
            </div>
            <button onclick="window.print()" class="btn btn-primary btn-sm px-4 rounded-pill">
                <i class="bi bi-printer me-1"></i> Print / Save PDF
            </button>
        </div>

        <!-- Official Report Header -->
        <div class="report-header d-flex justify-content-between align-items-center">
            <div>
                <h2 class="fw-bold text-dark mb-1">HealthRisk<span class="text-info">AI</span> Report</h2>
                <span class="text-muted small">Academic Machine Learning Risk Assessment System</span>
            </div>
            <div class="text-end">
                <h5 class="fw-bold mb-0">Report ID: #HRA-<?= $record['id'] ?></h5>
                <small class="text-muted"><?= date('F d, Y - h:i A', strtotime($record['created_at'])) ?></small>
            </div>
        </div>

        <!-- Patient / User Info Box -->
        <div class="row bg-light p-3 rounded border mb-4">
            <div class="col-md-6">
                <small class="text-uppercase text-muted fw-bold">Patient Name:</small>
                <div class="fw-bold text-dark"><?= sanitize($record['user_name']) ?></div>
            </div>
            <div class="col-md-6 text-md-end mt-2 mt-md-0">
                <small class="text-uppercase text-muted fw-bold">Assessed Condition:</small>
                <div class="fw-bold text-teal"><?= sanitize($record['disease']) ?></div>
            </div>
        </div>

        <!-- Prediction Result Summary -->
        <div class="card p-4 mb-4 border shadow-sm text-center">
            <h6 class="text-muted text-uppercase fw-bold mb-2">Calculated Statistical Risk Level</h6>
            <h2 class="mb-2">
                <span class="badge-risk badge-<?= strtoupper($record['risk_level']) ?>">
                    <?= strtoupper($record['risk_level']) ?> RISK
                </span>
            </h2>
            <h4 class="fw-bold text-dark mt-2">
                Prediction Probability: <?= number_format($record['probability'], 1) ?>%
            </h4>
        </div>

        <!-- Inputs Breakdown Table -->
        <h5 class="fw-bold mb-3">Reported Clinical Metrics</h5>
        <table class="table table-bordered align-middle mb-4">
            <thead class="table-light">
                <tr>
                    <th>Clinical Parameter</th>
                    <th class="text-end">Recorded Value</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($input_data as $param => $val): ?>
                    <tr>
                        <td class="fw-semibold text-secondary"><?= sanitize($param) ?></td>
                        <td class="text-end fw-bold"><?= sanitize($val) ?></td>
                    </tr>
                <?php endforeach; ?>
            </tbody>
        </table>

        <!-- Model Factor Influence -->
        <h5 class="fw-bold mb-3">Model Factor Importance Weights (XAI)</h5>
        <div class="mb-4 p-3 border rounded bg-light">
            <?php foreach ($feature_importance as $feat => $weight): ?>
                <div class="mb-2">
                    <div class="d-flex justify-content-between small fw-bold mb-1">
                        <span><?= sanitize($feat) ?></span>
                        <span><?= number_format($weight * 100, 1) ?>%</span>
                    </div>
                    <div class="progress" style="height: 8px;">
                        <div class="progress-bar bg-info" style="width: <?= $weight * 100 ?>%"></div>
                    </div>
                </div>
            <?php endforeach; ?>
        </div>

        <!-- Preventive Guidance -->
        <h5 class="fw-bold mb-3">Preventive Educational Guidance</h5>
        <ul class="list-group mb-4">
            <?php foreach ($recommendations as $tip): ?>
                <li class="list-group-item small"><i class="bi bi-check2 text-success me-2"></i><?= sanitize($tip) ?></li>
            <?php endforeach; ?>
        </ul>

        <!-- Disclaimer -->
        <div class="alert alert-warning small mb-0">
            <strong>Educational Disclaimer:</strong> This health assessment report is automatically generated by an academic machine learning platform for preliminary educational purposes only. It does NOT constitute medical diagnosis or prescription. Always consult a qualified physician for healthcare advice.
        </div>
    </div>

</body>
</html>
