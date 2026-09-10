<?php
$page_title = 'MediSense AI | Diseases Library';
require_once __DIR__ . '/includes/header.php';
require_once __DIR__ . '/includes/functions.php';

$pdo = get_db_connection();

$search = isset($_GET['search']) ? trim($_GET['search']) : '';
$category = isset($_GET['category']) ? trim($_GET['category']) : '';

$diseases = [];
$categories = [];

if ($pdo) {
    try {
        // Fetch categories
        $cat_stmt = $pdo->query("SELECT DISTINCT category FROM diseases ORDER BY category ASC");
        $categories = $cat_stmt->fetchAll(PDO::FETCH_COLUMN);

        // Build search query
        $sql = "SELECT * FROM diseases WHERE 1=1";
        $params = [];

        if ($search !== '') {
            $sql .= " AND (name LIKE ? OR short_description LIKE ? OR causes LIKE ?)";
            $params[] = "%$search%";
            $params[] = "%$search%";
            $params[] = "%$search%";
        }

        if ($category !== '') {
            $sql .= " AND category = ?";
            $params[] = $category;
        }

        $sql .= " ORDER BY name ASC";
        $stmt = $pdo->prepare($sql);
        $stmt->execute($params);
        $diseases = $stmt->fetchAll();
    } catch (PDOException $e) {
        $diseases = [];
    }
}
?>

<div class="row py-3">
    <div class="col-lg-12 text-center mb-4">
        <span class="badge hero-badge px-3 py-2 rounded-pill fw-bold mb-2">DISEASE DATABASE</span>
        <h1 class="display-5 fw-extrabold mb-2">Medical Conditions Library (<?= count($diseases) ?> Conditions)</h1>
        <p class="lead text-muted mx-auto" style="max-width: 750px;">
            Explore comprehensive information on descriptions, causes, risk factors, prevention strategies, and medical guidance across major medical domains.
        </p>
    </div>
</div>

<!-- Search & Category Filters -->
<div class="card-custom p-4 mb-4">
    <form method="GET" action="diseases.php" class="row g-3 align-items-center">
        <div class="col-md-6">
            <div class="input-group">
                <span class="input-group-text bg-card-subtle text-info border"><i class="bi bi-search"></i></span>
                <input type="text" name="search" class="form-control" placeholder="Search disease name, cause, or keyword..." value="<?= sanitize($search) ?>">
            </div>
        </div>
        <div class="col-md-4">
            <select name="category" class="form-select">
                <option value="">All Categories</option>
                <?php foreach ($categories as $cat): ?>
                    <option value="<?= sanitize($cat) ?>" <?= $category === $cat ? 'selected' : '' ?>><?= sanitize($cat) ?></option>
                <?php endforeach; ?>
            </select>
        </div>
        <div class="col-md-2">
            <button type="submit" class="btn btn-primary-custom w-100"><i class="bi bi-filter me-1"></i> Filter</button>
        </div>
    </form>
</div>

<!-- Disease Grid -->
<div class="row g-4">
    <?php if (!empty($diseases)): ?>
        <?php foreach ($diseases as $d): ?>
            <div class="col-md-6 col-lg-4">
                <div class="card-custom p-4 h-100 d-flex flex-column justify-content-between">
                    <div>
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <span class="badge bg-info bg-opacity-20 text-info border border-info border-opacity-25"><?= sanitize($d['category']) ?></span>
                        </div>
                        <h4 class="fw-bold mb-2"><?= sanitize($d['name']) ?></h4>
                        <p class="small text-muted mb-3" style="min-height: 60px;">
                            <?= sanitize(substr($d['short_description'], 0, 110)) ?>...
                        </p>
                    </div>
                    <a href="disease_detail.php?id=<?= $d['id'] ?>" class="btn btn-outline-info rounded-pill btn-sm w-100 mt-2">
                        View Disease Details <i class="bi bi-arrow-right me-1"></i>
                    </a>
                </div>
            </div>
        <?php endforeach; ?>
    <?php else: ?>
        <div class="col-12 text-center py-5">
            <i class="bi bi-search display-3 text-muted"></i>
            <h4 class="fw-bold mt-3">No Diseases Found</h4>
            <p class="text-muted small">Try broadening your search query or choosing "All Categories".</p>
            <a href="diseases.php" class="btn btn-outline-secondary rounded-pill px-4">Reset Filters</a>
        </div>
    <?php endif; ?>
</div>

<?php
require_once __DIR__ . '/includes/footer.php';
?>
