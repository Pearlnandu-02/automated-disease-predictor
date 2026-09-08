<?php
// history.php
require_once __DIR__ . '/includes/auth.php';

require_login();

$user_id = $_SESSION['user_id'];
$db = Database::getInstance();

$stmt = $db->prepare("SELECT * FROM health_assessments WHERE user_id = ? ORDER BY created_at DESC");
$stmt->execute([$user_id]);
$assessments = $stmt->fetchAll();

require_once __DIR__ . '/includes/header.php';
?>

<div class="row justify-content-center py-4">
    <div class="col-lg-11">
        <div class="card card-custom p-4 p-md-5 shadow-lg">
            <div class="d-flex justify-content-between align-items-center mb-4 pb-3 border-bottom">
                <div>
                    <h3 class="fw-bold mb-0">Prediction History Log</h3>
                    <p class="text-muted small mb-0">Complete record of your past AI healthcare risk assessments</p>
                </div>
                <a href="assessment.php" class="btn btn-info text-white rounded-pill px-4 shadow-sm">
                    <i class="bi bi-plus-lg me-1"></i> New Assessment
                </a>
            </div>

            <?php if (empty($assessments)): ?>
                <div class="text-center py-5">
                    <i class="bi bi-folder2-open fs-1 text-muted"></i>
                    <h5 class="fw-bold mt-3">No Records Found</h5>
                    <p class="text-muted small">You have not recorded any disease assessments yet.</p>
                    <a href="assessment.php" class="btn btn-info text-white rounded-pill px-4">Start Assessment Now</a>
                </div>
            <?php else: ?>
                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="table-dark">
                            <tr>
                                <th>Assessment ID</th>
                                <th>Date & Time</th>
                                <th>Assessed Condition</th>
                                <th>Predicted Risk Level</th>
                                <th>Probability</th>
                                <th class="text-center">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php foreach ($assessments as $row): ?>
                                <tr>
                                    <td class="fw-bold">#HRA-<?= $row['id'] ?></td>
                                    <td><?= date('M d, Y - h:i A', strtotime($row['created_at'])) ?></td>
                                    <td class="fw-bold text-primary"><?= sanitize($row['disease']) ?></td>
                                    <td>
                                        <span class="badge-risk-<?= strtoupper($row['risk_level']) ?>">
                                            <?= strtoupper($row['risk_level']) ?>
                                        </span>
                                    </td>
                                    <td class="fw-bold fs-6"><?= number_format($row['probability'], 1) ?>%</td>
                                    <td class="text-center">
                                        <a href="result.php?id=<?= $row['id'] ?>" class="btn btn-sm btn-outline-info rounded-pill me-1" title="View Details">
                                            <i class="bi bi-eye"></i> Details
                                        </a>
                                        <a href="simulator.php?from=<?= $row['id'] ?>" class="btn btn-sm btn-outline-success rounded-pill me-1" title="Simulate">
                                            <i class="bi bi-sliders"></i> Simulate
                                        </a>
                                        <a href="report.php?id=<?= $row['id'] ?>" target="_blank" class="btn btn-sm btn-outline-dark rounded-pill" title="Print PDF">
                                            <i class="bi bi-printer"></i>
                                        </a>
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
