<?php
// history.php - Assessment History (Section 7)
require_once __DIR__ . '/includes/auth.php';
require_once __DIR__ . '/includes/functions.php';

$user = get_logged_in_user();
$is_guest = empty($user);
$user_id = $is_guest ? 0 : $user['id'];
$pdo = get_db_connection();

$records = [];
$has_real_records = false;

if ($pdo && !$is_guest) {
    try {
        // Fetch clinical assessments
        $stmt = $pdo->prepare("SELECT id, 'Clinical Risk Assessment' AS assessment_type, disease AS title, risk_level AS status, probability AS score, created_at, 'clinical' AS category_code FROM health_assessments WHERE user_id = ?");
        $stmt->execute([$user_id]);
        $clinical_records = $stmt->fetchAll();

        // Fetch AI prediction assessments
        $stmt = $pdo->prepare("SELECT id, 'AI Symptom Prediction' AS assessment_type, predicted_disease AS title, 'Completed' AS status, confidence AS score, created_at, 'prediction' AS category_code FROM prediction_history WHERE user_id = ?");
        $stmt->execute([$user_id]);
        $pred_records = $stmt->fetchAll();

        $records = array_merge($clinical_records, $pred_records);
        if (!empty($records)) {
            $has_real_records = true;
            usort($records, function($a, $b) {
                return strtotime($b['created_at']) - strtotime($a['created_at']);
            });
        }
    } catch (PDOException $e) {
        $records = [];
    }
}

// If no real records exist yet, provide clearly marked demonstration entries
if (empty($records)) {
    $records = [
        [
            'id' => 101,
            'assessment_type' => 'Clinical Risk Assessment',
            'title' => 'Cardiovascular Disease Risk Evaluation',
            'status' => 'MODERATE',
            'score' => 42.5,
            'created_at' => date('Y-m-d H:i:s', strtotime('-1 day')),
            'category_code' => 'clinical',
            'is_demo' => true
        ],
        [
            'id' => 102,
            'assessment_type' => 'AI Symptom Prediction',
            'title' => 'Predicted Condition: Type 2 Diabetes',
            'status' => 'HIGH',
            'score' => 84.1,
            'created_at' => date('Y-m-d H:i:s', strtotime('-3 days')),
            'category_code' => 'prediction',
            'is_demo' => true
        ],
        [
            'id' => 103,
            'assessment_type' => 'Health Simulator',
            'title' => 'Systolic Optimization What-If Scenario',
            'status' => 'OPTIMAL',
            'score' => 15.0,
            'created_at' => date('Y-m-d H:i:s', strtotime('-5 days')),
            'category_code' => 'simulator',
            'is_demo' => true
        ],
        [
            'id' => 104,
            'assessment_type' => 'Injury Scanner',
            'title' => 'Visual Skin Screening: Possible Minor Injury',
            'status' => 'SCREENED',
            'score' => null,
            'created_at' => date('Y-m-d H:i:s', strtotime('-7 days')),
            'category_code' => 'scanner',
            'is_demo' => true
        ]
    ];
}

$page_title = 'MediSense AI | Assessment History';
require_once __DIR__ . '/includes/header.php';
?>

<div class="row justify-content-center py-3">
    <div class="col-lg-11 col-xl-10">
        <!-- Hero Header -->
        <div class="card-custom p-4 p-md-5 mb-4 hero-banner">
            <div class="row align-items-center">
                <div class="col-lg-8">
                    <span class="badge hero-badge px-3 py-1 mb-2 fw-bold">Assessment Records</span>
                    <h1 class="display-6 fw-extrabold hero-heading mb-2">Assessment History</h1>
                    <p class="hero-lead mb-3">
                        Review previous AI symptom predictions, clinical risk assessments, health simulator runs, and visual scanner records.
                    </p>
                    <?php if (!$has_real_records): ?>
                        <span class="badge bg-secondary-subtle text-secondary border px-3 py-1 rounded-pill small">
                            <i class="bi bi-info-circle me-1"></i> Displaying demonstration records. Real assessments will be stored here as you use tools.
                        </span>
                    <?php else: ?>
                        <span class="badge bg-success-subtle text-success border px-3 py-1 rounded-pill small">
                            <i class="bi bi-check-circle-fill me-1"></i> Live Database History Active
                        </span>
                    <?php endif; ?>
                </div>
                <div class="col-lg-4 text-center mt-3 mt-lg-0">
                    <div class="p-3 bg-card-subtle rounded-4 border border-secondary border-opacity-25">
                        <small class="text-uppercase fw-bold text-muted d-block">Total Assessments</small>
                        <h2 class="display-5 fw-extrabold text-info mb-0" id="readoutTotalCount"><?= count($records) ?></h2>
                    </div>
                </div>
            </div>
        </div>

        <!-- Filter & Search Toolbar (Section 7) -->
        <div class="card-custom p-4 mb-4">
            <div class="row g-3 align-items-center">
                <div class="col-md-5">
                    <div class="input-group">
                        <span class="input-group-text bg-card-subtle border text-info"><i class="bi bi-search"></i></span>
                        <input type="text" id="filterSearchInput" class="form-control" placeholder="Search by title, condition, or keyword...">
                    </div>
                </div>
                <div class="col-md-4">
                    <select id="filterTypeSelect" class="form-select">
                        <option value="ALL">All Assessment Types</option>
                        <option value="Clinical Risk Assessment">Clinical Risk Assessment</option>
                        <option value="AI Symptom Prediction">AI Symptom Prediction</option>
                        <option value="Health Simulator">Health Simulator</option>
                        <option value="Injury Scanner">Injury Scanner</option>
                    </select>
                </div>
                <div class="col-md-3">
                    <select id="filterDateSelect" class="form-select">
                        <option value="ALL">All Time</option>
                        <option value="7">Last 7 Days</option>
                        <option value="30">Last 30 Days</option>
                        <option value="90">Last 90 Days</option>
                    </select>
                </div>
            </div>
        </div>

        <!-- Assessment Records Table -->
        <div class="card-custom p-4 shadow-sm">
            <div class="table-responsive">
                <table class="table table-hover align-middle mb-0" id="assessmentHistoryTable">
                    <thead class="table-light">
                        <tr>
                            <th>Assessment ID</th>
                            <th>Date & Time</th>
                            <th>Assessment Type</th>
                            <th>Condition / Finding</th>
                            <th>Status / Risk</th>
                            <th class="text-center">Action</th>
                        </tr>
                    </thead>
                    <tbody id="historyTableBody">
                        <?php foreach ($records as $row): 
                            $is_demo = !empty($row['is_demo']);
                            $stat = strtoupper($row['status'] ?? 'COMPLETED');
                            $badge_class = 'bg-secondary';
                            if ($stat === 'HIGH' || $stat === 'ELEVATED') $badge_class = 'bg-danger text-white';
                            elseif ($stat === 'MODERATE') $badge_class = 'bg-warning text-dark';
                            elseif ($stat === 'LOW' || $stat === 'OPTIMAL' || $stat === 'COMPLETED' || $stat === 'SCREENED') $badge_class = 'bg-success text-white';
                        ?>
                            <tr class="history-row" data-type="<?= sanitize($row['assessment_type']) ?>" data-date="<?= $row['created_at'] ?>">
                                <td>
                                    <span class="fw-bold">#HRA-<?= $row['id'] ?></span>
                                    <?php if ($is_demo): ?>
                                        <span class="badge bg-secondary-subtle text-secondary small py-0 px-1 border" style="font-size: 0.65rem;">Demo</span>
                                    <?php endif; ?>
                                </td>
                                <td>
                                    <span class="text-body d-block"><?= date('M d, Y', strtotime($row['created_at'])) ?></span>
                                    <small class="text-muted"><?= date('h:i A', strtotime($row['created_at'])) ?></small>
                                </td>
                                <td>
                                    <span class="badge bg-info bg-opacity-15 text-info border border-info border-opacity-25 rounded-pill px-2 py-1 small">
                                        <?= sanitize($row['assessment_type']) ?>
                                    </span>
                                </td>
                                <td>
                                    <strong class="text-body"><?= sanitize($row['title']) ?></strong>
                                    <?php if ($row['score'] !== null): ?>
                                        <small class="text-muted d-block"><?= number_format($row['score'], 1) ?>% statistical score</small>
                                    <?php endif; ?>
                                </td>
                                <td>
                                    <span class="badge <?= $badge_class ?> px-2 py-1 rounded-pill small">
                                        <?= $stat ?>
                                    </span>
                                </td>
                                <td class="text-center">
                                    <a href="report.php?id=<?= $row['id'] ?>" class="btn btn-sm btn-outline-info rounded-pill px-3">
                                        <i class="bi bi-file-earmark-medical me-1"></i> View Details
                                    </a>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            </div>

            <!-- Empty State (Section 7) -->
            <div id="historyEmptyState" class="text-center py-5 d-none">
                <i class="bi bi-folder2-open display-4 text-muted opacity-50 d-block mb-3"></i>
                <h5 class="fw-bold mb-1">No Matching Assessments Found</h5>
                <p class="text-muted small mb-3">Try adjusting your search query, assessment type filter, or date range.</p>
                <button type="button" class="btn btn-outline-info rounded-pill px-4 btn-sm" id="btnResetFilters">
                    <i class="bi bi-arrow-counterclockwise me-1"></i> Reset Filters
                </button>
            </div>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('filterSearchInput');
    const typeSelect = document.getElementById('filterTypeSelect');
    const dateSelect = document.getElementById('filterDateSelect');
    const rows = document.querySelectorAll('.history-row');
    const emptyState = document.getElementById('historyEmptyState');
    const tableBody = document.getElementById('historyTableBody');
    const totalCount = document.getElementById('readoutTotalCount');
    const btnReset = document.getElementById('btnResetFilters');

    function applyFilters() {
        const query = searchInput.value.toLowerCase().trim();
        const selectedType = typeSelect.value;
        const selectedDateDays = dateSelect.value;
        const now = new Date();

        let visibleCount = 0;

        rows.forEach(row => {
            const text = row.innerText.toLowerCase();
            const rowType = row.getAttribute('data-type');
            const rowDateStr = row.getAttribute('data-date');
            const rowDate = new Date(rowDateStr);

            let matchesSearch = !query || text.includes(query);
            let matchesType = (selectedType === 'ALL') || (rowType === selectedType);
            let matchesDate = true;

            if (selectedDateDays !== 'ALL') {
                const maxAgeDays = parseInt(selectedDateDays);
                const diffTime = Math.abs(now - rowDate);
                const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
                matchesDate = diffDays <= maxAgeDays;
            }

            if (matchesSearch && matchesType && matchesDate) {
                row.style.display = '';
                visibleCount++;
            } else {
                row.style.display = 'none';
            }
        });

        if (totalCount) totalCount.textContent = visibleCount;

        if (visibleCount === 0) {
            emptyState.classList.remove('d-none');
            tableBody.classList.add('d-none');
        } else {
            emptyState.classList.add('d-none');
            tableBody.classList.remove('d-none');
        }
    }

    searchInput.addEventListener('input', applyFilters);
    typeSelect.addEventListener('change', applyFilters);
    dateSelect.addEventListener('change', applyFilters);

    if (btnReset) {
        btnReset.addEventListener('click', function() {
            searchInput.value = '';
            typeSelect.value = 'ALL';
            dateSelect.value = 'ALL';
            applyFilters();
        });
    }
});
</script>

<?php require_once __DIR__ . '/includes/footer.php'; ?>
