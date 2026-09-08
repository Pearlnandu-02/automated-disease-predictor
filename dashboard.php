<?php
// dashboard.php
require_once __DIR__ . '/includes/auth.php';

require_login();

$user = get_logged_in_user();
$user_id = $user['id'];

$db = Database::getInstance();

// Metrics
$stmt = $db->prepare("SELECT COUNT(*) AS total FROM health_assessments WHERE user_id = ?");
$stmt->execute([$user_id]);
$total_assessments = $stmt->fetch()['total'];

$stmt = $db->prepare("SELECT * FROM health_assessments WHERE user_id = ? ORDER BY created_at DESC LIMIT 5");
$stmt->execute([$user_id]);
$recent_history = $stmt->fetchAll();

$latest_assessment = $recent_history[0] ?? null;

require_once __DIR__ . '/includes/header.php';
?>

<div class="row gy-4 py-4">
    <!-- Welcome Header -->
    <div class="col-12">
        <div class="card card-custom p-4 p-md-5 bg-dark text-white position-relative overflow-hidden" style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);">
            <div class="row align-items-center">
                <div class="col-lg-8">
                    <span class="badge bg-info text-dark px-3 py-1 mb-2">Member Dashboard</span>
                    <h2 class="fw-bold mb-2">Welcome, <?= sanitize($user['name']) ?>!</h2>
                    <p class="text-light opacity-75 mb-3">
                        Monitor your personalized healthcare assessments, track historical AI risk predictions, and run simulations.
                    </p>
                    <a href="assessment.php" class="btn btn-info text-white rounded-pill px-4 me-2">
                        <i class="bi bi-plus-circle me-1"></i> New Assessment
                    </a>
                    <a href="history.php" class="btn btn-outline-light rounded-pill px-4">
                        <i class="bi bi-clock-history me-1"></i> History Log
                    </a>
                </div>
                <div class="col-lg-4 text-center mt-4 mt-lg-0">
                    <div class="p-3 bg-white bg-opacity-10 rounded-4 backdrop-blur text-white">
                        <small class="text-uppercase fw-bold opacity-75">Total Assessments Run</small>
                        <h1 class="display-3 fw-extrabold text-info mb-0"><?= number_format($total_assessments) ?></h1>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Quick Stats Cards -->
    <div class="col-md-6 col-lg-4">
        <div class="card card-custom p-4 h-100 border-0 shadow-sm">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <span class="text-muted fw-bold small uppercase">Latest Assessment</span>
                <i class="bi bi-activity text-info fs-4"></i>
            </div>
            <?php if ($latest_assessment): ?>
                <h4 class="fw-bold text-dark mb-1"><?= sanitize($latest_assessment['disease']) ?></h4>
                <div class="mt-2">
                    <span class="badge-risk-<?= strtoupper($latest_assessment['risk_level']) ?>">
                        <?= strtoupper($latest_assessment['risk_level']) ?> RISK
                    </span>
                    <span class="ms-2 fw-bold text-secondary"><?= number_format($latest_assessment['probability'], 1) ?>%</span>
                </div>
                <small class="text-muted d-block mt-3"><i class="bi bi-calendar3 me-1"></i><?= date('M d, Y', strtotime($latest_assessment['created_at'])) ?></small>
            <?php else: ?>
                <p class="text-muted small">No assessments performed yet.</p>
                <a href="assessment.php" class="btn btn-sm btn-outline-info rounded-pill">Start Assessment</a>
            <?php endif; ?>
        </div>
    </div>

    <div class="col-md-6 col-lg-4">
        <div class="card card-custom p-4 h-100 border-0 shadow-sm">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <span class="text-muted fw-bold small uppercase">What-If Simulator</span>
                <i class="bi bi-sliders text-success fs-4"></i>
            </div>
            <h5 class="fw-bold text-dark mb-2">Interactive Risk Simulation</h5>
            <p class="text-muted small mb-3">Simulate metric adjustments and evaluate prospective probability updates.</p>
            <a href="simulator.php" class="btn btn-sm btn-success rounded-pill mt-auto">Open Simulator</a>
        </div>
    </div>

    <div class="col-md-6 col-lg-4">
        <div class="card card-custom p-4 h-100 border-0 shadow-sm">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <span class="text-muted fw-bold small uppercase">Health Reports</span>
                <i class="bi bi-file-earmark-pdf text-primary fs-4"></i>
            </div>
            <h5 class="fw-bold text-dark mb-2">Printable PDF Assessment</h5>
            <p class="text-muted small mb-3">Generate formatted health report documents for offline review.</p>
            <?php if ($latest_assessment): ?>
                <a href="report.php?id=<?= $latest_assessment['id'] ?>" target="_blank" class="btn btn-sm btn-primary rounded-pill mt-auto">Print Latest Report</a>
            <?php else: ?>
                <button class="btn btn-sm btn-secondary rounded-pill mt-auto" disabled>No Report Available</button>
            <?php endif; ?>
        </div>
    </div>

    <!-- Recent History Table -->
    <div class="col-12">
        <div class="card card-custom p-4 shadow-sm">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h5 class="fw-bold mb-0 text-dark"><i class="bi bi-clock-history me-2 text-info"></i>Recent Assessment History</h5>
                <a href="history.php" class="text-info fw-bold small text-decoration-none">View All <i class="bi bi-arrow-right"></i></a>
            </div>

            <?php if (empty($recent_history)): ?>
                <div class="text-center py-4">
                    <i class="bi bi-inbox fs-1 text-muted"></i>
                    <p class="text-muted mt-2">You haven't completed any assessments yet.</p>
                    <a href="assessment.php" class="btn btn-info text-white rounded-pill px-4">Take First Assessment</a>
                </div>
            <?php else: ?>
                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="table-light">
                            <tr>
                                <th>Date & Time</th>
                                <th>Condition</th>
                                <th>Risk Level</th>
                                <th>Probability</th>
                                <th class="text-end">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php foreach ($recent_history as $row): ?>
                                <tr>
                                    <td><i class="bi bi-calendar-event me-2 text-muted"></i><?= date('M d, Y h:i A', strtotime($row['created_at'])) ?></td>
                                    <td class="fw-bold text-dark"><?= sanitize($row['disease']) ?></td>
                                    <td>
                                        <span class="badge-risk-<?= strtoupper($row['risk_level']) ?>">
                                            <?= strtoupper($row['risk_level']) ?>
                                        </span>
                                    </td>
                                    <td class="fw-bold"><?= number_format($row['probability'], 1) ?>%</td>
                                    <td class="text-end">
                                        <a href="result.php?id=<?= $row['id'] ?>" class="btn btn-sm btn-outline-info rounded-pill">Details</a>
                                    </td>
                                </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                </div>
            <?php endif; ?>
        </div>
    </div>
</div>

<?php require_once __DIR__ . '/includes/footer.php'; ?>
