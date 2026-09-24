<?php
require_once __DIR__ . '/includes/functions.php';
$page_title = 'MediSense AI | Emergency & Red-Flag Clinical Guide';
require_once __DIR__ . '/includes/header.php';
?>

<div class="container py-4">
    <!-- Breadcrumb -->
    <nav aria-label="breadcrumb" class="mb-3">
        <ol class="breadcrumb">
            <li class="breadcrumb-item"><a href="index.php" class="text-decoration-none text-info">Home</a></li>
            <li class="breadcrumb-item"><a href="diseases.php" class="text-decoration-none text-info">Health Library</a></li>
            <li class="breadcrumb-item active text-danger" aria-current="page">Emergency & Red-Flag Guide</li>
        </ol>
    </nav>

    <!-- CRITICAL EMERGENCY WARNING BANNER -->
    <div class="card border-danger border-2 shadow-lg mb-5 overflow-hidden" style="background: linear-gradient(135deg, rgba(220, 53, 69, 0.12), rgba(220, 53, 69, 0.04));">
        <div class="card-body p-4 p-md-5">
            <div class="row align-items-center">
                <div class="col-lg-8">
                    <div class="d-inline-flex align-items-center gap-2 px-3 py-1 rounded-pill bg-danger text-white fw-bold small mb-3">
                        <i class="bi bi-exclamation-triangle-fill"></i> CRITICAL MEDICAL ADVISORY
                    </div>
                    <h1 class="display-6 fw-extrabold text-danger mb-2">Are You Experiencing a Medical Emergency?</h1>
                    <p class="lead fw-semibold mb-3" style="color: var(--text-primary);">
                        Do NOT use MediSense AI, chat assistants, or digital symptom checkers if you are facing acute trauma or life-threatening symptoms. Call emergency medical dispatch immediately.
                    </p>
                    <div class="d-flex flex-wrap gap-3 align-items-center">
                        <a href="tel:911" class="btn btn-danger btn-lg px-4 py-3 rounded-pill fw-bold shadow">
                            <i class="bi bi-telephone-fill me-2"></i> Call 911 (US / Canada)
                        </a>
                        <a href="tel:112" class="btn btn-outline-danger btn-lg px-4 py-3 rounded-pill fw-bold">
                            <i class="bi bi-globe me-2"></i> Call 112 (EU / India / Global)
                        </a>
                        <a href="tel:999" class="btn btn-outline-secondary btn-lg px-3 py-3 rounded-pill fw-semibold">
                            Call 999 (UK)
                        </a>
                    </div>
                </div>
                <div class="col-lg-4 text-center mt-4 mt-lg-0">
                    <div class="p-4 rounded-4 border border-danger border-opacity-25 bg-card">
                        <div class="text-danger display-3 mb-2"><i class="bi bi-shield-slash-fill"></i></div>
                        <h5 class="fw-bold mb-1">Zero Emergency Delay</h5>
                        <p class="small text-muted mb-0">
                            Minutes matter during myocardial infarction, acute stroke, and respiratory arrest. Never delay dispatch for online symptom research.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Quick Emergency Directory & Poison Control -->
    <div class="row g-4 mb-5">
        <div class="col-md-4">
            <div class="card-custom p-4 h-100 border-start border-4 border-danger">
                <div class="d-flex align-items-center gap-3 mb-2">
                    <i class="bi bi-telephone-inbound-fill fs-2 text-danger"></i>
                    <div>
                        <h6 class="fw-bold mb-0">Poison Control Center</h6>
                        <span class="text-muted small">24/7 National Hotline</span>
                    </div>
                </div>
                <p class="small text-muted mb-3">Accidental ingestion of toxins, household chemicals, medication overdose, or snake/insect bites.</p>
                <a href="tel:18002221222" class="btn btn-sm btn-outline-danger rounded-pill w-100 fw-bold">
                    <i class="bi bi-telephone me-1"></i> 1-800-222-1222 (US)
                </a>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card-custom p-4 h-100 border-start border-4 border-primary">
                <div class="d-flex align-items-center gap-3 mb-2">
                    <i class="bi bi-heart-pulse-fill fs-2 text-primary"></i>
                    <div>
                        <h6 class="fw-bold mb-0">Suicide & Crisis Lifeline</h6>
                        <span class="text-muted small">Free, Confidential Support</span>
                    </div>
                </div>
                <p class="small text-muted mb-3">If you or someone you know is in acute emotional distress, experiencing self-harm urges, or in crisis.</p>
                <a href="tel:988" class="btn btn-sm btn-outline-primary rounded-pill w-100 fw-bold">
                    <i class="bi bi-chat-heart me-1"></i> Call or Text 988
                </a>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card-custom p-4 h-100 border-start border-4 border-warning">
                <div class="d-flex align-items-center gap-3 mb-2">
                    <i class="bi bi-geo-alt-fill fs-2 text-warning"></i>
                    <div>
                        <h6 class="fw-bold mb-0">Nearest Emergency Room</h6>
                        <span class="text-muted small">Facility Locator</span>
                    </div>
                </div>
                <p class="small text-muted mb-3">Locate the closest verified 24/7 Level 1-4 trauma center or emergency department in your vicinity.</p>
                <a href="https://www.google.com/maps/search/nearest+emergency+room" target="_blank" rel="noopener noreferrer" class="btn btn-sm btn-outline-warning rounded-pill w-100 fw-bold">
                    <i class="bi bi-compass me-1"></i> Locate Emergency Rooms
                </a>
            </div>
        </div>
    </div>

    <!-- 8 CRITICAL RED-FLAG CONDITIONS -->
    <div class="mb-4">
        <h2 class="fw-bold mb-1"><i class="bi bi-exclamation-octagon-fill text-danger me-2"></i> 8 Critical Red-Flag Clinical Presentations</h2>
        <p class="text-muted">The following symptom clusters represent clinical emergencies requiring instantaneous dispatch of Advanced Life Support (ALS) ambulances:</p>
    </div>

    <div class="row g-4 mb-5">
        <!-- 1. Chest Pain & Cardiac -->
        <div class="col-lg-6">
            <div class="card-custom p-4 h-100">
                <div class="d-flex justify-content-between align-items-start mb-3">
                    <div class="d-flex align-items-center gap-3">
                        <div class="p-3 bg-danger bg-opacity-10 text-danger rounded-3 fs-3">
                            <i class="bi bi-heart-pulse"></i>
                        </div>
                        <div>
                            <h5 class="fw-bold mb-0">Severe Chest Pain & Cardiac Arrest Signs</h5>
                            <span class="badge bg-danger text-white small">Acute Coronary Syndrome</span>
                        </div>
                    </div>
                </div>
                <div class="mb-3">
                    <h6 class="fw-bold small text-danger"><i class="bi bi-exclamation-circle me-1"></i> Warning Presentation:</h6>
                    <ul class="text-muted small ps-3 mb-0">
                        <li>Crushing central chest heaviness, tightness, or pressure (feels like an elephant on the chest).</li>
                        <li>Pain radiating to the left shoulder, left arm, neck, jaw, or upper back.</li>
                        <li>Accompanied by cold sweating (diaphoresis), nausea, dizziness, or profound shortness of breath.</li>
                        <li><em>In women & diabetics:</em> May present atypically as profound sudden fatigue, epigastric nausea, or shortness of breath without dramatic chest pain.</li>
                    </ul>
                </div>
                <div class="p-3 bg-card-subtle rounded-3 border">
                    <strong class="text-danger small"><i class="bi bi-check2-circle me-1"></i> Immediate Action:</strong>
                    <p class="small text-muted mb-0">Call 911 immediately. Have patient sit upright at rest. If advised by the emergency operator and not allergic, chew 325 mg of non-enteric coated aspirin.</p>
                </div>
            </div>
        </div>

        <!-- 2. Acute Stroke (BE-FAST) -->
        <div class="col-lg-6">
            <div class="card-custom p-4 h-100">
                <div class="d-flex justify-content-between align-items-start mb-3">
                    <div class="d-flex align-items-center gap-3">
                        <div class="p-3 bg-danger bg-opacity-10 text-danger rounded-3 fs-3">
                            <i class="bi bi-activity"></i>
                        </div>
                        <div>
                            <h5 class="fw-bold mb-0">Acute Stroke (BE-FAST Protocol)</h5>
                            <span class="badge bg-danger text-white small">Cerebrovascular Accident</span>
                        </div>
                    </div>
                </div>
                <div class="mb-3">
                    <h6 class="fw-bold small text-danger"><i class="bi bi-exclamation-circle me-1"></i> Warning Presentation:</h6>
                    <ul class="text-muted small ps-3 mb-0">
                        <li><strong>B (Balance):</strong> Sudden loss of balance, vertigo, or coordination.</li>
                        <li><strong>E (Eyes):</strong> Sudden loss of vision, blurriness, or double vision in one or both eyes.</li>
                        <li><strong>F (Face):</strong> Facial droop or asymmetry when attempting to smile.</li>
                        <li><strong>A (Arms):</strong> Arm weakness or downward drift when raising both arms.</li>
                        <li><strong>S (Speech):</strong> Slurred speech, inability to repeat simple phrases, or garbled words.</li>
                        <li><strong>T (Time):</strong> Note the exact time symptoms started; call 911 immediately.</li>
                    </ul>
                </div>
                <div class="p-3 bg-card-subtle rounded-3 border">
                    <strong class="text-danger small"><i class="bi bi-check2-circle me-1"></i> Immediate Action:</strong>
                    <p class="small text-muted mb-0">Time is brain tissue (2 million neurons lost per minute). Do NOT allow patient to sleep or drive themselves. Note last known well time for thrombolytic window (tPA).</p>
                </div>
            </div>
        </div>

        <!-- 3. Severe Respiratory Distress -->
        <div class="col-lg-6">
            <div class="card-custom p-4 h-100">
                <div class="d-flex justify-content-between align-items-start mb-3">
                    <div class="d-flex align-items-center gap-3">
                        <div class="p-3 bg-danger bg-opacity-10 text-danger rounded-3 fs-3">
                            <i class="bi bi-wind"></i>
                        </div>
                        <div>
                            <h5 class="fw-bold mb-0">Severe Respiratory Distress / Airway Obstruction</h5>
                            <span class="badge bg-danger text-white small">Respiratory Failure</span>
                        </div>
                    </div>
                </div>
                <div class="mb-3">
                    <h6 class="fw-bold small text-danger"><i class="bi bi-exclamation-circle me-1"></i> Warning Presentation:</h6>
                    <ul class="text-muted small ps-3 mb-0">
                        <li>Inability to speak in full sentences or gasping for air between individual words.</li>
                        <li>Cyanosis: Bluish or grayish discoloration of the lips, tongue, nail beds, or oral mucosa.</li>
                        <li>Intercostal and suprasternal retractions (skin sucking in around ribs and neck during inhalation).</li>
                        <li>High-pitched inspiratory whistling (stridor) indicating upper airway obstruction.</li>
                    </ul>
                </div>
                <div class="p-3 bg-card-subtle rounded-3 border">
                    <strong class="text-danger small"><i class="bi bi-check2-circle me-1"></i> Immediate Action:</strong>
                    <p class="small text-muted mb-0">Keep patient seated upright; loosen tight clothing. Administer rescue bronchodilator (albuterol) if known asthmatic. Call 911 immediately.</p>
                </div>
            </div>
        </div>

        <!-- 4. Loss of Consciousness & Coma -->
        <div class="col-lg-6">
            <div class="card-custom p-4 h-100">
                <div class="d-flex justify-content-between align-items-start mb-3">
                    <div class="d-flex align-items-center gap-3">
                        <div class="p-3 bg-danger bg-opacity-10 text-danger rounded-3 fs-3">
                            <i class="bi bi-person-x"></i>
                        </div>
                        <div>
                            <h5 class="fw-bold mb-0">Loss of Consciousness & Severe Syncope</h5>
                            <span class="badge bg-danger text-white small">Neurological / Circulatory Collapse</span>
                        </div>
                    </div>
                </div>
                <div class="mb-3">
                    <h6 class="fw-bold small text-danger"><i class="bi bi-exclamation-circle me-1"></i> Warning Presentation:</h6>
                    <ul class="text-muted small ps-3 mb-0">
                        <li>Fainting, collapse, or unresponsiveness lasting longer than a few seconds.</li>
                        <li>Inability to awaken a sleeping individual or sudden profound confusion / delirium.</li>
                        <li>Convulsive active tonic-clonic seizures lasting &gt; 5 minutes (status epilepticus) or repeated back-to-back seizures.</li>
                        <li>Loss of bowel or bladder control accompanying collapse.</li>
                    </ul>
                </div>
                <div class="p-3 bg-card-subtle rounded-3 border">
                    <strong class="text-danger small"><i class="bi bi-check2-circle me-1"></i> Immediate Action:</strong>
                    <p class="small text-muted mb-0">Check breathing and pulse. If breathing, place in lateral recovery position to protect airway. If no pulse/breathing, begin chest compressions immediately.</p>
                </div>
            </div>
        </div>

        <!-- 5. Anaphylaxis -->
        <div class="col-lg-6">
            <div class="card-custom p-4 h-100">
                <div class="d-flex justify-content-between align-items-start mb-3">
                    <div class="d-flex align-items-center gap-3">
                        <div class="p-3 bg-danger bg-opacity-10 text-danger rounded-3 fs-3">
                            <i class="bi bi-shield-x"></i>
                        </div>
                        <div>
                            <h5 class="fw-bold mb-0">Anaphylaxis (Systemic Allergic Shock)</h5>
                            <span class="badge bg-danger text-white small">Immune Shock</span>
                        </div>
                    </div>
                </div>
                <div class="mb-3">
                    <h6 class="fw-bold small text-danger"><i class="bi bi-exclamation-circle me-1"></i> Warning Presentation:</h6>
                    <ul class="text-muted small ps-3 mb-0">
                        <li>Rapidly progressive swelling of the lips, tongue, uvula, soft palate, or throat tightness.</li>
                        <li>Widespread urticaria (hives), flushing, and intense cutaneous pruritus.</li>
                        <li>Severe wheezing, stridor, and respiratory collapse.</li>
                        <li>Sudden catastrophic drop in arterial blood pressure (dizziness, clamminess, fainting).</li>
                    </ul>
                </div>
                <div class="p-3 bg-card-subtle rounded-3 border">
                    <strong class="text-danger small"><i class="bi bi-check2-circle me-1"></i> Immediate Action:</strong>
                    <p class="small text-muted mb-0">Inject Epinephrine Auto-Injector (EpiPen) into the outer mid-thigh immediately through clothing. Call 911 even if symptoms improve (biphasic reaction risk).</p>
                </div>
            </div>
        </div>

        <!-- 6. Severe Hemorrhage & Trauma -->
        <div class="col-lg-6">
            <div class="card-custom p-4 h-100">
                <div class="d-flex justify-content-between align-items-start mb-3">
                    <div class="d-flex align-items-center gap-3">
                        <div class="p-3 bg-danger bg-opacity-10 text-danger rounded-3 fs-3">
                            <i class="bi bi-droplet-half"></i>
                        </div>
                        <div>
                            <h5 class="fw-bold mb-0">Uncontrolled Hemorrhage & Penetrating Trauma</h5>
                            <span class="badge bg-danger text-white small">Hemorrhagic Shock</span>
                        </div>
                    </div>
                </div>
                <div class="mb-3">
                    <h6 class="fw-bold small text-danger"><i class="bi bi-exclamation-circle me-1"></i> Warning Presentation:</h6>
                    <ul class="text-muted small ps-3 mb-0">
                        <li>Bright red, pulsatile, spurting blood indicative of an arterial laceration.</li>
                        <li>Bleeding that continues actively despite 10+ minutes of continuous direct manual pressure.</li>
                        <li>Coughing up copious bright red blood (massive hemoptysis) or vomiting dark coffee-ground blood (hematemesis).</li>
                        <li>High-energy trauma (motor vehicle collision, fall from &gt; 10 feet, gunshot or stab injury).</li>
                    </ul>
                </div>
                <div class="p-3 bg-card-subtle rounded-3 border">
                    <strong class="text-danger small"><i class="bi bi-check2-circle me-1"></i> Immediate Action:</strong>
                    <p class="small text-muted mb-0">Apply firm, continuous direct pressure with sterile gauze or clean cloth. If limb bleeding cannot be stopped, apply a commercial tourniquet 2-3 inches above the wound.</p>
                </div>
            </div>
        </div>

        <!-- 7. Thunderclap Headache & Meningitis -->
        <div class="col-lg-6">
            <div class="card-custom p-4 h-100">
                <div class="d-flex justify-content-between align-items-start mb-3">
                    <div class="d-flex align-items-center gap-3">
                        <div class="p-3 bg-danger bg-opacity-10 text-danger rounded-3 fs-3">
                            <i class="bi bi-lightning-charge"></i>
                        </div>
                        <div>
                            <h5 class="fw-bold mb-0">"Thunderclap" Headache & Meningitis Signs</h5>
                            <span class="badge bg-danger text-white small">Subarachnoid Hemorrhage / CNS Infection</span>
                        </div>
                    </div>
                </div>
                <div class="mb-3">
                    <h6 class="fw-bold small text-danger"><i class="bi bi-exclamation-circle me-1"></i> Warning Presentation:</h6>
                    <ul class="text-muted small ps-3 mb-0">
                        <li>Sudden, excruciating headache reaching peak intensity within 60 seconds ("worst headache of life").</li>
                        <li>Severe rigid neck stiffness (inability to touch chin to chest) paired with high fever and chills.</li>
                        <li>Non-blanching dark purple pinpoint rash (petechiae/purpura) that does not fade when pressed with glass.</li>
                        <li>Photophobia (extreme eye pain in room light) with projectile vomiting and acute confusion.</li>
                    </ul>
                </div>
                <div class="p-3 bg-card-subtle rounded-3 border">
                    <strong class="text-danger small"><i class="bi bi-check2-circle me-1"></i> Immediate Action:</strong>
                    <p class="small text-muted mb-0">Requires immediate neuroimaging (CT brain) or emergency lumbar puncture. Do not administer aspirin or anticoagulants prior to ruling out intracranial hemorrhage.</p>
                </div>
            </div>
        </div>

        <!-- 8. Pediatric Emergencies -->
        <div class="col-lg-6">
            <div class="card-custom p-4 h-100">
                <div class="d-flex justify-content-between align-items-start mb-3">
                    <div class="d-flex align-items-center gap-3">
                        <div class="p-3 bg-danger bg-opacity-10 text-danger rounded-3 fs-3">
                            <i class="bi bi-emoji-frown"></i>
                        </div>
                        <div>
                            <h5 class="fw-bold mb-0">Critical Pediatric & Neonatal Red Flags</h5>
                            <span class="badge bg-danger text-white small">Pediatric Emergency</span>
                        </div>
                    </div>
                </div>
                <div class="mb-3">
                    <h6 class="fw-bold small text-danger"><i class="bi bi-exclamation-circle me-1"></i> Warning Presentation:</h6>
                    <ul class="text-muted small ps-3 mb-0">
                        <li><strong>Infant Fever:</strong> Any rectal temperature &ge; 100.4°F (38.0°C) in an infant under 3 months of age is a mandatory emergency evaluation.</li>
                        <li>Severe lethargy, floppy muscle tone, unresponsiveness, or weak abnormal whimpering cry.</li>
                        <li>Sunken soft spot (fontanelle) with dry diapers for &gt; 8 hours indicating dangerous infant dehydration.</li>
                        <li>Nasal flaring, grunting sounds on expiration, and chest retractions while breathing.</li>
                    </ul>
                </div>
                <div class="p-3 bg-card-subtle rounded-3 border">
                    <strong class="text-danger small"><i class="bi bi-check2-circle me-1"></i> Immediate Action:</strong>
                    <p class="small text-muted mb-0">Transport immediately to the nearest Pediatric Emergency Department or call 911. Do not give aspirin to children/teens due to risk of Reye's syndrome.</p>
                </div>
            </div>
        </div>
    </div>

    <!-- Bystander Emergency Guidance -->
    <div class="card-custom p-4 p-md-5 mb-5 bg-gradient">
        <h3 class="fw-bold mb-3"><i class="bi bi-life-preserver text-info me-2"></i> What to Do While Waiting for Emergency Services</h3>
        <div class="row g-4">
            <div class="col-md-3">
                <div class="p-3 rounded-3 bg-card border h-100">
                    <div class="fw-bold text-info mb-2"><i class="bi bi-1-circle-fill me-1"></i> Clear Access</div>
                    <p class="small text-muted mb-0">Unlock the front door, turn on outdoor lights, restrain pets, and have someone meet the ambulance crew at the street if possible.</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="p-3 rounded-3 bg-card border h-100">
                    <div class="fw-bold text-info mb-2"><i class="bi bi-2-circle-fill me-1"></i> Do Not Give Oral Fluids</div>
                    <p class="small text-muted mb-0">Do not offer water, food, or oral medications if the person is confused or may require emergency general anesthesia or surgery.</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="p-3 rounded-3 bg-card border h-100">
                    <div class="fw-bold text-info mb-2"><i class="bi bi-3-circle-fill me-1"></i> Gather Medications</div>
                    <p class="small text-muted mb-0">Collect all daily prescription bottles, supplements, and allergy lists into a bag to hand directly to the paramedics upon arrival.</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="p-3 rounded-3 bg-card border h-100">
                    <div class="fw-bold text-info mb-2"><i class="bi bi-4-circle-fill me-1"></i> Hands-Only CPR</div>
                    <p class="small text-muted mb-0">If patient is unresponsive with no normal breathing, push hard and fast in the center of the chest (100-120 beats/min, to "Stayin' Alive").</p>
                </div>
            </div>
        </div>
    </div>

    <!-- Official Legal Disclaimer -->
    <div class="disclaimer-banner my-5 text-start p-4">
        <h5 class="fw-bold mb-2 text-danger"><i class="bi bi-shield-fill-exclamation me-2"></i> Mandatory Emergency Legal Disclaimer</h5>
        <p class="small text-muted mb-0">
            MediSense AI is a software application designed for educational and informational health literacy. It is NOT an emergency response platform, medical dispatch provider, or real-time diagnostic device. In any acute situation where you or another individual may be experiencing a medical emergency, you must immediately contact your local emergency number (such as 911, 112, or 999) or visit the closest emergency department. Never disregard or delay seeking emergency medical care based on content generated by or hosted on MediSense AI.
        </p>
    </div>
</div>

<?php
require_once __DIR__ . '/includes/footer.php';
?>
