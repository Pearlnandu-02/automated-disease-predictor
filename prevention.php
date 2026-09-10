<?php
require_once __DIR__ . '/includes/functions.php';
require_once __DIR__ . '/includes/header.php';

// Structured Healthy Lifestyle Pillars
$lifestyle_pillars = [
    [
        'icon' => 'bi-egg-fried',
        'title' => 'Nutritional Balance',
        'badge' => 'Diet & Fuel',
        'color' => 'text-success',
        'explanation' => 'A diverse, nutrient-rich diet forms the fundamental biochemical foundation of immune defense, cellular repair, and cardiovascular vitality.',
        'tip' => 'Prioritize whole grains, colorful vegetables, legumes, lean proteins, and unsaturated fats while minimizing ultra-processed sugars and excessive dietary sodium (<2,300 mg/day).'
    ],
    [
        'icon' => 'bi-lightning-charge-fill',
        'title' => 'Physical Activity',
        'badge' => 'Movement',
        'color' => 'text-warning',
        'explanation' => 'Consistent daily movement enhances insulin sensitivity, improves endothelial vascular function, and promotes neuroplasticity.',
        'tip' => 'Target at least 150 minutes of moderate-intensity aerobic exercise (brisk walking, cycling) or 75 minutes of vigorous activity weekly, supplemented by muscle-strengthening twice a week.'
    ],
    [
        'icon' => 'bi-moon-stars-fill',
        'title' => 'Restorative Sleep',
        'badge' => 'Recovery',
        'color' => 'text-info',
        'explanation' => 'Adequate sleep facilitates glymphatic waste clearance in the brain, hormonal equilibrium, memory consolidation, and tissue regeneration.',
        'tip' => 'Aim for 7 to 9 hours of uninterrupted nocturnal sleep in a cool, dark room. Establish a consistent sleep schedule and limit stimulating blue screens 60 minutes before bedtime.'
    ],
    [
        'icon' => 'bi-droplet-fill',
        'title' => 'Optimal Hydration',
        'badge' => 'Vital Fluids',
        'color' => 'text-primary',
        'explanation' => 'Water is essential for renal excretion of metabolic wastes, joint lubrication, cognitive focus, and body temperature regulation.',
        'tip' => 'Consume approximately 2 to 3 liters of water daily based on activity level and climate. Rely primarily on fresh water rather than sugar-sweetened beverages or energy drinks.'
    ],
    [
        'icon' => 'bi-heart-half',
        'title' => 'Stress Management',
        'badge' => 'Nervous System',
        'color' => 'text-danger',
        'explanation' => 'Chronic psychological stress causes sustained cortisol and sympathetic elevation, promoting systemic vascular inflammation and immune suppression.',
        'tip' => 'Integrate evidence-based mindfulness, diaphragmatic breathing exercises, nature immersion, or regular therapeutic hobbies to down-regulate sympathetic fight-or-flight states.'
    ],
    [
        'icon' => 'bi-shield-shaded',
        'title' => 'Personal & Domestic Hygiene',
        'badge' => 'Sanitation',
        'color' => 'text-success',
        'explanation' => 'Infection control stops pathogenic bacteria, viruses, and parasites before they can establish colonization within mucous membranes.',
        'tip' => 'Wash hands with soap and water for at least 20 seconds before eating, after using restrooms, and after public transit. Practice safe food handling and surface disinfection.'
    ],
    [
        'icon' => 'bi-capsule',
        'title' => 'Vaccination Awareness',
        'badge' => 'Immunization',
        'color' => 'text-info',
        'explanation' => 'Immunizations stimulate adaptive immunological memory, conferring strong systemic protection against life-threatening bacterial and viral illnesses.',
        'tip' => 'Keep routine immunizations up-to-date, including seasonal influenza vaccines, COVID-19 boosters, tetanus toxoid every 10 years, and pneumococcal or shingles vaccines as clinically advised.'
    ],
    [
        'icon' => 'bi-clipboard2-pulse',
        'title' => 'Regular Health Screenings',
        'badge' => 'Proactive Care',
        'color' => 'text-warning',
        'explanation' => 'Many critical chronic illnesses—including hypertension, pre-diabetes, and hyperlipidemia—remain asymptomatic during their earliest, most reversible stages.',
        'tip' => 'Schedule an annual preventive physical examination with your primary physician to monitor blood pressure, lipid profile, fasting blood glucose, and age-recommended cancer screenings.'
    ]
];

// Chronic Disease Prevention Focus Areas
$chronic_prevention = [
    [
        'icon' => 'bi-heart-pulse',
        'title' => 'Heart Health & Circulation',
        'badge' => 'Cardiovascular',
        'explanation' => 'Preventing atherosclerotic coronary artery disease, hypertensive vascular changes, and myocardial infarction.',
        'tip' => 'Regular aerobic activity, avoiding all tobacco and vaping exposure, maintaining a BMI between 18.5–24.9, and keeping blood pressure under 120/80 mmHg support long-term cardiac longevity.'
    ],
    [
        'icon' => 'bi-droplet-half',
        'title' => 'Diabetes Prevention & Metabolic Care',
        'badge' => 'Endocrine',
        'explanation' => 'Protecting pancreatic beta-cell function and preventing insulin receptor resistance across peripheral tissues.',
        'tip' => 'Replace refined starches and high-fructose syrups with fiber-rich complex carbohydrates. Modest weight loss of 5–7% can reduce pre-diabetes progression to Type 2 diabetes by up to 58%.'
    ],
    [
        'icon' => 'bi-lungs',
        'title' => 'Respiratory Longevity',
        'badge' => 'Pulmonary',
        'explanation' => 'Protecting delicate bronchial passages and pulmonary alveoli from chronic inflammatory destruction and airway remodeling.',
        'tip' => 'Avoid tobacco smoke, secondhand smoke, and indoor biomass combustion fumes. Ensure adequate household airflow and use air filtration during high-particulate air quality alerts.'
    ],
    [
        'icon' => 'bi-water',
        'title' => 'Kidney Health Preservation',
        'badge' => 'Renal',
        'explanation' => 'Preserving glomerular filtration rate and preventing irreversible nephron fibrosis caused by hypertension or diabetes.',
        'tip' => 'Drink adequate clean water, strictly control blood pressure and blood glucose, and avoid frequent or unmonitored over-the-counter NSAID pain relievers (such as ibuprofen).'
    ],
    [
        'icon' => 'bi-shield-plus',
        'title' => 'Liver Health & Metabolic Protection',
        'badge' => 'Hepatic',
        'explanation' => 'Safeguarding hepatocytes from steatosis (fatty liver disease), viral inflammation, and chemical or pharmaceutical hepatotoxicity.',
        'tip' => 'Limit alcohol consumption, get vaccinated against Hepatitis A and B, use medications only as directed, and combat metabolic-associated fatty liver disease (MAFLD) through a balanced diet.'
    ],
    [
        'icon' => 'bi-puzzle',
        'title' => 'Mental Well-being & Cognitive Health',
        'badge' => 'Neurological',
        'explanation' => 'Nurturing neurochemistry, cognitive reserve, emotional resilience, and lifelong brain synaptic connectivity.',
        'tip' => 'Engage in continuous mental challenges (reading, learning new skills), foster supportive social connections, prioritize rest, and seek professional mental health counseling whenever needed.'
    ]
];
?>

<div class="row py-3">
    <div class="col-lg-12 text-center mb-4">
        <span class="badge hero-badge px-3 py-2 rounded-pill fw-bold mb-2">PREVENTATIVE HEALTH GUIDELINES</span>
        <h1 class="display-5 fw-extrabold mb-2">Health Awareness & Disease Prevention</h1>
        <p class="lead text-muted mx-auto" style="max-width: 780px;">
            Evidence-based preventative practices, lifestyle foundations, and organ-specific risk reduction strategies designed to support lifelong wellness and early clinical detection.
        </p>
    </div>
</div>

<!-- SECTION 1: Healthy Lifestyle Foundations -->
<div class="mb-5">
    <div class="d-flex align-items-center mb-4">
        <div class="p-2 bg-info bg-opacity-20 text-info rounded-circle me-3">
            <i class="bi bi-compass fs-4"></i>
        </div>
        <div>
            <h3 class="fw-bold mb-0">Foundations of Healthy Living</h3>
            <p class="small text-muted mb-0">Core daily behaviors that cultivate baseline physiological health and resilience</p>
        </div>
    </div>

    <div class="row g-4">
        <?php foreach ($lifestyle_pillars as $pillar): ?>
            <div class="col-md-6 col-lg-3">
                <div class="card-custom p-4 h-100 d-flex flex-column justify-content-between hover-elevate">
                    <div>
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <div class="p-3 bg-card-subtle rounded-3 <?= $pillar['color'] ?>">
                                <i class="bi <?= $pillar['icon'] ?> fs-3"></i>
                            </div>
                            <span class="badge bg-secondary bg-opacity-25 text-info border border-info border-opacity-25 small">
                                <?= sanitize($pillar['badge']) ?>
                            </span>
                        </div>
                        <h5 class="fw-bold mb-2"><?= sanitize($pillar['title']) ?></h5>
                        <p class="small text-muted mb-3" style="line-height: 1.6;">
                            <?= sanitize($pillar['explanation']) ?>
                        </p>
                    </div>
                    <div class="p-3 bg-card-subtle rounded-3 border mt-2">
                        <strong class="text-info d-block small mb-1">
                            <i class="bi bi-lightbulb-fill me-1"></i> Practical Action Tip:
                        </strong>
                        <p class="small text-muted mb-0" style="font-size: 0.85rem;">
                            <?= sanitize($pillar['tip']) ?>
                        </p>
                    </div>
                </div>
            </div>
        <?php endforeach; ?>
    </div>
</div>

<!-- SECTION 2: Chronic Disease Prevention -->
<div class="mb-5">
    <div class="d-flex align-items-center mb-4">
        <div class="p-2 bg-warning bg-opacity-20 text-warning rounded-circle me-3">
            <i class="bi bi-shield-check fs-4"></i>
        </div>
        <div>
            <h3 class="fw-bold mb-0">Chronic Disease Prevention</h3>
            <p class="small text-muted mb-0">Targeted organ-system protection against widespread non-communicable conditions</p>
        </div>
    </div>

    <div class="row g-4">
        <?php foreach ($chronic_prevention as $item): ?>
            <div class="col-md-6 col-lg-4">
                <div class="card-custom p-4 h-100 d-flex flex-column justify-content-between">
                    <div>
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <div class="p-3 bg-card-subtle text-warning rounded-3">
                                <i class="bi <?= $item['icon'] ?> fs-3"></i>
                            </div>
                            <span class="badge bg-secondary bg-opacity-25 text-warning border border-warning border-opacity-25 small">
                                <?= sanitize($item['badge']) ?>
                            </span>
                        </div>
                        <h5 class="fw-bold mb-2"><?= sanitize($item['title']) ?></h5>
                        <p class="small text-muted mb-3" style="line-height: 1.6;">
                            <?= sanitize($item['explanation']) ?>
                        </p>
                    </div>
                    <div class="p-3 bg-card-subtle rounded-3 border mt-2">
                        <strong class="text-warning d-block small mb-1">
                            <i class="bi bi-check-circle-fill me-1"></i> Preventative Recommendation:
                        </strong>
                        <p class="small text-muted mb-0" style="font-size: 0.85rem;">
                            <?= sanitize($item['tip']) ?>
                        </p>
                    </div>
                </div>
            </div>
        <?php endforeach; ?>
    </div>
</div>

<!-- SECTION 3: Emergency Warning Signs & Triage -->
<div class="card-custom p-4 p-md-5 my-5 border-danger" style="border-width: 2px;">
    <div class="d-flex align-items-center mb-3">
        <div class="p-3 bg-danger bg-opacity-20 text-danger rounded-circle me-3">
            <i class="bi bi-exclamation-octagon-fill fs-2"></i>
        </div>
        <div>
            <h3 class="fw-bold text-danger mb-1">When to Seek Immediate Emergency Medical Attention</h3>
            <p class="small text-muted mb-0">Severe physiological red flags requiring prompt emergency hospital evaluation (Dial 911 / 112)</p>
        </div>
    </div>

    <div class="row g-4 mt-1">
        <div class="col-md-6 col-lg-3">
            <div class="p-3 bg-card-subtle rounded-3 border border-danger border-opacity-25 h-100">
                <div class="text-danger fw-bold mb-2 d-flex align-items-center">
                    <i class="bi bi-heart-pulse-fill me-2 fs-5"></i> Cardiac Emergencies
                </div>
                <ul class="text-muted small mb-0 ps-3">
                    <li>Crushing, squeezing chest pressure or fullness</li>
                    <li>Pain radiating to the jaw, neck, back, or left arm</li>
                    <li>Sudden cold sweats, shortness of breath, or nausea</li>
                </ul>
            </div>
        </div>
        <div class="col-md-6 col-lg-3">
            <div class="p-3 bg-card-subtle rounded-3 border border-danger border-opacity-25 h-100">
                <div class="text-danger fw-bold mb-2 d-flex align-items-center">
                    <i class="bi bi-wind me-2 fs-5"></i> Respiratory Crises
                </div>
                <ul class="text-muted small mb-0 ps-3">
                    <li>Severe air hunger or inability to speak full sentences</li>
                    <li>Bluish or pale discoloration of lips or fingertips (cyanosis)</li>
                    <li>Audible stridor or sudden airway obstruction</li>
                </ul>
            </div>
        </div>
        <div class="col-md-6 col-lg-3">
            <div class="p-3 bg-card-subtle rounded-3 border border-danger border-opacity-25 h-100">
                <div class="text-danger fw-bold mb-2 d-flex align-items-center">
                    <i class="bi bi-person-exclamation me-2 fs-5"></i> Neurological Emergencies
                </div>
                <ul class="text-muted small mb-0 ps-3">
                    <li>Sudden facial drooping, arm weakness, or slurred speech (FAST stroke signs)</li>
                    <li>Sudden severe "thunderclap" headache</li>
                    <li>Involuntary convulsions or seizure lasting > 5 minutes</li>
                </ul>
            </div>
        </div>
        <div class="col-md-6 col-lg-3">
            <div class="p-3 bg-card-subtle rounded-3 border border-danger border-opacity-25 h-100">
                <div class="text-danger fw-bold mb-2 d-flex align-items-center">
                    <i class="bi bi-virus me-2 fs-5"></i> Severe Systemic Sepsis
                </div>
                <ul class="text-muted small mb-0 ps-3">
                    <li>Extremely high fever (>103°F) with acute confusion</li>
                    <li>Severe drenching rigors and uncontrollable shivering</li>
                    <li>Rapid heart rate coupled with plummeting blood pressure</li>
                </ul>
            </div>
        </div>
    </div>

    <div class="p-3 bg-danger bg-opacity-10 border border-danger border-opacity-25 rounded-3 mt-4 text-center">
        <span class="text-danger fw-bold small">
            <i class="bi bi-telephone-fill me-1"></i> If you or someone near you experiences any of these red-flag symptoms, do not use web tools—seek emergency medical attention or contact emergency services immediately.
        </span>
    </div>
</div>

<!-- Educational Disclaimer -->
<div class="disclaimer-banner mb-5 p-4 text-start">
    <h5 class="fw-bold mb-2 text-warning"><i class="bi bi-info-circle-fill me-2"></i> Educational Notice</h5>
    <p class="small text-muted mb-0">
        The preventative health strategies and general tips provided on this platform are for broad educational and informational purposes only. They do not constitute personalized medical advice, diagnosis, or prescription. Always consult a qualified, licensed medical professional regarding individual health concerns or treatment plans.
    </p>
</div>

<?php
require_once __DIR__ . '/includes/footer.php';
?>
