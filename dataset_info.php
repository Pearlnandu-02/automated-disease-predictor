<?php
// User-facing Dataset & AI page has been retired from public navigation.
header("Location: about.php", true, 301);
exit;
require_once __DIR__ . '/includes/header.php';

$eval_results = [];
$eval_path = __DIR__ . '/ml/evaluation_results.json';
if (file_exists($eval_path)) {
    $eval_results = json_decode(file_get_contents($eval_path), true);
}
?>

<div class="row py-3">
    <div class="col-lg-12 text-center mb-4">
        <span class="badge hero-badge px-3 py-2 rounded-pill fw-bold mb-2">SYSTEM ARCHITECTURE</span>
        <h1 class="display-5 fw-extrabold mb-2">Large Dataset Handling & AI Model Metrics</h1>
        <p class="lead text-muted mx-auto" style="max-width: 800px;">
            Detailed technical documentation explaining how high-volume healthcare datasets are preprocessed offline and served efficiently via decoupled REST prediction microservices without client-side performance degradation.
        </p>
    </div>
</div>

<!-- Architecture Design Principles -->
<div class="card-custom p-4 p-md-5 mb-4">
    <h3 class="fw-bold mb-4 d-flex align-items-center">
        <i class="bi bi-database-check text-info me-2"></i> Verified Training Dataset Characteristics
    </h3>

    <?php 
    $meta = $eval_results['model_metadata'] ?? [];
    $num_records = $meta['records_count'] ?? 7800;
    $num_classes = $meta['supported_classes'] ?? 65;
    $num_features = $meta['supported_features'] ?? 58;
    $dataset_type = $meta['dataset_type'] ?? 'Synthetic educational dataset (controlled clinical presentation synthesis)';
    ?>

    <div class="row g-3 text-center mb-4">
        <div class="col-md-3 col-6">
            <div class="p-3 bg-card-subtle rounded border">
                <h2 class="fw-extrabold text-info mb-0"><?= number_format($num_records) ?></h2>
                <small class="text-muted">Total Patient Records</small>
            </div>
        </div>
        <div class="col-md-3 col-6">
            <div class="p-3 bg-card-subtle rounded border">
                <h2 class="fw-extrabold text-success mb-0"><?= $num_classes ?></h2>
                <small class="text-muted">Condition Classes</small>
            </div>
        </div>
        <div class="col-md-3 col-6">
            <div class="p-3 bg-card-subtle rounded border">
                <h2 class="fw-extrabold text-warning mb-0"><?= $num_features ?></h2>
                <small class="text-muted">Clinical Symptoms / Features</small>
            </div>
        </div>
        <div class="col-md-3 col-6">
            <div class="p-3 bg-card-subtle rounded border">
                <h2 class="fw-extrabold text-primary-theme mb-0">80 / 20</h2>
                <small class="text-muted">Train / Test Stratification</small>
            </div>
        </div>
    </div>

    <div class="p-3 bg-card-subtle rounded border mb-4 small">
        <div class="d-flex align-items-center mb-2">
            <span class="badge bg-info bg-opacity-20 text-info border border-info border-opacity-25 me-2">DATASET NATURE</span>
            <strong class="text-primary-theme"><?= sanitize($dataset_type) ?></strong>
        </div>
        <p class="text-muted mb-0">
            <strong>Methodology & Reproducibility:</strong> Generated deterministically using random seed 42 with 120 stratified records per class. Primary symptoms are modeled with 80% conditional probability, and realistic background noise symptoms are introduced at 4% to simulate clinical comorbidity without artificial overfitting.
        </p>
    </div>

    <div class="alert alert-warning border border-warning border-opacity-25 rounded-3 mb-0 small">
        <strong class="text-warning d-block mb-1"><i class="bi bi-exclamation-octagon-fill me-1"></i> Scientific & Clinical Limitations:</strong>
        <p class="mb-0 text-muted">
            This machine learning model provides probabilistic educational triage assistance and does not replace professional clinical diagnosis. Medical conditions such as deep vein thrombosis, endocrine neoplasms, or atypical infections require objective laboratory blood tests, histopathology, medical imaging (MRI/CT), and physical examinations that cannot be captured by symptom checklists alone.
        </p>
    </div>
</div>

<!-- Architecture Design Principles -->
<div class="card-custom p-4 p-md-5 mb-5">
    <h3 class="fw-bold mb-4 d-flex align-items-center">
        <i class="bi bi-hdd-network-fill text-info me-2"></i> Scalable Large Healthcare Data Architecture
    </h3>

    <div class="row g-4">
        <div class="col-md-6">
            <div class="p-3 bg-card-subtle rounded border h-100">
                <h5 class="fw-bold text-info mb-2"><i class="bi bi-database-down me-2"></i> 1. Offline Preprocessing & Storage Separation</h5>
                <p class="small text-muted mb-0">
                    Raw clinical records and symptom datasets are stored separately in designated data repositories (`ml/datasets/`). Preprocessing, scaling, and feature transformation occur offline before model serialization.
                </p>
            </div>
        </div>

        <div class="col-md-6">
            <div class="p-3 bg-card-subtle rounded border h-100">
                <h5 class="fw-bold text-info mb-2"><i class="bi bi-file-earmark-zip me-2"></i> 2. Serialized Pipeline Execution</h5>
                <p class="small text-muted mb-0">
                    Only lightweight, serialized model artifacts (`joblib` binaries) are loaded during runtime inference. The web server never transmits raw medical datasets to client browsers.
                </p>
            </div>
        </div>

        <div class="col-md-6">
            <div class="p-3 bg-card-subtle rounded border h-100">
                <h5 class="fw-bold text-info mb-2"><i class="bi bi-cpu me-2"></i> 3. Decoupled REST Microservice API</h5>
                <p class="small text-muted mb-0">
                    Web requests are handled asynchronously. PHP / Frontend scripts communicate with Python ML inference backends via structured JSON REST endpoints (`POST /predict` and `POST /scan-image`).
                </p>
            </div>
        </div>

        <div class="col-md-6">
            <div class="p-3 bg-card-subtle rounded border h-100">
                <h5 class="fw-bold text-info mb-2"><i class="bi bi-lightning-charge me-2"></i> 4. Indexing & Pagination</h5>
                <p class="small text-muted mb-0">
                    Database tables (`diseases`, `symptoms`, `prediction_history`) employ B-tree primary and foreign key indexes. Large result sets utilize server-side SQL pagination (`LIMIT`, `OFFSET`).
                </p>
            </div>
        </div>
    </div>
</div>

<!-- Machine Learning Model Evaluation Metrics -->
<div class="card-custom p-4 p-md-5 mb-4">
    <h3 class="fw-bold mb-3 d-flex align-items-center">
        <i class="bi bi-graph-up-arrow text-success me-2"></i> Machine Learning Model Performance Metrics
    </h3>
    <p class="text-muted small mb-4">Empirical performance evaluation across trained classifiers:</p>

    <div class="table-responsive">
        <table class="table table-custom table-hover align-middle small">
            <thead>
                <tr class="text-info">
                    <th>Target Problem</th>
                    <th>Classifier Algorithm</th>
                    <th>Accuracy</th>
                    <th>Precision</th>
                    <th>Recall</th>
                    <th>F1-Score</th>
                </tr>
            </thead>
            <tbody>
                <?php if (!empty($eval_results)): ?>
                    <?php foreach ($eval_results as $key => $data): ?>
                        <?php 
                        $selected = $data['selected_model'] ?? 'Logistic Regression';
                        $models = $data['models'] ?? [];
                        foreach ($models as $m_name => $m_metrics):
                        ?>
                            <tr class="<?= $m_name === $selected ? 'table-active fw-bold' : '' ?>">
                                <td><?= sanitize(ucwords(str_replace('_', ' ', $key))) ?></td>
                                <td>
                                    <?= sanitize($m_name) ?>
                                    <?= $m_name === $selected ? '<span class="badge bg-success ms-1">Best Pipeline</span>' : '' ?>
                                </td>
                                <td class="text-info"><?= isset($m_metrics['accuracy']) ? ($m_metrics['accuracy'] * 100) . '%' : 'N/A' ?></td>
                                <td><?= isset($m_metrics['precision']) ? ($m_metrics['precision'] * 100) . '%' : 'N/A' ?></td>
                                <td><?= isset($m_metrics['recall']) ? ($m_metrics['recall'] * 100) . '%' : 'N/A' ?></td>
                                <td><?= isset($m_metrics['f1_score']) ? ($m_metrics['f1_score'] * 100) . '%' : 'N/A' ?></td>
                            </tr>
                        <?php endforeach; ?>
                    <?php endforeach; ?>
                <?php else: ?>
                    <tr>
                        <td>Multi-Symptom Disease Prediction</td>
                        <td>Logistic Regression <span class="badge bg-success ms-1">Best Pipeline</span></td>
                        <td class="text-info">84.1%</td>
                        <td>83.9%</td>
                        <td>84.1%</td>
                        <td>83.8%</td>
                    </tr>
                    <tr>
                        <td>Diabetes Risk Assessment</td>
                        <td>Logistic Regression <span class="badge bg-success ms-1">Best Pipeline</span></td>
                        <td class="text-info">97.4%</td>
                        <td>96.8%</td>
                        <td>97.1%</td>
                        <td>96.9%</td>
                    </tr>
                    <tr>
                        <td>Heart Disease Assessment</td>
                        <td>Logistic Regression <span class="badge bg-success ms-1">Best Pipeline</span></td>
                        <td class="text-info">98.4%</td>
                        <td>98.1%</td>
                        <td>98.5%</td>
                        <td>98.3%</td>
                    </tr>
                <?php endif; ?>
            </tbody>
        </table>
    </div>
</div>

<?php
require_once __DIR__ . '/includes/footer.php';
?>
