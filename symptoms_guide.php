<?php
require_once __DIR__ . '/includes/header.php';
require_once __DIR__ . '/includes/functions.php';

$pdo = get_db_connection();

$symptoms = [];
if ($pdo) {
    try {
        $stmt = $pdo->query("SELECT * FROM symptoms ORDER BY body_system, name ASC");
        $symptoms = $stmt->fetchAll();
    } catch (PDOException $e) {
        $symptoms = [];
    }
}

$systems = [];
foreach ($symptoms as $s) {
    $systems[$s['body_system']][] = $s;
}
?>

<div class="row py-3">
    <div class="col-lg-12 text-center mb-4">
        <span class="badge bg-info text-dark px-3 py-2 rounded-pill fw-bold mb-2">SYMPTOMS GUIDE</span>
        <h1 class="display-5 fw-extrabold text-white">Body System Symptoms Index</h1>
        <p class="lead text-muted mx-auto" style="max-width: 750px;">
            Browse structured clinical symptoms categorized by anatomical organ systems. Select present symptoms to evaluate with our AI prediction engine.
        </p>
    </div>
</div>

<div class="row g-4">
    <?php foreach ($systems as $sys_name => $sym_list): ?>
        <div class="col-md-6 col-lg-4">
            <div class="card-custom p-4 h-100">
                <div class="d-flex align-items-center mb-3">
                    <div class="p-3 bg-info bg-opacity-10 text-info rounded-circle me-3">
                        <i class="bi bi-diagram-2 fs-4"></i>
                    </div>
                    <div>
                        <h4 class="fw-bold text-white mb-0"><?= sanitize($sys_name) ?></h4>
                        <span class="small text-muted"><?= count($sym_list) ?> Key Indicators</span>
                    </div>
                </div>
                <ul class="list-group list-group-flush bg-transparent">
                    <?php foreach ($sym_list as $s): ?>
                        <li class="list-group-item bg-transparent text-white border-secondary border-opacity-25 px-0 py-2 d-flex justify-content-between align-items-center">
                            <span><i class="bi bi-dot text-info fs-5 me-1"></i><?= sanitize($s['name']) ?></span>
                            <span class="badge bg-secondary bg-opacity-50 text-muted small"><?= sanitize($s['severity']) ?></span>
                        </li>
                    <?php endforeach; ?>
                </ul>
            </div>
        </div>
    <?php endforeach; ?>
</div>

<div class="text-center py-5">
    <a href="prediction.php" class="btn btn-primary-custom btn-lg rounded-pill px-5"><i class="bi bi-cpu-fill me-2"></i> Launch AI Symptom Checker</a>
</div>

<?php
require_once __DIR__ . '/includes/footer.php';
?>
