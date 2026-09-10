<?php
require_once __DIR__ . '/includes/header.php';
require_once __DIR__ . '/includes/functions.php';

$pdo = get_db_connection();

$id = isset($_GET['id']) ? intval($_GET['id']) : 0;
$name = isset($_GET['name']) ? trim($_GET['name']) : '';

$disease = null;
$symptoms = [];

if ($pdo) {
    try {
        if ($id > 0) {
            $stmt = $pdo->prepare("SELECT * FROM diseases WHERE id = ?");
            $stmt->execute([$id]);
            $disease = $stmt->fetch();
        } elseif ($name !== '') {
            $stmt = $pdo->prepare("SELECT * FROM diseases WHERE name LIKE ?");
            $stmt->execute(['%' . $name . '%']);
            $disease = $stmt->fetch();
        }

        if ($disease) {
            $sym_stmt = $pdo->prepare("
                SELECT s.* FROM symptoms s
                JOIN disease_symptoms ds ON s.id = ds.symptom_id
                WHERE ds.disease_id = ?
            ");
            $sym_stmt->execute([$disease['id']]);
            $symptoms = $sym_stmt->fetchAll();
        }
    } catch (PDOException $e) {
        $disease = null;
    }
}

if (!$disease) {
    echo '<div class="text-center py-5"><h3 class="text-white">Disease record not found.</h3><a href="diseases.php" class="btn btn-outline-info rounded-pill px-4 mt-3">Back to Diseases List</a></div>';
    require_once __DIR__ . '/includes/footer.php';
    exit;
}
?>

<div class="row py-3">
    <div class="col-lg-12">
        <a href="diseases.php" class="btn btn-outline-secondary btn-sm rounded-pill mb-3">
            <i class="bi bi-arrow-left me-1"></i> Back to Disease Library
        </a>
        <div class="d-flex align-items-center gap-3">
            <h1 class="display-4 fw-extrabold mb-0"><?= sanitize($disease['name']) ?></h1>
            <span class="badge bg-info text-white px-3 py-2 rounded-pill fw-bold fs-6"><?= sanitize($disease['category']) ?></span>
        </div>
        <p class="lead text-muted mt-3"><?= sanitize($disease['short_description']) ?></p>
    </div>
</div>

<div class="row g-4 my-2">
    <!-- Main Info Column -->
    <div class="col-lg-8">
        <!-- Associated Symptoms -->
        <div class="card-custom p-4 mb-4">
            <h4 class="fw-bold mb-3 d-flex align-items-center">
                <i class="bi bi-activity text-info me-2"></i> Associated Common Symptoms
            </h4>
            <div class="d-flex flex-wrap gap-2">
                <?php if (!empty($symptoms)): ?>
                    <?php foreach ($symptoms as $s): ?>
                        <span class="badge bg-info bg-opacity-20 text-info border border-info border-opacity-25 px-3 py-2 rounded-pill">
                            <?= sanitize($s['name']) ?> (<?= sanitize($s['body_system']) ?>)
                        </span>
                    <?php endforeach; ?>
                <?php else: ?>
                    <span class="text-muted small">Standard clinical symptom constellation.</span>
                <?php endif; ?>
            </div>
        </div>

        <!-- Causes & Pathophysiology -->
        <div class="card-custom p-4 mb-4">
            <h4 class="fw-bold mb-2 d-flex align-items-center">
                <i class="bi bi-diagram-3-fill text-warning me-2"></i> Causes & Etiology
            </h4>
            <p class="text-muted mb-0"><?= sanitize($disease['causes']) ?></p>
        </div>

        <!-- Risk Factors -->
        <div class="card-custom p-4 mb-4">
            <h4 class="fw-bold mb-2 d-flex align-items-center">
                <i class="bi bi-exclamation-octagon-fill text-danger me-2"></i> Risk Factors
            </h4>
            <p class="text-muted mb-0"><?= sanitize($disease['risk_factors']) ?></p>
        </div>

        <!-- Prevention Strategies -->
        <div class="card-custom p-4 mb-4">
            <h4 class="fw-bold mb-2 d-flex align-items-center">
                <i class="bi bi-shield-check text-success me-2"></i> Prevention & Risk Reduction
            </h4>
            <p class="text-muted mb-0"><?= sanitize($disease['prevention']) ?></p>
        </div>
    </div>

    <!-- Sidebar Column -->
    <div class="col-lg-4">
        <!-- General Management -->
        <div class="card-custom p-4 mb-4 border-info">
            <h5 class="fw-bold mb-3"><i class="bi bi-journal-medical text-info me-2"></i> General Management</h5>
            <p class="small text-muted mb-0"><?= sanitize($disease['management']) ?></p>
        </div>

        <!-- When to Seek Medical Attention -->
        <div class="card-custom p-4 mb-4 border-warning">
            <h5 class="fw-bold text-warning mb-3"><i class="bi bi-telephone-plus-fill me-2"></i> When to Seek Care</h5>
            <p class="small text-muted mb-0"><?= sanitize($disease['when_to_seek_care']) ?></p>
        </div>

        <!-- Action Card -->
        <div class="card-custom p-4 text-center">
            <h6 class="fw-bold mb-2">Experiencing Symptoms?</h6>
            <p class="small text-muted mb-3">Check your symptom profile against our AI ML classification engine.</p>
            <a href="prediction.php" class="btn btn-primary-custom w-100 rounded-pill"><i class="bi bi-cpu me-1"></i> Check Symptoms Now</a>
        </div>
    </div>
</div>

<div class="disclaimer-banner my-4 p-4 text-center">
    <i class="bi bi-exclamation-triangle-fill fs-4 me-2"></i>
    <strong>Educational Disclaimer:</strong> Information provided is for educational reference only and does NOT constitute specific medical advice, diagnosis, or prescription instructions. Always consult a certified physician.
</div>

<?php
require_once __DIR__ . '/includes/footer.php';
?>
