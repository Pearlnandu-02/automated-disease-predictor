<?php
require_once __DIR__ . '/includes/functions.php';
require_once __DIR__ . '/includes/header.php';

// Comprehensive structured symptom knowledge base aligned with ML dictionary
$symptom_guide_data = [
    // General
    [
        'key' => 'fatigue',
        'name' => 'Chronic Lethargy & Fatigue',
        'category' => 'General',
        'icon' => 'bi-battery-half',
        'explanation' => 'A persistent sense of extreme physical exhaustion and lack of vital energy that does not significantly resolve with sleep or normal rest.',
        'conditions' => 'Anemia, Chronic Kidney Disease, Diabetes, Hypothyroidism, Heart Disease, Post-viral Syndromes',
        'when_to_seek' => 'When accompanied by shortness of breath, unexplained fever, sudden weight loss, chest discomfort, or when it impairs everyday tasks.'
    ],
    [
        'key' => 'fever',
        'name' => 'Fever (>100.4°F / 38°C)',
        'category' => 'General',
        'icon' => 'bi-thermometer-high',
        'explanation' => 'An elevated body temperature resulting from the body\'s immune response to microbial infection, inflammation, or systemic illness.',
        'conditions' => 'Pneumonia, Urinary Tract Infection, COVID-19, Malaria, Tuberculosis, Bacterial Infections',
        'when_to_seek' => 'If body temperature exceeds 103°F (39.4°C), lasts more than 3 consecutive days, or is accompanied by stiff neck, mental confusion, or rash.'
    ],
    [
        'key' => 'chills',
        'name' => 'Severe Chills & Rigors',
        'category' => 'General',
        'icon' => 'bi-snow',
        'explanation' => 'Involuntary muscular shivering accompanied by a feeling of coldness, frequently signaling an acute surge in core body temperature.',
        'conditions' => 'Acute Pneumonia, Sepsis, Pyelonephritis (Kidney Infection), Malaria, Influenza',
        'when_to_seek' => 'When occurring with shaking rigors, high fever, delirium, sudden shortness of breath, or localized acute flank or back pain.'
    ],
    [
        'key' => 'weight_loss',
        'name' => 'Unexplained Rapid Weight Loss',
        'category' => 'General',
        'icon' => 'bi-graph-down-arrow',
        'explanation' => 'Losing more than 5% of body weight unintentionally over 6 to 12 months without deliberate dietary restriction or increased physical activity.',
        'conditions' => 'Type 1 Diabetes, Hyperthyroidism, Tuberculosis, Chronic Kidney Disease, Malabsorption Syndromes',
        'when_to_seek' => 'Prompt medical consultation is advised whenever weight decline is continuous, involuntary, or coupled with severe fatigue and night sweats.'
    ],
    [
        'key' => 'sweats',
        'name' => 'Drenching Night Sweats',
        'category' => 'General',
        'icon' => 'bi-droplet-half',
        'explanation' => 'Repeated episodes of extreme perspiration during nocturnal sleep that soak through bedclothes and linens despite comfortable room temperatures.',
        'conditions' => 'Tuberculosis, Endocrine Imbalances, Chronic Infections, Lymphoma, Hyperthyroidism',
        'when_to_seek' => 'If persisting for more than 2 weeks, or accompanied by low-grade fever, cough, enlarged lymph nodes, or unexplained weight loss.'
    ],

    // Respiratory
    [
        'key' => 'shortness_of_breath',
        'name' => 'Shortness of Breath (Dyspnea)',
        'category' => 'Respiratory',
        'icon' => 'bi-wind',
        'explanation' => 'A subjective sensation of air hunger, labored breathing, or inability to take in a complete breath during mild exertion or at rest.',
        'conditions' => 'Asthma, Chronic Obstructive Pulmonary Disease (COPD), Pneumonia, Congestive Heart Failure, Pulmonary Embolism',
        'when_to_seek' => 'Seek immediate emergency medical evaluation if sudden in onset, accompanied by chest tightness, blue lips/fingertips, or lightheadedness.'
    ],
    [
        'key' => 'cough_with_sputum',
        'name' => 'Persistent Productive Cough',
        'category' => 'Respiratory',
        'icon' => 'bi-lungs',
        'explanation' => 'A persistent reflex cough producing noticeable phlegm or mucus from the lower respiratory tract lasting longer than two weeks.',
        'conditions' => 'Bacterial Pneumonia, Chronic Bronchitis, Asthma Exacerbation, Bronchiectasis, Tuberculosis',
        'when_to_seek' => 'When mucus turns rusty or discolored with high fever, or if coughing fits cause vomiting, severe chest pain, or wheezing.'
    ],
    [
        'key' => 'wheezing',
        'name' => 'Respiratory Wheezing',
        'category' => 'Respiratory',
        'icon' => 'bi-soundwave',
        'explanation' => 'A high-pitched musical whistling sound produced by air passing through narrowed or inflamed bronchial airways during expiration.',
        'conditions' => 'Bronchial Asthma, COPD, Acute Allergic Reactions, Bronchiolitis, Vocal Cord Dysfunction',
        'when_to_seek' => 'Immediate clinical attention is critical if wheezing begins acutely after allergen exposure, causes gasping, or limits speech to single words.'
    ],
    [
        'key' => 'hemoptysis',
        'name' => 'Hemoptysis (Coughing Blood)',
        'category' => 'Respiratory',
        'icon' => 'bi-exclamation-octagon',
        'explanation' => 'The expectoration of frank blood or blood-tinged sputum originating from the lungs, bronchi, or trachea.',
        'conditions' => 'Pulmonary Tuberculosis, Severe Pneumonia, Pulmonary Embolism, Bronchiectasis, Lung Malignancy',
        'when_to_seek' => 'Immediate emergency evaluation is mandatory for any coughing of blood to identify the underlying vascular or infectious etiology.'
    ],

    // Digestive & Hepatic
    [
        'key' => 'heartburn',
        'name' => 'Heartburn & Acid Reflux',
        'category' => 'Digestive',
        'icon' => 'bi-fire',
        'explanation' => 'A burning retrosternal discomfort moving up toward the throat, caused by acidic gastric contents regurgitating into the esophagus.',
        'conditions' => 'Gastroesophageal Reflux Disease (GERD), Hiatal Hernia, Gastritis, Peptic Ulcer Disease',
        'when_to_seek' => 'When accompanied by difficulty swallowing, vomiting coffee-ground material, black stools, or if radiating to jaw, neck, or left arm.'
    ],
    [
        'key' => 'jaundice',
        'name' => 'Jaundice (Yellowing Eyes & Skin)',
        'category' => 'Digestive',
        'icon' => 'bi-eye-fill',
        'explanation' => 'Yellowish discoloration of the sclera (white of eyes) and cutaneous skin caused by hyperbilirubinemia in circulating blood.',
        'conditions' => 'Hepatitis (A, B, C), Cirrhosis, Biliary Obstruction (Gallstones), Hemolytic Anemia, Toxic Liver Injury',
        'when_to_seek' => 'Urgent medical evaluation is needed. Especially vital when accompanied by dark amber urine, pale clay-colored stool, or abdominal distension.'
    ],
    [
        'key' => 'right_upper_quadrant_pain',
        'name' => 'Right Upper Quadrant Abdominal Pain',
        'category' => 'Digestive',
        'icon' => 'bi-bandaid',
        'explanation' => 'Discomfort, dull ache, or sharp spasms localized to the right side of the upper abdomen directly below the rib cage.',
        'conditions' => 'Cholecystitis (Gallbladder inflammation), Gallstones, Acute Hepatitis, Liver Abscess, Peptic Duodenal Ulcer',
        'when_to_seek' => 'When pain is severe, radiates to the right shoulder blade, or is joined by fever, vomiting, and yellowing sclera.'
    ],

    // Neurological
    [
        'key' => 'headache',
        'name' => 'Severe Throbbing Headache',
        'category' => 'Neurological',
        'icon' => 'bi-headset-vr',
        'explanation' => 'Intense cranial or temporal pain, which may present as throbbing, pressure, or band-like constriction around the head.',
        'conditions' => 'Migraine with/without aura, Severe Hypertension, Tension Cephalea, Sinusitis, Temporal Arteritis',
        'when_to_seek' => 'Immediately if "worst headache of life", or joined by stiff neck, fever, vision changes, confusion, facial droop, or limb weakness.'
    ],
    [
        'key' => 'resting_tremor',
        'name' => 'Resting Hand / Limb Tremor',
        'category' => 'Neurological',
        'icon' => 'bi-hand-index-thumb',
        'explanation' => 'An involuntary, rhythmic oscillatory movement of a hand, arm, or leg occurring primarily when the affected extremity is relaxed and supported.',
        'conditions' => 'Parkinson\'s Disease, Essential Tremor, Hyperthyroidism, Drug-induced Extrapyramidal Effects',
        'when_to_seek' => 'Consult a neurologist when tremors interfere with daily eating, writing, or gait balance, or progress over weeks.'
    ],
    [
        'key' => 'seizures',
        'name' => 'Involuntary Seizures / Convulsions',
        'category' => 'Neurological',
        'icon' => 'bi-lightning-charge',
        'explanation' => 'Sudden, uncontrolled electrical surges in cerebral neurons causing temporary changes in behavior, muscle twitching, or loss of consciousness.',
        'conditions' => 'Epilepsy, Severe Metabolic Disturbance, High Febrile Convulsions, Stroke, Hypoglycemia',
        'when_to_seek' => 'Call emergency emergency services immediately. Continuous seizures lasting >5 minutes require emergent neurological stabilization.'
    ],
    [
        'key' => 'memory_loss',
        'name' => 'Progressive Memory Decline',
        'category' => 'Neurological',
        'icon' => 'bi-journal-medical',
        'explanation' => 'Impairment in short-term recall, spatial disorientation, or difficulty retaining recently learned information beyond typical age-related forgetfulness.',
        'conditions' => 'Mild Cognitive Impairment (MCI), Alzheimer\'s Disease, Vascular Dementia, Vitamin B12 Deficiency, Hypothyroidism',
        'when_to_seek' => 'When forgetfulness compromises home safety, medication management, financial autonomy, or orientation to familiar places.'
    ],

    // Urinary / Kidney
    [
        'key' => 'frequent_urination',
        'name' => 'Frequent Urination (Polyuria)',
        'category' => 'Urinary',
        'icon' => 'bi-clock-history',
        'explanation' => 'An unusually increased frequency of voiding urine throughout the day or night (nocturia), often producing large volumes.',
        'conditions' => 'Type 1 & 2 Diabetes, Urinary Tract Infection, Chronic Kidney Disease, Benign Prostatic Hyperplasia (BPH), Diuretic Therapy',
        'when_to_seek' => 'When accompanied by unquenchable thirst, pelvic pain, discolored or foul-smelling urine, or systemic fever.'
    ],
    [
        'key' => 'dysuria',
        'name' => 'Dysuria (Painful Urination)',
        'category' => 'Urinary',
        'icon' => 'bi-shield-exclamation',
        'explanation' => 'A sharp burning, stinging, or scalding discomfort in the urethra during or directly following the passage of urine.',
        'conditions' => 'Urinary Tract Infection (Cystitis), Urethritis, Kidney Stones (Nephrolithiasis), Prostatitis',
        'when_to_seek' => 'If accompanied by fever, chills, lower back/flank pain, visible hematuria, or persistent symptoms despite increased hydration.'
    ],
    [
        'key' => 'flank_pain',
        'name' => 'Flank & Costovertebral Pain',
        'category' => 'Urinary',
        'icon' => 'bi-activity',
        'explanation' => 'Dull or spasmodic cramping pain located in the side of the body between the upper abdomen and the back, near the anatomical kidneys.',
        'conditions' => 'Nephrolithiasis (Kidney Stones), Pyelonephritis (Renal Infection), Polycystic Kidney Disease, Muscle Strain',
        'when_to_seek' => 'Urgent care is indicated for severe colicky spasms, inability to find a comfortable position, vomiting, or accompanying fever.'
    ],

    // Cardiovascular
    [
        'key' => 'chest_pain',
        'name' => 'Chest Pain & Retrosternal Pressure',
        'category' => 'Cardiovascular',
        'icon' => 'bi-heart-pulse-fill',
        'explanation' => 'Discomfort, squeezing, tightness, heaviness, or burning sensation felt in the anterior chest or precordium.',
        'conditions' => 'Coronary Artery Disease, Myocardial Infarction, Angina Pectoris, Pericarditis, Aortic Dissection, Severe GERD',
        'when_to_seek' => 'EMERGENCY: If chest pain lasts >5 minutes, radiates to the jaw, back, neck, or left arm, or occurs with diaphoresis, call emergency services immediately.'
    ],
    [
        'key' => 'high_blood_pressure',
        'name' => 'Hypertension Indicators',
        'category' => 'Cardiovascular',
        'icon' => 'bi-speedometer2',
        'explanation' => 'Chronically elevated arterial hydrostatic pressure (≥130/80 mmHg). Often silent, but severe spikes may produce characteristic signs.',
        'conditions' => 'Essential Hypertension, Secondary Renovascular Disease, Chronic Kidney Disease, Preeclampsia, Pheochromocytoma',
        'when_to_seek' => 'Immediate evaluation if blood pressure exceeds 180/120 mmHg (Hypertensive Crisis), especially with chest pain, vision changes, or shortness of breath.'
    ],
    [
        'key' => 'palpitations',
        'name' => 'Rapid Heart Palpitations',
        'category' => 'Cardiovascular',
        'icon' => 'bi-activity',
        'explanation' => 'An awareness of fluttering, rapid pounding, racing, or skipped cardiac beats felt within the chest or neck.',
        'conditions' => 'Atrial Fibrillation, Supraventricular Tachycardia, Hyperthyroidism, Severe Anemia, Anxiety / Panic Response',
        'when_to_seek' => 'When palpitations are accompanied by near-syncope (fainting), lightheadedness, chest tightness, or persistent racing pulse at rest.'
    ],

    // Endocrine / Metabolic
    [
        'key' => 'high_blood_sugar',
        'name' => 'High Blood Sugar & Polydipsia',
        'category' => 'Endocrine',
        'icon' => 'bi-droplet',
        'explanation' => 'Excess glucose in circulation (Hyperglycemia), producing excessive thirst (polydipsia), dry mouth, and increased volume of urination.',
        'conditions' => 'Type 1 & Type 2 Diabetes Mellitus, Metabolic Syndrome, Cushing\'s Syndrome, Impaired Glucose Tolerance',
        'when_to_seek' => 'Urgent care is required if fruity breath odor, rapid breathing, confusion, or nausea develops (Diabetic Ketoacidosis risk).'
    ],
    [
        'key' => 'cold_intolerance',
        'name' => 'Cold Intolerance & Hypometabolism',
        'category' => 'Endocrine',
        'icon' => 'bi-thermometer-snow',
        'explanation' => 'An abnormal, heightened sensitivity to cold ambient temperatures caused by reduced basal metabolic heat production.',
        'conditions' => 'Hypothyroidism (Hashimoto\'s Disease), Severe Anemia, Raynaud\'s Phenomenon, Hypopituitarism, Anorexia',
        'when_to_seek' => 'When joined by sluggishness, coarse dry skin, constipation, bradycardia (slow heart rate), or progressive weight gain.'
    ],
    [
        'key' => 'heat_intolerance',
        'name' => 'Heat Intolerance & Hyperhidrosis',
        'category' => 'Endocrine',
        'icon' => 'bi-thermometer-sun',
        'explanation' => 'Hypersensitivity to moderately warm environments, associated with excessive cutaneous sweating, irritability, and heat distress.',
        'conditions' => 'Hyperthyroidism (Graves\' Disease), Autonomic Neuropathy, Pheochromocytoma, Menopausal Transitions',
        'when_to_seek' => 'If accompanied by continuous rapid pulse, unintentional weight loss, bulging eyes (proptosis), or significant fine tremors.'
    ],
    [
        'key' => 'joint_pain',
        'name' => 'Severe Joint / Bone Pain',
        'category' => 'Musculoskeletal',
        'icon' => 'bi-diagram-3',
        'explanation' => 'Aching, stiffness, warmth, or swelling within articular joints that restricts range of motion or weight-bearing mobility.',
        'conditions' => 'Osteoarthritis, Rheumatoid Arthritis, Gouty Arthritis, Septic Arthritis, Systemic Lupus Erythematosus',
        'when_to_seek' => 'Immediate evaluation if a single joint becomes hot, red, and swollen with high fever, which can indicate acute septic arthritis.'
    ]
];

$categories = ['All', 'General', 'Respiratory', 'Digestive', 'Neurological', 'Urinary', 'Cardiovascular', 'Endocrine', 'Musculoskeletal'];
?>

<div class="row py-3">
    <div class="col-lg-12 text-center mb-4">
        <span class="badge hero-badge px-3 py-2 rounded-pill fw-bold mb-2">CLINICAL DIRECTORY</span>
        <h1 class="display-5 fw-extrabold mb-2">Interactive Symptoms Guide & Clinical Index</h1>
        <p class="lead text-muted mx-auto" style="max-width: 780px;">
            Explore our clinically organized index of symptoms aligned directly with our machine learning classification model. Search, filter by body system, and seamlessly load symptoms into our AI diagnostic checker.
        </p>
    </div>
</div>

<!-- Search and Category Filter Toolbar -->
<div class="card-custom p-4 mb-4">
    <div class="row g-3 align-items-center">
        <div class="col-lg-5">
            <div class="input-group">
                <span class="input-group-text bg-card-subtle text-info border">
                    <i class="bi bi-search"></i>
                </span>
                <input 
                    type="text" 
                    id="symptomSearchInput" 
                    class="form-control" 
                    placeholder="Search symptoms by name, description, or disease..."
                    autocomplete="off"
                >
            </div>
        </div>
        <div class="col-lg-7">
            <div class="d-flex flex-wrap gap-2 justify-content-lg-end" id="categoryFilterContainer">
                <?php foreach ($categories as $idx => $cat): ?>
                    <button 
                        type="button" 
                        class="btn btn-sm symptom-filter-pill <?= $idx === 0 ? 'active btn-info text-white fw-bold' : 'btn-outline-secondary' ?>"
                        data-category="<?= strtolower($cat) ?>"
                    >
                        <?= sanitize($cat) ?>
                    </button>
                <?php endforeach; ?>
            </div>
        </div>
    </div>
</div>

<!-- Symptoms Grid -->
<div class="row g-4" id="symptomsGuideGrid">
    <?php foreach ($symptom_guide_data as $s): ?>
        <div class="col-md-6 col-lg-4 symptom-guide-card" 
             data-name="<?= strtolower($s['name']) ?>" 
             data-category="<?= strtolower($s['category']) ?>" 
             data-desc="<?= strtolower($s['explanation'] . ' ' . $s['conditions']) ?>">
            <div class="card-custom p-4 h-100 d-flex flex-column justify-content-between">
                <div>
                    <div class="d-flex justify-content-between align-items-start mb-3">
                        <div class="p-3 bg-info bg-opacity-10 text-info rounded-circle">
                            <i class="bi <?= $s['icon'] ?> fs-4"></i>
                        </div>
                        <span class="badge bg-secondary bg-opacity-25 text-info border border-info border-opacity-25">
                            <?= sanitize($s['category']) ?>
                        </span>
                    </div>

                    <h5 class="fw-bold mb-2"><?= sanitize($s['name']) ?></h5>
                    <p class="small text-muted mb-3" style="line-height: 1.6;">
                        <?= sanitize($s['explanation']) ?>
                    </p>

                    <div class="mb-3 p-2 bg-card-subtle rounded border small">
                        <strong class="text-primary-theme d-block mb-1">
                            <i class="bi bi-diagram-3-fill text-info me-1"></i> Commonly Associated:
                        </strong>
                        <span class="text-muted"><?= sanitize($s['conditions']) ?></span>
                    </div>

                    <div class="mb-3 p-2 bg-warning bg-opacity-10 rounded border border-warning border-opacity-25 small">
                        <strong class="text-warning d-block mb-1">
                            <i class="bi bi-shield-check me-1"></i> When to Seek Evaluation:
                        </strong>
                        <span class="text-muted"><?= sanitize($s['when_to_seek']) ?></span>
                    </div>
                </div>

                <div class="pt-3 border-top mt-2">
                    <a href="prediction.php?symptom=<?= urlencode($s['key']) ?>" class="btn btn-sm btn-outline-info rounded-pill w-100 py-2 fw-semibold">
                        <i class="bi bi-cpu-fill me-1"></i> Use this symptom in AI checker
                    </a>
                </div>
            </div>
        </div>
    <?php endforeach; ?>
</div>

<!-- Empty Search Fallback -->
<div id="symptomsEmptySearch" class="card-custom p-5 text-center my-4" style="display: none;">
    <i class="bi bi-search text-muted display-4 mb-3"></i>
    <h4 class="fw-bold">No Matching Symptoms Found</h4>
    <p class="text-muted small mb-3">Try adjusting your search terms or select "All" from the body system filters above.</p>
    <button type="button" class="btn btn-outline-info rounded-pill px-4" onclick="document.getElementById('symptomSearchInput').value=''; document.querySelector('[data-category=all]').click();">
        Reset Search & Filters
    </button>
</div>

<div class="disclaimer-banner my-5 text-start p-4">
    <h5 class="fw-bold mb-2 text-warning"><i class="bi bi-info-circle-fill me-2"></i> Clinical Reference Note</h5>
    <p class="small text-muted mb-0">
        Symptoms are non-specific indicators and can arise from multiple independent or interacting physiological mechanisms. One symptom alone does not diagnose a clinical disease. Always discuss persistent or concerning symptoms with a licensed healthcare provider.
    </p>
</div>

<?php
require_once __DIR__ . '/includes/footer.php';
?>
