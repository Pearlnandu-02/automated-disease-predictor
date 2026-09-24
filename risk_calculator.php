<?php
// risk_calculator.php - Interactive Health Risk Calculator (Section 5)
require_once __DIR__ . '/includes/auth.php';
require_once __DIR__ . '/includes/functions.php';

$page_title = 'MediSense AI | Health Risk Calculator';
require_once __DIR__ . '/includes/header.php';
?>

<div class="row justify-content-center py-3">
    <div class="col-lg-11 col-xl-10">
        <!-- Hero Banner -->
        <div class="card-custom p-4 p-md-5 mb-4 hero-banner">
            <div class="row align-items-center">
                <div class="col-lg-8">
                    <span class="badge hero-badge px-3 py-1 mb-2 fw-bold">Interactive Clinical Tool</span>
                    <h1 class="display-6 fw-extrabold hero-heading mb-2">Health Risk Calculator</h1>
                    <p class="hero-lead mb-3">
                        Evaluate metabolic, cardiovascular, blood pressure, and lifestyle indicators using real-time interactive controls.
                    </p>
                    <div class="d-flex align-items-center gap-2 small text-muted">
                        <i class="bi bi-info-circle-fill text-info"></i>
                        <span>Results represent an <strong>educational risk estimate</strong>, strictly separated from a formal medical diagnosis.</span>
                    </div>
                </div>
                <div class="col-lg-4 text-center mt-3 mt-lg-0">
                    <div class="p-3 bg-card-subtle rounded-4 border border-secondary border-opacity-25">
                        <small class="text-uppercase fw-bold text-muted d-block">Overall Risk Index</small>
                        <h2 class="display-5 fw-extrabold text-info mb-1" id="readoutCompositeScore">--</h2>
                        <span id="readoutCompositeBadge" class="badge bg-secondary rounded-pill px-3 py-1">Adjust Inputs</span>
                    </div>
                </div>
            </div>
        </div>

        <form id="riskCalculatorForm" class="row g-4">
            <!-- 1. BMI Section (Interactive sliders & height/weight) -->
            <div class="col-md-6">
                <div class="card-custom p-4 h-100 border-info-subtle">
                    <div class="d-flex align-items-center justify-content-between mb-3">
                        <h5 class="fw-bold mb-0 d-flex align-items-center text-info">
                            <i class="bi bi-person-standing me-2 fs-4"></i> 1. Body Mass Index (BMI)
                        </h5>
                        <span id="bmiBadge" class="badge bg-success-subtle text-success border border-success-subtle px-3 py-1 rounded-pill">Optimal Weight</span>
                    </div>

                    <div class="mb-4">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <label class="form-label small fw-semibold text-muted mb-0">Height (cm)</label>
                            <span class="badge bg-card-subtle border text-body fw-bold px-2 py-1"><span id="val_height">172</span> cm</span>
                        </div>
                        <input type="range" class="form-range sync-slider" id="sliderHeight" name="height" min="120" max="220" value="172" data-target="val_height">
                        <div class="d-flex justify-content-between text-muted" style="font-size: 0.7rem;">
                            <span>120 cm</span>
                            <span>170 cm</span>
                            <span>220 cm</span>
                        </div>
                    </div>

                    <div class="mb-4">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <label class="form-label small fw-semibold text-muted mb-0">Weight (kg)</label>
                            <span class="badge bg-card-subtle border text-body fw-bold px-2 py-1"><span id="val_weight">68</span> kg</span>
                        </div>
                        <input type="range" class="form-range sync-slider" id="sliderWeight" name="weight" min="35" max="180" value="68" data-target="val_weight">
                        <div class="d-flex justify-content-between text-muted" style="font-size: 0.7rem;">
                            <span>35 kg</span>
                            <span>100 kg</span>
                            <span>180 kg</span>
                        </div>
                    </div>

                    <div class="mb-3">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <label class="form-label small fw-semibold text-muted mb-0">Age (years)</label>
                            <span class="badge bg-card-subtle border text-body fw-bold px-2 py-1"><span id="val_age">35</span> yrs</span>
                        </div>
                        <input type="range" class="form-range sync-slider" id="sliderAge" name="age" min="18" max="95" value="35" data-target="val_age">
                    </div>

                    <div class="p-3 rounded-3 bg-card-subtle border d-flex justify-content-around text-center mt-auto">
                        <div>
                            <small class="text-muted text-uppercase d-block" style="font-size: 0.7rem;">Calculated BMI</small>
                            <h3 class="fw-extrabold text-info mb-0" id="readoutBmiVal">23.0</h3>
                        </div>
                        <div class="border-start border-secondary border-opacity-25 ps-3">
                            <small class="text-muted text-uppercase d-block" style="font-size: 0.7rem;">Ideal Range</small>
                            <span class="fw-bold text-success" id="readoutIdealWeight">54.7 - 73.6 kg</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 2. Diabetes Risk Factors (Tile-based selections) -->
            <div class="col-md-6">
                <div class="card-custom p-4 h-100 border-primary-subtle">
                    <div class="d-flex align-items-center justify-content-between mb-3">
                        <h5 class="fw-bold mb-0 d-flex align-items-center text-primary">
                            <i class="bi bi-droplet-half me-2 fs-4"></i> 2. Diabetes Risk Factors
                        </h5>
                        <span id="diabetesRiskBadge" class="badge bg-success-subtle text-success border border-success-subtle px-3 py-1 rounded-pill">Low Risk</span>
                    </div>

                    <label class="form-label small fw-semibold text-muted mb-2">Fasting Blood Glucose Estimate</label>
                    <div class="d-flex flex-wrap gap-2 mb-3">
                        <button type="button" class="btn btn-sm btn-outline-info rounded-pill px-3 py-2 flex-fill calc-tile-btn active" data-group="glucose" data-val="normal">
                            &lt; 100 mg/dL (Normal)
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-info rounded-pill px-3 py-2 flex-fill calc-tile-btn" data-group="glucose" data-val="impaired">
                            100-125 (Prediabetes)
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-info rounded-pill px-3 py-2 flex-fill calc-tile-btn" data-group="glucose" data-val="high">
                            &ge; 126 mg/dL (High)
                        </button>
                    </div>

                    <label class="form-label small fw-semibold text-muted mb-2">Family History of Diabetes</label>
                    <div class="d-flex flex-wrap gap-2 mb-3">
                        <button type="button" class="btn btn-sm btn-outline-info rounded-pill px-3 py-2 flex-fill calc-tile-btn active" data-group="fam_diabetes" data-val="none">
                            No Family History
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-info rounded-pill px-3 py-2 flex-fill calc-tile-btn" data-group="fam_diabetes" data-val="one_parent">
                            One Parent or Sibling
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-info rounded-pill px-3 py-2 flex-fill calc-tile-btn" data-group="fam_diabetes" data-val="both_parents">
                            Both Parents
                        </button>
                    </div>

                    <div class="mb-3">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <label class="form-label small fw-semibold text-muted mb-0">Waist Circumference (cm)</label>
                            <span class="badge bg-card-subtle border text-body fw-bold px-2 py-1"><span id="val_waist">82</span> cm</span>
                        </div>
                        <input type="range" class="form-range sync-slider" id="sliderWaist" name="waist" min="60" max="150" value="82" data-target="val_waist">
                    </div>
                </div>
            </div>

            <!-- 3. Heart-Health Risk Factors -->
            <div class="col-md-6">
                <div class="card-custom p-4 h-100 border-danger-subtle">
                    <div class="d-flex align-items-center justify-content-between mb-3">
                        <h5 class="fw-bold mb-0 d-flex align-items-center text-danger">
                            <i class="bi bi-heart-pulse-fill me-2 fs-4"></i> 3. Heart-Health Risk Factors
                        </h5>
                        <span id="heartRiskBadge" class="badge bg-success-subtle text-success border border-success-subtle px-3 py-1 rounded-pill">Low Risk</span>
                    </div>

                    <div class="mb-3">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <label class="form-label small fw-semibold text-muted mb-0">Resting Heart Rate (bpm)</label>
                            <span class="badge bg-card-subtle border text-body fw-bold px-2 py-1"><span id="val_pulse">70</span> bpm</span>
                        </div>
                        <input type="range" class="form-range sync-slider" id="sliderPulse" name="pulse" min="45" max="130" value="70" data-target="val_pulse">
                    </div>

                    <label class="form-label small fw-semibold text-muted mb-2">Total Cholesterol Range</label>
                    <div class="d-flex flex-wrap gap-2 mb-3">
                        <button type="button" class="btn btn-sm btn-outline-info rounded-pill px-3 py-2 flex-fill calc-tile-btn active" data-group="cholesterol" data-val="desirable">
                            &lt; 200 mg/dL (Desirable)
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-info rounded-pill px-3 py-2 flex-fill calc-tile-btn" data-group="cholesterol" data-val="borderline">
                            200-239 (Borderline)
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-info rounded-pill px-3 py-2 flex-fill calc-tile-btn" data-group="cholesterol" data-val="high">
                            &ge; 240 mg/dL (Elevated)
                        </button>
                    </div>

                    <label class="form-label small fw-semibold text-muted mb-2">Tobacco / Smoking Exposure</label>
                    <div class="d-flex flex-wrap gap-2 mb-2">
                        <button type="button" class="btn btn-sm btn-outline-info rounded-pill px-3 py-2 flex-fill calc-tile-btn active" data-group="smoking" data-val="never">
                            Never Smoked
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-info rounded-pill px-3 py-2 flex-fill calc-tile-btn" data-group="smoking" data-val="former">
                            Former Smoker (&gt;1 yr)
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-info rounded-pill px-3 py-2 flex-fill calc-tile-btn" data-group="smoking" data-val="current">
                            Current Smoker
                        </button>
                    </div>
                </div>
            </div>

            <!-- 4. Blood-Pressure-Related Risk Factors -->
            <div class="col-md-6">
                <div class="card-custom p-4 h-100 border-warning-subtle">
                    <div class="d-flex align-items-center justify-content-between mb-3">
                        <h5 class="fw-bold mb-0 d-flex align-items-center text-warning">
                            <i class="bi bi-speedometer2 me-2 fs-4"></i> 4. Blood Pressure Factors
                        </h5>
                        <span id="bpCategoryBadge" class="badge bg-success-subtle text-success border border-success-subtle px-3 py-1 rounded-pill">Normal (&lt;120/80)</span>
                    </div>

                    <div class="mb-3">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <label class="form-label small fw-semibold text-muted mb-0">Systolic Blood Pressure (mm Hg)</label>
                            <span class="badge bg-card-subtle border text-body fw-bold px-2 py-1"><span id="val_systolic">118</span> mm Hg</span>
                        </div>
                        <input type="range" class="form-range sync-slider" id="sliderSystolic" name="systolic" min="90" max="200" value="118" data-target="val_systolic">
                    </div>

                    <div class="mb-3">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <label class="form-label small fw-semibold text-muted mb-0">Diastolic Blood Pressure (mm Hg)</label>
                            <span class="badge bg-card-subtle border text-body fw-bold px-2 py-1"><span id="val_diastolic">76</span> mm Hg</span>
                        </div>
                        <input type="range" class="form-range sync-slider" id="sliderDiastolic" name="diastolic" min="55" max="130" value="76" data-target="val_diastolic">
                    </div>

                    <label class="form-label small fw-semibold text-muted mb-2">Dietary Sodium / Salt Pattern</label>
                    <div class="d-flex flex-wrap gap-2 mb-2">
                        <button type="button" class="btn btn-sm btn-outline-info rounded-pill px-3 py-2 flex-fill calc-tile-btn active" data-group="sodium" data-val="low">
                            Low Sodium
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-info rounded-pill px-3 py-2 flex-fill calc-tile-btn" data-group="sodium" data-val="moderate">
                            Moderate / Standard
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-info rounded-pill px-3 py-2 flex-fill calc-tile-btn" data-group="sodium" data-val="high">
                            High Salt / Processed
                        </button>
                    </div>
                </div>
            </div>

            <!-- 5. Lifestyle Factors (Section 5) -->
            <div class="col-12">
                <div class="card-custom p-4 border-success-subtle">
                    <div class="d-flex align-items-center justify-content-between mb-3">
                        <h5 class="fw-bold mb-0 d-flex align-items-center text-success">
                            <i class="bi bi-bicycle me-2 fs-4"></i> 5. Lifestyle & Behavioral Factors
                        </h5>
                        <span id="lifestyleRiskBadge" class="badge bg-success-subtle text-success border border-success-subtle px-3 py-1 rounded-pill">Optimal Habits</span>
                    </div>

                    <div class="row g-4">
                        <div class="col-md-4">
                            <div class="d-flex justify-content-between align-items-center mb-1">
                                <label class="form-label small fw-semibold text-muted mb-0">Sleep Duration (hrs/night)</label>
                                <span class="badge bg-card-subtle border text-body fw-bold px-2 py-1"><span id="val_sleep">7.5</span> hrs</span>
                            </div>
                            <input type="range" class="form-range sync-slider" id="sliderSleep" name="sleep" min="4" max="11" step="0.5" value="7.5" data-target="val_sleep">
                        </div>

                        <div class="col-md-4">
                            <div class="d-flex justify-content-between align-items-center mb-1">
                                <label class="form-label small fw-semibold text-muted mb-0">Daily Water Intake (Liters)</label>
                                <span class="badge bg-card-subtle border text-body fw-bold px-2 py-1"><span id="val_water">2.5</span> L</span>
                            </div>
                            <input type="range" class="form-range sync-slider" id="sliderWater" name="water" min="1" max="5" step="0.25" value="2.5" data-target="val_water">
                        </div>

                        <div class="col-md-4">
                            <div class="d-flex justify-content-between align-items-center mb-1">
                                <label class="form-label small fw-semibold text-muted mb-0">Aerobic Activity (mins/week)</label>
                                <span class="badge bg-card-subtle border text-body fw-bold px-2 py-1"><span id="val_activity">150</span> mins</span>
                            </div>
                            <input type="range" class="form-range sync-slider" id="sliderActivity" name="activity" min="0" max="360" step="15" value="150" data-target="val_activity">
                        </div>

                        <div class="col-md-6">
                            <label class="form-label small fw-semibold text-muted mb-2">Dietary Pattern Quality</label>
                            <div class="d-flex flex-wrap gap-2">
                                <button type="button" class="btn btn-sm btn-outline-info rounded-pill px-3 py-2 flex-fill calc-tile-btn active" data-group="diet" data-val="whole_food">
                                    Whole-Food / Mediterranean
                                </button>
                                <button type="button" class="btn btn-sm btn-outline-info rounded-pill px-3 py-2 flex-fill calc-tile-btn" data-group="diet" data-val="standard">
                                    Balanced Mixed Diet
                                </button>
                                <button type="button" class="btn btn-sm btn-outline-info rounded-pill px-3 py-2 flex-fill calc-tile-btn" data-group="diet" data-val="fast_food">
                                    Frequent Fast Food
                                </button>
                            </div>
                        </div>

                        <div class="col-md-6">
                            <label class="form-label small fw-semibold text-muted mb-2">Chronic Emotional Stress Level</label>
                            <div class="d-flex flex-wrap gap-2">
                                <button type="button" class="btn btn-sm btn-outline-info rounded-pill px-3 py-2 flex-fill calc-tile-btn active" data-group="stress" data-val="low">
                                    Low / Well Managed
                                </button>
                                <button type="button" class="btn btn-sm btn-outline-info rounded-pill px-3 py-2 flex-fill calc-tile-btn" data-group="stress" data-val="moderate">
                                    Moderate Stress
                                </button>
                                <button type="button" class="btn btn-sm btn-outline-info rounded-pill px-3 py-2 flex-fill calc-tile-btn" data-group="stress" data-val="high">
                                    High / Chronic Stress
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Real-Time Educational Assessment Output (Section 5) -->
            <div class="col-12">
                <div class="card-custom p-4 p-md-5 border-info shadow-lg">
                    <div class="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-4 pb-3 border-bottom">
                        <div>
                            <span class="small text-muted fw-bold text-uppercase"><i class="bi bi-clipboard2-pulse text-info me-1"></i> Real-Time Analysis</span>
                            <h3 class="fw-bold mb-0">Educational Health Risk Summary</h3>
                        </div>
                        <div class="d-flex gap-2">
                            <a href="report.php?type=calculator" class="btn btn-outline-info rounded-pill px-4" id="btnDownloadCalcReport">
                                <i class="bi bi-file-earmark-arrow-down me-1"></i> Generate Health Report
                            </a>
                        </div>
                    </div>

                    <div class="row g-4 mb-4">
                        <div class="col-md-4">
                            <div class="p-4 rounded-4 border bg-card-subtle text-center h-100">
                                <small class="text-muted text-uppercase fw-bold">Cardiovascular Domain</small>
                                <h3 class="fw-extrabold mt-2 mb-1" id="scoreCardioText">Low Risk</h3>
                                <div class="progress my-2" style="height: 8px;">
                                    <div class="progress-bar bg-success" id="progressCardio" style="width: 20%;"></div>
                                </div>
                                <span class="small text-muted" id="subCardioText">Based on BP, cholesterol & smoking</span>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="p-4 rounded-4 border bg-card-subtle text-center h-100">
                                <small class="text-muted text-uppercase fw-bold">Metabolic & Diabetes Domain</small>
                                <h3 class="fw-extrabold mt-2 mb-1" id="scoreMetabolicText">Low Risk</h3>
                                <div class="progress my-2" style="height: 8px;">
                                    <div class="progress-bar bg-success" id="progressMetabolic" style="width: 18%;"></div>
                                </div>
                                <span class="small text-muted" id="subMetabolicText">Based on BMI, waist & glucose</span>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="p-4 rounded-4 border bg-card-subtle text-center h-100">
                                <small class="text-muted text-uppercase fw-bold">Lifestyle & Vitality Domain</small>
                                <h3 class="fw-extrabold mt-2 mb-1" id="scoreLifestyleText">Optimal</h3>
                                <div class="progress my-2" style="height: 8px;">
                                    <div class="progress-bar bg-success" id="progressLifestyle" style="width: 15%;"></div>
                                </div>
                                <span class="small text-muted" id="subLifestyleText">Based on exercise, sleep & diet</span>
                            </div>
                        </div>
                    </div>

                    <!-- Actionable Personalized Guidance -->
                    <div class="row g-4">
                        <div class="col-md-6">
                            <div class="p-3 rounded-3 border bg-card-subtle h-100">
                                <h6 class="fw-bold text-success mb-2 d-flex align-items-center">
                                    <i class="bi bi-check-circle-fill me-2"></i> Observed Positive Habits
                                </h6>
                                <ul class="small text-muted ps-3 mb-0" id="listPositiveHabits">
                                    <li>Optimal BMI within normal healthy parameters.</li>
                                    <li>Reported non-smoker with favorable arterial compliance.</li>
                                    <li>Recommended 150+ minutes of weekly aerobic exercise.</li>
                                </ul>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="p-3 rounded-3 border bg-card-subtle h-100">
                                <h6 class="fw-bold text-warning mb-2 d-flex align-items-center">
                                    <i class="bi bi-arrow-up-circle-fill me-2"></i> Opportunities for Preventive Optimization
                                </h6>
                                <ul class="small text-muted ps-3 mb-0" id="listActionableRecommendations">
                                    <li>Maintain consistent sleep schedules to support cellular cortisol recovery.</li>
                                    <li>Monitor annual fasting blood glucose during routine annual physicals.</li>
                                    <li>Incorporate whole plant-based fiber foods to promote arterial endothelial health.</li>
                                </ul>
                            </div>
                        </div>
                    </div>

                    <!-- Medical Disclaimer -->
                    <div class="alert alert-secondary py-2 px-3 small border rounded-3 mt-4 mb-0 text-center" style="font-size: 0.8rem;">
                        <i class="bi bi-shield-exclamation text-warning me-1"></i>
                        <strong>Clinical Disclaimer:</strong> This health risk calculator computes statistical risk projections for preliminary educational purposes only. <strong>It does not provide a medical diagnosis</strong>. Consult a board-certified physician for personalized clinical screenings.
                    </div>
                </div>
            </div>
        </form>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const tileButtons = document.querySelectorAll('.calc-tile-btn');
    const tileValues = {
        glucose: 'normal',
        fam_diabetes: 'none',
        cholesterol: 'desirable',
        smoking: 'never',
        sodium: 'low',
        diet: 'whole_food',
        stress: 'low'
    };

    tileButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const group = this.getAttribute('data-group');
            const val = this.getAttribute('data-val');
            document.querySelectorAll(`.calc-tile-btn[data-group="${group}"]`).forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            tileValues[group] = val;
            computeHealthRisks();
        });
    });

    const sliders = ['sliderHeight', 'sliderWeight', 'sliderAge', 'sliderWaist', 'sliderPulse', 'sliderSystolic', 'sliderDiastolic', 'sliderSleep', 'sliderWater', 'sliderActivity'];
    sliders.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('input', computeHealthRisks);
        }
    });

    function computeHealthRisks() {
        const heightCm = parseFloat(document.getElementById('sliderHeight').value) || 172;
        const weightKg = parseFloat(document.getElementById('sliderWeight').value) || 68;
        const age = parseInt(document.getElementById('sliderAge').value) || 35;
        const waist = parseFloat(document.getElementById('sliderWaist').value) || 82;
        const pulse = parseInt(document.getElementById('sliderPulse').value) || 70;
        const systolic = parseInt(document.getElementById('sliderSystolic').value) || 118;
        const diastolic = parseInt(document.getElementById('sliderDiastolic').value) || 76;
        const sleep = parseFloat(document.getElementById('sliderSleep').value) || 7.5;
        const water = parseFloat(document.getElementById('sliderWater').value) || 2.5;
        const activity = parseInt(document.getElementById('sliderActivity').value) || 150;

        // 1. BMI Calculation
        const heightM = heightCm / 100;
        const bmi = weightKg / (heightM * heightM);
        const bmiReadout = document.getElementById('readoutBmiVal');
        const bmiBadge = document.getElementById('bmiBadge');
        if (bmiReadout) bmiReadout.textContent = bmi.toFixed(1);

        let bmiRiskScore = 0;
        if (bmi < 18.5) {
            if (bmiBadge) { bmiBadge.className = 'badge bg-warning-subtle text-warning border px-3 py-1 rounded-pill'; bmiBadge.textContent = 'Underweight'; }
            bmiRiskScore = 15;
        } else if (bmi < 25) {
            if (bmiBadge) { bmiBadge.className = 'badge bg-success-subtle text-success border px-3 py-1 rounded-pill'; bmiBadge.textContent = 'Optimal Weight'; }
            bmiRiskScore = 0;
        } else if (bmi < 30) {
            if (bmiBadge) { bmiBadge.className = 'badge bg-warning-subtle text-warning border px-3 py-1 rounded-pill'; bmiBadge.textContent = 'Overweight'; }
            bmiRiskScore = 25;
        } else {
            if (bmiBadge) { bmiBadge.className = 'badge bg-danger-subtle text-danger border px-3 py-1 rounded-pill'; bmiBadge.textContent = 'Obese Range'; }
            bmiRiskScore = 50;
        }

        // Ideal weight range
        const minIdeal = (18.5 * heightM * heightM).toFixed(1);
        const maxIdeal = (24.9 * heightM * heightM).toFixed(1);
        const idealElem = document.getElementById('readoutIdealWeight');
        if (idealElem) idealElem.textContent = `${minIdeal} - ${maxIdeal} kg`;

        // 2. Diabetes Risk
        let diabetesScore = 0;
        if (tileValues.glucose === 'impaired') diabetesScore += 30;
        if (tileValues.glucose === 'high') diabetesScore += 65;
        if (tileValues.fam_diabetes === 'one_parent') diabetesScore += 20;
        if (tileValues.fam_diabetes === 'both_parents') diabetesScore += 40;
        if (waist > 94) diabetesScore += 20;
        diabetesScore += (bmiRiskScore * 0.5);

        const diabetesBadge = document.getElementById('diabetesRiskBadge');
        if (diabetesScore > 50) {
            if (diabetesBadge) { diabetesBadge.className = 'badge bg-danger-subtle text-danger border px-3 py-1 rounded-pill'; diabetesBadge.textContent = 'Elevated Risk'; }
        } else if (diabetesScore > 25) {
            if (diabetesBadge) { diabetesBadge.className = 'badge bg-warning-subtle text-warning border px-3 py-1 rounded-pill'; diabetesBadge.textContent = 'Moderate Watch'; }
        } else {
            if (diabetesBadge) { diabetesBadge.className = 'badge bg-success-subtle text-success border px-3 py-1 rounded-pill'; diabetesBadge.textContent = 'Low Risk'; }
        }

        // 3. Blood Pressure
        let bpScore = 0;
        const bpBadge = document.getElementById('bpCategoryBadge');
        if (systolic >= 140 || diastolic >= 90) {
            if (bpBadge) { bpBadge.className = 'badge bg-danger-subtle text-danger border px-3 py-1 rounded-pill'; bpBadge.textContent = 'Stage 2 Hypertension'; }
            bpScore = 55;
        } else if (systolic >= 130 || diastolic >= 80) {
            if (bpBadge) { bpBadge.className = 'badge bg-warning-subtle text-warning border px-3 py-1 rounded-pill'; bpBadge.textContent = 'Stage 1 Hypertension'; }
            bpScore = 35;
        } else if (systolic >= 120 && diastolic < 80) {
            if (bpBadge) { bpBadge.className = 'badge bg-warning-subtle text-warning border px-3 py-1 rounded-pill'; bpBadge.textContent = 'Elevated BP (120-129)'; }
            bpScore = 15;
        } else {
            if (bpBadge) { bpBadge.className = 'badge bg-success-subtle text-success border px-3 py-1 rounded-pill'; bpBadge.textContent = 'Normal (<120/80)'; }
            bpScore = 0;
        }
        if (tileValues.sodium === 'high') bpScore += 15;

        // 4. Heart Health
        let heartScore = bpScore * 0.4;
        if (tileValues.cholesterol === 'borderline') heartScore += 20;
        if (tileValues.cholesterol === 'high') heartScore += 45;
        if (tileValues.smoking === 'current') heartScore += 40;
        if (tileValues.smoking === 'former') heartScore += 15;
        if (pulse > 90) heartScore += 15;

        const heartBadge = document.getElementById('heartRiskBadge');
        if (heartScore > 45) {
            if (heartBadge) { heartBadge.className = 'badge bg-danger-subtle text-danger border px-3 py-1 rounded-pill'; heartBadge.textContent = 'Elevated Risk'; }
        } else if (heartScore > 20) {
            if (heartBadge) { heartBadge.className = 'badge bg-warning-subtle text-warning border px-3 py-1 rounded-pill'; heartBadge.textContent = 'Moderate Watch'; }
        } else {
            if (heartBadge) { heartBadge.className = 'badge bg-success-subtle text-success border px-3 py-1 rounded-pill'; heartBadge.textContent = 'Low Risk'; }
        }

        // 5. Lifestyle Score
        let lifestyleScore = 0;
        if (activity < 60) lifestyleScore += 30;
        else if (activity < 150) lifestyleScore += 15;
        if (sleep < 6 || sleep > 9.5) lifestyleScore += 20;
        if (water < 1.5) lifestyleScore += 15;
        if (tileValues.diet === 'fast_food') lifestyleScore += 30;
        if (tileValues.stress === 'high') lifestyleScore += 25;

        // Summary Calculations
        const cardioPct = Math.min(100, Math.round(heartScore));
        const metabolicPct = Math.min(100, Math.round(diabetesScore));
        const lifestylePct = Math.min(100, Math.round(lifestyleScore));
        const compositeScore = Math.round((cardioPct * 0.4) + (metabolicPct * 0.35) + (lifestylePct * 0.25));

        // Update Summary Card
        const readoutScore = document.getElementById('readoutCompositeScore');
        const readoutBadge = document.getElementById('readoutCompositeBadge');
        if (readoutScore) readoutScore.textContent = compositeScore + '/100';

        if (compositeScore < 25) {
            if (readoutBadge) { readoutBadge.className = 'badge bg-success rounded-pill px-3 py-1'; readoutBadge.textContent = 'Optimal Health Index'; }
        } else if (compositeScore < 50) {
            if (readoutBadge) { readoutBadge.className = 'badge bg-info text-dark rounded-pill px-3 py-1'; readoutBadge.textContent = 'Mild Risk Profile'; }
        } else if (compositeScore < 70) {
            if (readoutBadge) { readoutBadge.className = 'badge bg-warning text-dark rounded-pill px-3 py-1'; readoutBadge.textContent = 'Moderate Risk'; }
        } else {
            if (readoutBadge) { readoutBadge.className = 'badge bg-danger rounded-pill px-3 py-1'; readoutBadge.textContent = 'Elevated Clinical Risk'; }
        }

        // Update progress bars & text
        updateMeter('progressCardio', 'scoreCardioText', cardioPct);
        updateMeter('progressMetabolic', 'scoreMetabolicText', metabolicPct);
        updateMeter('progressLifestyle', 'scoreLifestyleText', lifestylePct);

        // Update Positive Habits & Opportunities
        updateRecommendations(bmi, systolic, activity, tileValues);
    }

    function updateMeter(barId, textId, pct) {
        const bar = document.getElementById(barId);
        const txt = document.getElementById(textId);
        if (!bar || !txt) return;

        bar.style.width = pct + '%';
        if (pct < 25) {
            bar.className = 'progress-bar bg-success';
            txt.className = 'fw-extrabold mt-2 mb-1 text-success';
            txt.textContent = 'Low Risk (' + pct + '%)';
        } else if (pct < 55) {
            bar.className = 'progress-bar bg-warning';
            txt.className = 'fw-extrabold mt-2 mb-1 text-warning';
            txt.textContent = 'Moderate (' + pct + '%)';
        } else {
            bar.className = 'progress-bar bg-danger';
            txt.className = 'fw-extrabold mt-2 mb-1 text-danger';
            txt.textContent = 'Elevated (' + pct + '%)';
        }
    }

    function updateRecommendations(bmi, systolic, activity, tiles) {
        const posList = document.getElementById('listPositiveHabits');
        const recList = document.getElementById('listActionableRecommendations');
        if (!posList || !recList) return;

        const positives = [];
        const recs = [];

        if (bmi >= 18.5 && bmi < 25) positives.push('BMI is in the healthy optimal range, lowering pressure on joints and vascular beds.');
        else if (bmi >= 25) recs.push('Gradual 5-7% weight reduction significantly improves insulin sensitivity and blood pressure.');

        if (systolic < 120) positives.push('Resting systolic blood pressure is in the optimal range (<120 mm Hg).');
        else recs.push('Adopt the dietary DASH eating plan (rich in potassium and magnesium) to support arterial relaxation.');

        if (activity >= 150) positives.push('Meets or exceeds 150 minutes of weekly moderate aerobic conditioning.');
        else recs.push('Aim for at least 30 minutes of brisk walking 5 days a week to support cardiovascular stamina.');

        if (tiles.smoking === 'never') positives.push('Non-smoking status preserves microvascular health and prevents arterial stiffening.');
        else if (tiles.smoking === 'current') recs.push('Smoking cessation provides rapid cardiovascular recovery within weeks of discontinuation.');

        if (tiles.diet === 'whole_food') positives.push('Nutrient-dense whole-food dietary pattern provides antioxidant anti-inflammatory protection.');
        else recs.push('Increase daily soluble fiber intake from oats, legumes, and cruciferous vegetables to optimize lipid absorption.');

        posList.innerHTML = positives.slice(0, 3).map(p => `<li>${p}</li>`).join('');
        recList.innerHTML = recs.slice(0, 3).map(r => `<li>${r}</li>`).join('');
    }

    computeHealthRisks();
});
</script>

<?php require_once __DIR__ . '/includes/footer.php'; ?>
