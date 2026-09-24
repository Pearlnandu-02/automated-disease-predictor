<?php
// diseases.php - Comprehensive Disease Library (Section 9)
$page_title = 'MediSense AI | Disease Library';
require_once __DIR__ . '/includes/header.php';
require_once __DIR__ . '/includes/functions.php';

$pdo = get_db_connection();

$search = isset($_GET['search']) ? trim($_GET['search']) : '';
$category = isset($_GET['category']) ? trim($_GET['category']) : '';

$diseases = [];
$categories = [];

// Curated requested category mapping
$requested_categories = [
    'General Health' => ['Fever', 'Common Cold', 'Influenza', 'Dehydration', 'Fatigue'],
    'Respiratory' => ['Asthma', 'Bronchitis', 'Pneumonia', 'COPD', 'Sinusitis'],
    'Cardiovascular' => ['Hypertension', 'Coronary Artery Disease', 'Heart Failure', 'Arrhythmia', 'Angina Pectoris'],
    'Metabolic' => ['Diabetes', 'Hypothyroidism', 'Hyperthyroidism', 'Obesity', 'Prediabetes'],
    'Digestive' => ['Gastritis', 'GERD (Acid Reflux)', 'Gastroenteritis', 'Irritable Bowel Syndrome (IBS)', 'Peptic Ulcer Disease'],
    'Neurological' => ['Migraine', 'Epilepsy', "Parkinson's Disease", 'Stroke', 'Tension Headache'],
    'Skin' => ['Acne Vulgaris', 'Eczema (Atopic Dermatitis)', 'Psoriasis', 'Contact Dermatitis', 'Melanoma', 'Basal Cell Carcinoma', 'Actinic Keratosis']
];

if ($pdo) {
    try {
        $cat_stmt = $pdo->query("SELECT DISTINCT category FROM diseases ORDER BY category ASC");
        $categories = $cat_stmt->fetchAll(PDO::FETCH_COLUMN);

        $sql = "SELECT * FROM diseases WHERE 1=1";
        $params = [];

        if ($search !== '') {
            $sql .= " AND (name LIKE ? OR short_description LIKE ? OR causes LIKE ? OR category LIKE ?)";
            $params[] = "%$search%";
            $params[] = "%$search%";
            $params[] = "%$search%";
            $params[] = "%$search%";
        }

        if ($category !== '') {
            if ($category === 'Metabolic') {
                $sql .= " AND (category = 'Endocrine' OR category = 'Metabolic')";
            } elseif ($category === 'Digestive') {
                $sql .= " AND (category = 'Gastrointestinal' OR category = 'Digestive')";
            } elseif ($category === 'Skin') {
                $sql .= " AND (category = 'Dermatological' OR category = 'Skin')";
            } else {
                $sql .= " AND category LIKE ?";
                $params[] = "%$category%";
            }
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
        <span class="badge hero-badge px-3 py-2 rounded-pill fw-bold mb-2">CLINICAL REFERENCE LIBRARY</span>
        <h1 class="display-5 fw-extrabold mb-2">Disease Library (<?= count($diseases) ?> Supported Conditions)</h1>
        <p class="lead text-muted mx-auto" style="max-width: 800px;">
            Explore evidence-based clinical descriptions, causes, risk factors, prevention strategies, and medical warning signs organized across major health domains.
        </p>
    </div>
</div>

<!-- Category Filter Pills (Section 9) -->
<div class="d-flex flex-wrap justify-content-center gap-2 mb-4">
    <a href="diseases.php" class="btn btn-sm rounded-pill px-3 py-2 <?= empty($category) && empty($search) ? 'btn-info text-white' : 'btn-outline-secondary' ?>">
        All Conditions
    </a>
    <a href="diseases.php?category=General%20Health" class="btn btn-sm rounded-pill px-3 py-2 <?= $category === 'General Health' ? 'btn-info text-white' : 'btn-outline-secondary' ?>">
        <i class="bi bi-heart-pulse me-1"></i> General Health
    </a>
    <a href="diseases.php?category=Respiratory" class="btn btn-sm rounded-pill px-3 py-2 <?= $category === 'Respiratory' ? 'btn-info text-white' : 'btn-outline-secondary' ?>">
        <i class="bi bi-lungs me-1"></i> Respiratory
    </a>
    <a href="diseases.php?category=Cardiovascular" class="btn btn-sm rounded-pill px-3 py-2 <?= $category === 'Cardiovascular' ? 'btn-info text-white' : 'btn-outline-secondary' ?>">
        <i class="bi bi-heart me-1"></i> Cardiovascular
    </a>
    <a href="diseases.php?category=Metabolic" class="btn btn-sm rounded-pill px-3 py-2 <?= $category === 'Metabolic' ? 'btn-info text-white' : 'btn-outline-secondary' ?>">
        <i class="bi bi-droplet-half me-1"></i> Metabolic
    </a>
    <a href="diseases.php?category=Digestive" class="btn btn-sm rounded-pill px-3 py-2 <?= $category === 'Digestive' ? 'btn-info text-white' : 'btn-outline-secondary' ?>">
        <i class="bi bi-shield-check me-1"></i> Digestive
    </a>
    <a href="diseases.php?category=Neurological" class="btn btn-sm rounded-pill px-3 py-2 <?= $category === 'Neurological' ? 'btn-info text-white' : 'btn-outline-secondary' ?>">
        <i class="bi bi-lightning-charge me-1"></i> Neurological
    </a>
    <a href="diseases.php?category=Skin" class="btn btn-sm rounded-pill px-3 py-2 <?= $category === 'Skin' ? 'btn-info text-white' : 'btn-outline-secondary' ?>">
        <i class="bi bi-app-indicator me-1"></i> Skin
    </a>
</div>

<!-- Search & Category Filters Form -->
<div class="card-custom p-4 mb-4">
    <form method="GET" action="diseases.php" class="row g-3 align-items-center">
        <div class="col-md-7">
            <div class="input-group">
                <span class="input-group-text bg-card-subtle text-info border"><i class="bi bi-search"></i></span>
                <input type="text" name="search" class="form-control" placeholder="Search disease name, cause, or medical keyword..." value="<?= sanitize($search) ?>">
            </div>
        </div>
        <div class="col-md-3">
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
<div class="row g-4 mb-5">
    <?php if (!empty($diseases)): ?>
        <?php foreach ($diseases as $d): ?>
            <div class="col-md-6 col-lg-4">
                <div class="card-custom p-4 h-100 d-flex flex-column justify-content-between hover-lift">
                    <div>
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <span class="badge bg-info bg-opacity-15 text-info border border-info border-opacity-25 rounded-pill px-3 py-1 small">
                                <?= sanitize($d['category']) ?>
                            </span>
                        </div>
                        <h4 class="fw-bold mb-2 text-body"><?= sanitize($d['name']) ?></h4>
                        <p class="small text-muted mb-3" style="min-height: 60px;">
                            <?= sanitize(substr($d['short_description'], 0, 120)) ?>...
                        </p>
                    </div>
                    <div class="pt-2 border-top">
                        <a href="disease_detail.php?id=<?= $d['id'] ?>" class="btn btn-outline-info rounded-pill btn-sm w-100">
                            View Clinical Details <i class="bi bi-arrow-right ms-1"></i>
                        </a>
                    </div>
                </div>
            </div>
        <?php endforeach; ?>
    <?php else: ?>
        <div class="col-12 text-center py-5">
            <div class="p-4 bg-card-subtle rounded-4 border border-secondary border-opacity-25 d-inline-block" style="max-width: 480px;">
                <i class="bi bi-journal-x fs-1 text-muted opacity-50 d-block mb-2"></i>
                <h4 class="fw-bold mb-1">No Matching Conditions Found</h4>
                <p class="text-muted small mb-3">No disease records matched your search query or filter selection.</p>
                <a href="diseases.php" class="btn btn-primary-custom rounded-pill btn-sm px-4">View All Conditions</a>
            </div>
        </div>
    <?php endif; ?>
</div>

<!-- Medical Notice -->
<div class="alert alert-secondary py-3 px-4 rounded-3 border text-center small">
    <i class="bi bi-shield-exclamation text-warning me-1"></i>
    <strong>Medical Literacy Notice:</strong> The MediSense AI Disease Library is provided strictly for educational reference and general health literacy. <strong>It does not confirm or substitute for a formal clinical diagnosis.</strong> For personal diagnosis, laboratory work, or medical management, consult a board-certified physician.
</div>

<?php require_once __DIR__ . '/includes/footer.php'; ?>
