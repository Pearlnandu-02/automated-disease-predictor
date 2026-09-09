<?php
require_once __DIR__ . '/includes/header.php';
?>

<div class="row py-3">
    <div class="col-lg-12 text-center mb-4">
        <span class="badge bg-info text-dark px-3 py-2 rounded-pill fw-bold mb-2">PREVENTATIVE HEALTH</span>
        <h1 class="display-5 fw-extrabold text-white">Health Awareness & Disease Prevention</h1>
        <p class="lead text-muted mx-auto" style="max-width: 750px;">
            Evidence-based lifestyle strategies, preventative screening timelines, and wellness recommendations for reducing chronic disease risk.
        </p>
    </div>
</div>

<div class="row g-4 my-2">
    <div class="col-md-6">
        <div class="card-custom p-4 h-100">
            <h4 class="fw-bold text-white mb-3 d-flex align-items-center">
                <i class="bi bi-heart-pulse text-danger me-2"></i> Cardiovascular & Metabolic Wellness
            </h4>
            <ul class="text-muted small mb-0 lh-lg">
                <li><strong>150 Mins/Week Physical Activity:</strong> Moderate aerobic exercise (brisk walking, cycling) optimizes blood pressure and insulin sensitivity.</li>
                <li><strong>DASH / Mediterranean Diet:</strong> High fiber, whole grains, lean protein, and reduced dietary sodium (<2,300 mg/day).</li>
                <li><strong>Routine Lipid & Glucose Panels:</strong> Annual fasting blood glucose and lipid panel screening starting at age 35+.</li>
                <li><strong>Tobacco Cessation:</strong> Complete avoidance of nicotine and secondhand smoke to prevent arterial plaque accumulation.</li>
            </ul>
        </div>
    </div>

    <div class="col-md-6">
        <div class="card-custom p-4 h-100">
            <h4 class="fw-bold text-white mb-3 d-flex align-items-center">
                <i class="bi bi-lungs text-info me-2"></i> Respiratory & Infectious Hygiene
            </h4>
            <ul class="text-muted small mb-0 lh-lg">
                <li><strong>Annual Vaccination:</strong> Yearly Influenza and COVID-19 booster vaccinations, plus Pneumococcal vaccine for adults 65+.</li>
                <li><strong>Hand Hygiene & Masking:</strong> Frequent hand washing with soap and water for 20 seconds during seasonal virus outbreaks.</li>
                <li><strong>Indoor Air Quality:</strong> Avoid biomass smoke exposure and ensure proper ventilation in enclosed crowded spaces.</li>
                <li><strong>Clean Water & Food Safety:</strong> Drink boiled/filtered water and maintain hygiene to prevent water-borne Typhoid & Dengue.</li>
            </ul>
        </div>
    </div>
</div>

<!-- Emergency Triage Guidance -->
<div class="card-custom p-4 p-md-5 my-4 border-danger">
    <h4 class="fw-bold text-danger mb-3 d-flex align-items-center">
        <i class="bi bi-exclamation-octagon-fill me-2"></i> Red-Flag Warning Signs: When to Seek Immediate Emergency Medical Care
    </h4>
    <div class="row g-3 text-muted small">
        <div class="col-md-4">
            <div class="p-3 bg-dark bg-opacity-50 rounded border border-danger border-opacity-25 h-100">
                <strong class="text-white d-block mb-1">Cardiac Symptoms:</strong> Crushing chest pressure, pain radiating to left arm or jaw, sudden cold sweat.
            </div>
        </div>
        <div class="col-md-4">
            <div class="p-3 bg-dark bg-opacity-50 rounded border border-danger border-opacity-25 h-100">
                <strong class="text-white d-block mb-1">Respiratory Distress:</strong> Inability to speak full sentences, severe shortness of breath, blue lips/fingertips (cyanosis).
            </div>
        </div>
        <div class="col-md-4">
            <div class="p-3 bg-dark bg-opacity-50 rounded border border-danger border-opacity-25 h-100">
                <strong class="text-white d-block mb-1">Neurological Emergencies:</strong> Sudden facial drooping, arm weakness, slurred speech (stroke signs) or prolonged seizure >5 mins.
            </div>
        </div>
    </div>
</div>

<?php
require_once __DIR__ . '/includes/footer.php';
?>
