<?php
// prevention.php - Prevention Center (Section 11)
require_once __DIR__ . '/includes/functions.php';
$page_title = 'MediSense AI | Prevention Center';
require_once __DIR__ . '/includes/header.php';

// The 10 Primary Prevention Domains specified in Section 11
$prevention_domains = [
    [
        'id' => 'diabetes',
        'title' => 'Diabetes Prevention',
        'badge' => 'Metabolic / Endocrine',
        'icon' => 'bi-droplet-half',
        'color' => 'text-primary',
        'overview' => 'Type 2 Diabetes mellitus is driven by progressive peripheral insulin resistance and relative pancreatic beta-cell fatigue. Over 80% of cases are preventable through evidence-based dietary and movement interventions.',
        'strategies' => [
            'Target a sustained 5% to 7% reduction in body weight if overweight, which lowers progression risk by up to 58%.',
            'Replace ultra-refined carbohydrates, white bread, and sweetened beverages with complex low-glycemic whole grains, lentils, and legumes.',
            'Incorporate at least 150 minutes of moderate-intensity exercise weekly, which directly enhances insulin-mediated glucose disposal into muscle cells.',
            'Ask for an annual fasting plasma glucose or HbA1c screening if aged 35+ or with a family history of diabetes.'
        ],
        'action_tip' => 'A 15-minute post-meal walk significantly blunts postprandial glucose spikes by directing glucose directly to working muscle tissue.'
    ],
    [
        'id' => 'heart',
        'title' => 'Heart Health & Cardiovascular Care',
        'badge' => 'Cardiovascular',
        'icon' => 'bi-heart-pulse-fill',
        'color' => 'text-danger',
        'overview' => 'Atherosclerosis and coronary heart disease develop silently over decades. Controlling vascular endothelial inflammation, blood pressure, and circulating apolipoprotein B is essential to lifelong heart health.',
        'strategies' => [
            'Follow the DASH or Mediterranean eating plan rich in potassium, magnesium, and dietary fiber while keeping sodium under 2,300 mg/day.',
            'Eliminate all forms of tobacco smoking, vaping, and secondhand exposure; vascular endothelial recovery begins within hours of cessation.',
            'Maintain resting blood pressure under 120/80 mm Hg and manage LDL cholesterol through unsaturated plant fats (olive oil, avocados, nuts).',
            'Engage in regular aerobic cardiovascular training to improve cardiac output, stroke volume, and arterial compliance.'
        ],
        'action_tip' => 'Replacing saturated animal fats with monounsaturated olive oil and omega-3 rich fatty fish reduces major adverse cardiovascular events by up to 30%.'
    ],
    [
        'id' => 'respiratory',
        'title' => 'Respiratory Health & Airway Defense',
        'badge' => 'Respiratory',
        'icon' => 'bi-lungs-fill',
        'color' => 'text-info',
        'overview' => 'Pulmonary alveoli and bronchial mucosa are vulnerable to oxidative airborne particles, tobacco toxins, and occupational irritants leading to COPD and chronic asthma.',
        'strategies' => [
            'Maintain smoke-free indoor living environments and avoid wood-burning stove or biomass smoke inhalation.',
            'Use HEPA air filtration during days with high particulate air pollution (PM2.5) or severe pollen counts.',
            'Practice deep diaphragmatic breathing and stay physically active to preserve vital lung capacity and functional residual volume.',
            'Receive seasonal influenza and pneumococcal immunizations to prevent secondary bacterial pneumonia in vulnerable airways.'
        ],
        'action_tip' => 'Ensure proper indoor ventilation and replace HVAC furnace filters every 90 days to minimize indoor mold spores and fine particulates.'
    ],
    [
        'id' => 'skin',
        'title' => 'Skin Health & UV Protection',
        'badge' => 'Dermatological',
        'icon' => 'bi-sun-fill',
        'color' => 'text-warning',
        'overview' => 'Solar ultraviolet radiation (UVA and UVB) causes cumulative DNA mutations in keratinocytes and melanocytes, accelerating photo-aging and triggering skin malignancies.',
        'strategies' => [
            'Apply broad-spectrum water-resistant sunscreen (SPF 30 or higher) daily to all sun-exposed skin, re-applying every 2 hours during outdoor activity.',
            'Seek shade during peak ultraviolet intensity hours between 10:00 AM and 4:00 PM.',
            'Wear protective wide-brimmed hats, UV-blocking sunglasses, and tightly woven sun-protective clothing.',
            'Perform monthly head-to-toe skin self-examinations using the ABCDE criteria (Asymmetry, Border, Color, Diameter, Evolving) for suspicious pigmented lesions.'
        ],
        'action_tip' => 'Never use indoor ultraviolet tanning beds; a single indoor tanning session before age 35 increases melanoma risk by 75%.'
    ],
    [
        'id' => 'nutrition',
        'title' => 'Nutrition & Whole-Food Eating',
        'badge' => 'Nutritional Health',
        'icon' => 'bi-egg-fried',
        'color' => 'text-success',
        'overview' => 'Nutrient-dense nutrition provides essential amino acids, micronutrients, polyphenols, and soluble fibers that nourish the gut microbiome and suppress chronic low-grade inflammation.',
        'strategies' => [
            'Fill half your plate with diverse colorful vegetables and whole fruits at every main meal to maximize antioxidant intake.',
            'Consume 25 to 35 grams of dietary fiber daily from oats, chia seeds, beans, lentils, and whole grains to support healthy lipid metabolism.',
            'Minimize ultra-processed packaged snacks, industrial trans fats, and artificial preservatives.',
            'Prioritize lean protein sources (legumes, tofu, poultry, fish, eggs) to maintain skeletal muscle mass across all age groups.'
        ],
        'action_tip' => 'Drinking a glass of water 20 minutes before meals and eating slowly promotes natural satiety signaling via gastrointestinal peptide hormones.'
    ],
    [
        'id' => 'activity',
        'title' => 'Physical Activity & Fitness',
        'badge' => 'Musculoskeletal / Vitality',
        'icon' => 'bi-bicycle',
        'color' => 'text-primary',
        'overview' => 'Prolonged physical inactivity is an independent risk factor for metabolic decline, osteopenia, cardiovascular disease, and depression. Movement is biological medicine.',
        'strategies' => [
            'Accumulate at least 150 minutes of moderate aerobic activity (e.g. brisk walking) or 75 minutes of vigorous activity weekly.',
            'Perform progressive resistance training targeting major muscle groups at least 2 days per week to preserve metabolic bone density.',
            'Break up prolonged sitting every 30 to 45 minutes with brief 2-minute standing or stretching breaks.',
            'Incorporate daily mobility, balance, and flexibility exercises to prevent musculoskeletal strains and lower fall risk with aging.'
        ],
        'action_tip' => 'Even short bouts of exercise (three 10-minute walks spread throughout the day) offer cardiovascular benefits comparable to one continuous 30-minute session.'
    ],
    [
        'id' => 'sleep',
        'title' => 'Sleep Hygiene & Restorative Rest',
        'badge' => 'Neuro-Recovery',
        'icon' => 'bi-moon-stars-fill',
        'color' => 'text-info',
        'overview' => 'During deep non-REM and REM sleep cycles, the brain undergoes glymphatic waste clearance, cellular repair takes place, and cardiovascular stress is minimized.',
        'strategies' => [
            'Aim for 7 to 9 hours of uninterrupted nocturnal sleep on a regular circadian schedule (same sleep and wake times daily).',
            'Keep bedroom temperatures cool (around 18°C / 65°F), completely dark, and quiet to support melatonin secretion.',
            'Eliminate blue-light emitting smartphones, tablets, and computers at least 60 minutes before bedtime.',
            'Limit caffeine consumption after 2:00 PM and avoid heavy alcoholic nightcaps, which fragment restorative REM sleep architecture.'
        ],
        'action_tip' => 'Viewing 15 to 30 minutes of natural outdoor sunlight within an hour of waking sets your internal master circadian clock for better nocturnal sleep onset.'
    ],
    [
        'id' => 'stress',
        'title' => 'Stress Management & Mental Health',
        'badge' => 'Psychological Wellbeing',
        'icon' => 'bi-emoji-smile-fill',
        'color' => 'text-warning',
        'overview' => 'Chronic psychological stress causes sustained sympathetic nervous system activation and elevated cortisol, driving systemic vascular inflammation, visceral fat gain, and digestive distress.',
        'strategies' => [
            'Practice evidence-based diaphragmatic breathing (e.g., 4-7-8 breathing or box breathing) to stimulate the vagus nerve and parasympathetic relaxation.',
            'Set healthy occupational and digital boundaries; schedule intentional screen-free downtime daily.',
            'Maintain meaningful social connections with friends, family, or community groups to foster emotional resilience.',
            'Engage in regular outdoor nature walks, journaling, or mindfulness meditation to lower sympathetic baseline arousal.'
        ],
        'action_tip' => 'A five-minute physiological sigh (two quick nasal inhales followed by one long, slow oral exhale) rapidly resets autonomic heart rate variability.'
    ],
    [
        'id' => 'infection',
        'title' => 'Infection Prevention & Hygiene',
        'badge' => 'Immune Protection',
        'icon' => 'bi-shield-plus',
        'color' => 'text-success',
        'overview' => 'Pathogenic bacteria, viruses, and fungi exploit mucous membranes and compromised skin barriers. Basic antiseptic and barrier practices prevent transmission.',
        'strategies' => [
            'Wash hands thoroughly with soap and clean running water for at least 20 seconds before eating, after using restrooms, and after public transit.',
            'Keep routine adult vaccinations up to date (seasonal influenza, tetanus boosters every 10 years, COVID-19, and shingles vaccines where indicated).',
            'Practice safe food hygiene: separate raw poultry and meats, cook to safe internal temperatures, and refrigerate leftovers promptly.',
            'Clean and dress minor cuts, scratches, or abrasions promptly with mild soap and protective bandages to prevent secondary bacterial cellulitis.'
        ],
        'action_tip' => 'Alcohol-based hand sanitizer (at least 60% alcohol) is an effective alternative when soap and potable water are temporarily unavailable.'
    ],
    [
        'id' => 'general',
        'title' => 'General Preventive Care & Screenings',
        'badge' => 'Clinical Guidance',
        'icon' => 'bi-clipboard-check',
        'color' => 'text-primary',
        'overview' => 'Many critical chronic illnesses—including hypertension, high cholesterol, pre-diabetes, and early cancers—develop without overt warning symptoms.',
        'strategies' => [
            'Schedule an annual comprehensive preventive physical examination with your primary healthcare provider.',
            'Monitor baseline blood pressure at least annually (or more frequently if readings exceed 120/80 mm Hg).',
            'Complete regular fasting lipid panels (total cholesterol, HDL, LDL, triglycerides) and glycemic tests (HbA1c).',
            'Follow age-appropriate evidence-based cancer screening guidelines (mammograms, colonoscopies, cervical cytology, dermatological exams).'
        ],
        'action_tip' => 'Maintain an updated digital record of your family medical history, routine immunizations, and annual lab trends to share with your physician.'
    ]
];
?>

<div class="row py-3">
    <div class="col-lg-12 text-center mb-4">
        <span class="badge hero-badge px-3 py-2 rounded-pill fw-bold mb-2">PREVENTIVE HEALTHCARE</span>
        <h1 class="display-5 fw-extrabold mb-2">Prevention Center</h1>
        <p class="lead text-muted mx-auto" style="max-width: 820px;">
            Evidence-based educational guidelines across 10 vital health pillars to optimize longevity, protect organ function, and minimize chronic disease vulnerability.
        </p>
    </div>
</div>

<!-- Category Jump Navigation (Section 11) -->
<div class="d-flex flex-wrap justify-content-center gap-2 mb-5">
    <?php foreach ($prevention_domains as $domain): ?>
        <a href="#<?= $domain['id'] ?>" class="btn btn-sm btn-outline-info rounded-pill px-3 py-2">
            <i class="bi <?= $domain['icon'] ?> me-1"></i> <?= sanitize($domain['title']) ?>
        </a>
    <?php endforeach; ?>
</div>

<!-- 10 Primary Prevention Domains Grid (Section 11) -->
<div class="row g-4 mb-5">
    <?php foreach ($prevention_domains as $idx => $d): ?>
        <div class="col-lg-6" id="<?= $d['id'] ?>">
            <div class="card-custom p-4 p-md-5 h-100 d-flex flex-column justify-content-between hover-lift">
                <div>
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <div class="p-3 rounded-circle bg-info bg-opacity-15 <?= $d['color'] ?> fs-3">
                            <i class="bi <?= $d['icon'] ?>"></i>
                        </div>
                        <span class="badge bg-secondary-subtle text-secondary border px-3 py-1 rounded-pill small">
                            <?= sanitize($d['badge']) ?>
                        </span>
                    </div>

                    <h4 class="fw-bold mb-2 text-body"><?= ($idx + 1) ?>. <?= sanitize($d['title']) ?></h4>
                    <p class="small text-muted mb-3" style="line-height: 1.6;">
                        <?= sanitize($d['overview']) ?>
                    </p>

                    <h6 class="fw-bold small text-uppercase text-info mb-2">
                        <i class="bi bi-shield-check me-1"></i> Evidence-Based Strategies:
                    </h6>
                    <ul class="small text-muted ps-3 mb-4">
                        <?php foreach ($d['strategies'] as $strat): ?>
                            <li class="mb-2"><?= sanitize($strat) ?></li>
                        <?php endforeach; ?>
                    </ul>
                </div>

                <div class="p-3 rounded-3 border bg-card-subtle mt-2">
                    <strong class="d-block small text-success mb-1">
                        <i class="bi bi-lightning-charge-fill me-1"></i> Actionable Habit:
                    </strong>
                    <p class="small text-muted mb-0"><?= sanitize($d['action_tip']) ?></p>
                </div>
            </div>
        </div>
    <?php endforeach; ?>
</div>

<!-- Prevention Checklist & Tools Banner -->
<div class="card-custom p-4 p-md-5 mb-5 hero-banner">
    <div class="row align-items-center">
        <div class="col-lg-8">
            <span class="badge hero-badge px-3 py-1 mb-2 fw-bold">Interactive Tools</span>
            <h3 class="fw-bold hero-heading mb-2">Ready to evaluate your current risk level?</h3>
            <p class="hero-lead mb-3">
                Pair prevention strategies with real-time biometric risk calculations and symptom evaluation tools.
            </p>
            <div class="d-flex flex-wrap gap-2">
                <a href="risk_calculator.php" class="btn btn-primary-custom rounded-pill px-4">
                    <i class="bi bi-calculator me-1"></i> Run Health Risk Calculator
                </a>
                <a href="prediction.php" class="btn btn-outline-info rounded-pill px-4">
                    <i class="bi bi-cpu me-1"></i> AI Symptom Checker
                </a>
                <a href="health_assistant.php" class="btn btn-outline-success rounded-pill px-4">
                    <i class="bi bi-chat-heart me-1"></i> Ask AI Assistant
                </a>
            </div>
        </div>
        <div class="col-lg-4 text-center mt-3 mt-lg-0">
            <i class="bi bi-heart-pulse-fill display-1 text-info opacity-50"></i>
        </div>
    </div>
</div>

<!-- Medical Disclaimer -->
<div class="alert alert-secondary py-3 px-4 rounded-3 border text-center small">
    <i class="bi bi-shield-exclamation text-warning me-1"></i>
    <strong>Disclaimer:</strong> Preventive guidance provided by MediSense AI is based on general health guidelines and clinical consensus. It does not replace individualized clinical advice from your physician or licensed specialist.
</div>

<?php require_once __DIR__ . '/includes/footer.php'; ?>
