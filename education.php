<?php
require_once __DIR__ . '/includes/functions.php';
$page_title = 'MediSense AI | Health Education Hub';
require_once __DIR__ . '/includes/header.php';
?>

<div class="container py-4">
    <!-- Breadcrumb & Header -->
    <nav aria-label="breadcrumb" class="mb-3">
        <ol class="breadcrumb">
            <li class="breadcrumb-item"><a href="index.php" class="text-decoration-none text-info">Home</a></li>
            <li class="breadcrumb-item"><a href="diseases.php" class="text-decoration-none text-info">Health Library</a></li>
            <li class="breadcrumb-item active" aria-current="page">Health Education Hub</li>
        </ol>
    </nav>

    <div class="row align-items-center mb-5">
        <div class="col-lg-8">
            <span class="badge hero-badge px-3 py-2 rounded-pill fw-bold mb-2">
                <i class="bi bi-book-half me-1"></i> EVIDENCE-BASED LEARNING
            </span>
            <h1 class="display-5 fw-extrabold mb-2">Health Education Hub</h1>
            <p class="lead text-muted mb-0">
                Explore verified medical articles, terminology glossaries, debunked health myths, and guides on how artificial intelligence is transforming clinical care.
            </p>
        </div>
        <div class="col-lg-4 text-lg-end mt-3 mt-lg-0">
            <div class="d-inline-flex align-items-center gap-2 px-3 py-2 rounded-3 border bg-card-subtle">
                <i class="bi bi-patch-check-fill text-info fs-4"></i>
                <div class="text-start">
                    <div class="fw-bold small">Clinical Advisory Board Reviewed</div>
                    <div class="text-muted" style="font-size: 0.75rem;">Updated Q3 2026 Guidelines</div>
                </div>
            </div>
        </div>
    </div>

    <!-- Search & Topic Filter -->
    <div class="card-custom p-4 mb-5">
        <div class="row g-3 align-items-center">
            <div class="col-lg-6">
                <div class="input-group">
                    <span class="input-group-text bg-card-subtle text-info border">
                        <i class="bi bi-search"></i>
                    </span>
                    <input 
                        type="text" 
                        id="eduSearchInput" 
                        class="form-control" 
                        placeholder="Search articles, medical terms, FAQs, or myths..."
                        autocomplete="off"
                    >
                </div>
            </div>
            <div class="col-lg-6">
                <ul class="nav nav-pills justify-content-lg-end gap-2" id="eduNavTabs" role="tablist">
                    <li class="nav-item">
                        <button class="nav-link active rounded-pill px-3 py-2 fw-semibold" id="tab-articles" data-bs-toggle="pill" data-bs-target="#content-articles" type="button">
                            <i class="bi bi-journal-text me-1"></i> Articles
                        </button>
                    </li>
                    <li class="nav-item">
                        <button class="nav-link rounded-pill px-3 py-2 fw-semibold" id="tab-myths" data-bs-toggle="pill" data-bs-target="#content-myths" type="button">
                            <i class="bi bi-lightbulb me-1"></i> Myth vs Fact
                        </button>
                    </li>
                    <li class="nav-item">
                        <button class="nav-link rounded-pill px-3 py-2 fw-semibold" id="tab-terms" data-bs-toggle="pill" data-bs-target="#content-terms" type="button">
                            <i class="bi bi-translate me-1"></i> Terminology
                        </button>
                    </li>
                    <li class="nav-item">
                        <button class="nav-link rounded-pill px-3 py-2 fw-semibold" id="tab-faqs" data-bs-toggle="pill" data-bs-target="#content-faqs" type="button">
                            <i class="bi bi-question-circle me-1"></i> FAQs
                        </button>
                    </li>
                    <li class="nav-item">
                        <button class="nav-link rounded-pill px-3 py-2 fw-semibold" id="tab-ai" data-bs-toggle="pill" data-bs-target="#content-ai" type="button">
                            <i class="bi bi-cpu me-1"></i> AI in Health
                        </button>
                    </li>
                </ul>
            </div>
        </div>
    </div>

    <!-- Tab Contents -->
    <div class="tab-content" id="eduTabContent">

        <!-- 1. HEALTH ARTICLES & LIFESTYLE -->
        <div class="tab-pane fade show active" id="content-articles" role="tabpanel">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h3 class="fw-bold mb-0"><i class="bi bi-journal-medical text-info me-2"></i> Featured Health & Lifestyle Articles</h3>
                <span class="text-muted small">8 Articles Published</span>
            </div>

            <div class="row g-4" id="articlesGrid">
                <!-- Article 1 -->
                <div class="col-md-6 col-lg-4 edu-item" data-search="blood pressure cardiovascular hypertension lifestyle sodium exercise heart">
                    <div class="card-custom h-100 d-flex flex-column p-4">
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <span class="badge bg-danger bg-opacity-10 text-danger border border-danger border-opacity-25 px-2 py-1">Cardiovascular</span>
                            <span class="text-muted small"><i class="bi bi-clock me-1"></i> 5 min read</span>
                        </div>
                        <h5 class="fw-bold mb-2">Understanding Blood Pressure: The Silent Biomarker</h5>
                        <p class="text-muted small flex-grow-1">
                            High blood pressure often produces zero visible symptoms until vascular damage has occurred. Learn how systolic and diastolic readings work, the DASH diet, and daily habits that keep arteries flexible.
                        </p>
                        <div class="pt-3 border-top mt-3 d-flex justify-content-between align-items-center">
                            <span class="badge bg-card-subtle text-info border">Hypertension Guide</span>
                            <a href="diseases.php?search=hypertension" class="btn btn-sm btn-outline-info rounded-pill px-3">Explore Disease</a>
                        </div>
                    </div>
                </div>

                <!-- Article 2 -->
                <div class="col-md-6 col-lg-4 edu-item" data-search="insulin resistance diabetes metabolic glucose hba1c nutrition sugar">
                    <div class="card-custom h-100 d-flex flex-column p-4">
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <span class="badge bg-warning bg-opacity-10 text-warning border border-warning border-opacity-25 px-2 py-1">Metabolic Health</span>
                            <span class="text-muted small"><i class="bi bi-clock me-1"></i> 6 min read</span>
                        </div>
                        <h5 class="fw-bold mb-2">Insulin Resistance: Early Signs and Dietary Interventions</h5>
                        <p class="text-muted small flex-grow-1">
                            Before Type 2 Diabetes is clinically detected on fasting tests, insulin sensitivity begins declining years earlier. Understand postprandial glucose spikes, dietary fiber, and resistance training benefits.
                        </p>
                        <div class="pt-3 border-top mt-3 d-flex justify-content-between align-items-center">
                            <span class="badge bg-card-subtle text-info border">Metabolic Screening</span>
                            <a href="risk_calculator.php" class="btn btn-sm btn-outline-info rounded-pill px-3">Check Risk</a>
                        </div>
                    </div>
                </div>

                <!-- Article 3 -->
                <div class="col-md-6 col-lg-4 edu-item" data-search="sleep circadian rhythm rem deep sleep immune memory insomnia cortisol">
                    <div class="card-custom h-100 d-flex flex-column p-4">
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <span class="badge bg-primary bg-opacity-10 text-primary border border-primary border-opacity-25 px-2 py-1">Sleep Science</span>
                            <span class="text-muted small"><i class="bi bi-clock me-1"></i> 4 min read</span>
                        </div>
                        <h5 class="fw-bold mb-2">The Architecture of Rest: How Sleep Cleans the Brain</h5>
                        <p class="text-muted small flex-grow-1">
                            During deep slow-wave sleep, the glymphatic system flushes metabolic byproducts from the cerebral cortex. Discover how sleep timing, bedroom temperature, and morning sunlight align your internal clock.
                        </p>
                        <div class="pt-3 border-top mt-3 d-flex justify-content-between align-items-center">
                            <span class="badge bg-card-subtle text-info border">Restorative Sleep</span>
                            <a href="prevention.php#sleep" class="btn btn-sm btn-outline-info rounded-pill px-3">Sleep Protocols</a>
                        </div>
                    </div>
                </div>

                <!-- Article 4 -->
                <div class="col-md-6 col-lg-4 edu-item" data-search="gut microbiome fiber fermented digestion ibs mental health axis probiotics">
                    <div class="card-custom h-100 d-flex flex-column p-4">
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <span class="badge bg-success bg-opacity-10 text-success border border-success border-opacity-25 px-2 py-1">Digestive Health</span>
                            <span class="text-muted small"><i class="bi bi-clock me-1"></i> 7 min read</span>
                        </div>
                        <h5 class="fw-bold mb-2">The Gut-Brain Axis: Microbes and Systemic Vitality</h5>
                        <p class="text-muted small flex-grow-1">
                            Over 90% of the body's serotonin receptors reside in the enteric nervous system. Explore how dietary diversity, prebiotic fibers, and limiting ultra-processed additives support intestinal barrier integrity.
                        </p>
                        <div class="pt-3 border-top mt-3 d-flex justify-content-between align-items-center">
                            <span class="badge bg-card-subtle text-info border">Microbiome</span>
                            <a href="diseases.php?search=gerd" class="btn btn-sm btn-outline-info rounded-pill px-3">Digestive Care</a>
                        </div>
                    </div>
                </div>

                <!-- Article 5 -->
                <div class="col-md-6 col-lg-4 edu-item" data-search="stress chronic cortisol nervous system vagus nerve breathing burnout">
                    <div class="card-custom h-100 d-flex flex-column p-4">
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <span class="badge bg-info bg-opacity-10 text-info border border-info border-opacity-25 px-2 py-1">Mental Wellbeing</span>
                            <span class="text-muted small"><i class="bi bi-clock me-1"></i> 5 min read</span>
                        </div>
                        <h5 class="fw-bold mb-2">Physiology of Stress: From Acute Alarm to Chronic Burnout</h5>
                        <p class="text-muted small flex-grow-1">
                            Sustained cortisol elevation elevates baseline systemic inflammation, disrupts blood sugar balance, and dampens cellular immunity. Learn physiologic sigh breathing and down-regulation practices.
                        </p>
                        <div class="pt-3 border-top mt-3 d-flex justify-content-between align-items-center">
                            <span class="badge bg-card-subtle text-info border">Stress Mastery</span>
                            <a href="prevention.php#stress" class="btn btn-sm btn-outline-info rounded-pill px-3">Prevention</a>
                        </div>
                    </div>
                </div>

                <!-- Article 6 -->
                <div class="col-md-6 col-lg-4 edu-item" data-search="skin cancer uv spf sunscreen melanoma basal cell actinic dermatology">
                    <div class="card-custom h-100 d-flex flex-column p-4">
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <span class="badge bg-warning bg-opacity-10 text-warning border border-warning border-opacity-25 px-2 py-1">Dermatology</span>
                            <span class="text-muted small"><i class="bi bi-clock me-1"></i> 5 min read</span>
                        </div>
                        <h5 class="fw-bold mb-2">Skin Cancer Prevention: Decoding UV Radiation and ABCDEs</h5>
                        <p class="text-muted small flex-grow-1">
                            Ultraviolet rays cause cumulative DNA photo-damage leading to non-melanoma and melanoma skin malignancies. Discover the ABCDE criteria for mole surveillance and optimal broad-spectrum photoprotection.
                        </p>
                        <div class="pt-3 border-top mt-3 d-flex justify-content-between align-items-center">
                            <span class="badge bg-card-subtle text-info border">Skin Vigilance</span>
                            <a href="diseases.php?search=melanoma" class="btn btn-sm btn-outline-info rounded-pill px-3">Skin Library</a>
                        </div>
                    </div>
                </div>

                <!-- Article 7 -->
                <div class="col-md-6 col-lg-4 edu-item" data-search="respiratory asthma copd clean air particulate matter lungs bronchitis">
                    <div class="card-custom h-100 d-flex flex-column p-4">
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <span class="badge bg-info bg-opacity-10 text-info border border-info border-opacity-25 px-2 py-1">Pulmonology</span>
                            <span class="text-muted small"><i class="bi bi-clock me-1"></i> 4 min read</span>
                        </div>
                        <h5 class="fw-bold mb-2">Protecting Lung Capacity: Environmental Air Quality & Defense</h5>
                        <p class="text-muted small flex-grow-1">
                            Inhaled fine particulate matter (PM2.5) bypasses upper nasal filtration to trigger bronchial hyper-reactivity. Review HEPA filtration, exercise air timing, and early spirometry assessment value.
                        </p>
                        <div class="pt-3 border-top mt-3 d-flex justify-content-between align-items-center">
                            <span class="badge bg-card-subtle text-info border">Lung Health</span>
                            <a href="diseases.php?search=asthma" class="btn btn-sm btn-outline-info rounded-pill px-3">Respiratory Guide</a>
                        </div>
                    </div>
                </div>

                <!-- Article 8 -->
                <div class="col-md-6 col-lg-4 edu-item" data-search="longevity hydration kidney electrolytes hydration urine color water">
                    <div class="card-custom h-100 d-flex flex-column p-4">
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <span class="badge bg-primary bg-opacity-10 text-primary border border-primary border-opacity-25 px-2 py-1">Renal & Hydration</span>
                            <span class="text-muted small"><i class="bi bi-clock me-1"></i> 3 min read</span>
                        </div>
                        <h5 class="fw-bold mb-2">Cellular Hydration: Electrolyte Equilibrium Beyond Plain Water</h5>
                        <p class="text-muted small flex-grow-1">
                            Effective fluid transport into cells relies on balanced sodium, potassium, and magnesium osmolality. Learn how to interpret urine color charts and avoid acute hyponatremia or dehydration.
                        </p>
                        <div class="pt-3 border-top mt-3 d-flex justify-content-between align-items-center">
                            <span class="badge bg-card-subtle text-info border">Kidney Vitality</span>
                            <a href="prevention.php#hydration" class="btn btn-sm btn-outline-info rounded-pill px-3">Hydration Tips</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 2. MYTH VS FACT INTERACTIVE CARDS -->
        <div class="tab-pane fade" id="content-myths" role="tabpanel">
            <div class="mb-4">
                <h3 class="fw-bold mb-1"><i class="bi bi-lightbulb-fill text-warning me-2"></i> Medical Myth vs Clinical Fact</h3>
                <p class="text-muted small">Click any card to reveal the evidence-based clinical reality.</p>
            </div>

            <div class="row g-4" id="mythsGrid">
                <!-- Myth 1 -->
                <div class="col-md-6 edu-item" data-search="sugar diabetes myth fact eating sweets causes diabetes">
                    <div class="card-custom p-4 h-100 border-start border-4 border-warning">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <span class="badge bg-danger bg-opacity-10 text-danger border border-danger border-opacity-25 fw-bold px-3 py-1">COMMON MYTH</span>
                            <i class="bi bi-x-circle-fill text-danger fs-4"></i>
                        </div>
                        <h5 class="fw-bold mb-2">"Eating sugar directly causes diabetes."</h5>
                        <div class="p-3 rounded-3 bg-card-subtle border mb-3">
                            <div class="fw-bold text-success mb-1"><i class="bi bi-check-circle-fill me-1"></i> Clinical Reality:</div>
                            <p class="small text-muted mb-0">
                                While excess simple sugars contribute to caloric surplus, hepatic fat accumulation, and weight gain, Type 2 diabetes is caused by complex insulin receptor resistance, pancreatic beta-cell fatigue, and genetic predisposition. Type 1 diabetes is an autoimmune destruction of beta cells unrelated to diet.
                            </p>
                        </div>
                    </div>
                </div>

                <!-- Myth 2 -->
                <div class="col-md-6 edu-item" data-search="cold weather flu myth fact getting cold causes pneumonia">
                    <div class="card-custom p-4 h-100 border-start border-4 border-warning">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <span class="badge bg-danger bg-opacity-10 text-danger border border-danger border-opacity-25 fw-bold px-3 py-1">COMMON MYTH</span>
                            <i class="bi bi-x-circle-fill text-danger fs-4"></i>
                        </div>
                        <h5 class="fw-bold mb-2">"Going outside with wet hair or in cold weather gives you the flu."</h5>
                        <div class="p-3 rounded-3 bg-card-subtle border mb-3">
                            <div class="fw-bold text-success mb-1"><i class="bi bi-check-circle-fill me-1"></i> Clinical Reality:</div>
                            <p class="small text-muted mb-0">
                                Respiratory infections are caused exclusively by microbial pathogens (such as influenza virus, rhinovirus, or SARS-CoV-2), not chilly air. Cold weather increases infection rates because people gather in poorly ventilated indoor spaces, and dry winter air can slightly thin the nasal mucosal barrier.
                            </p>
                        </div>
                    </div>
                </div>

                <!-- Myth 3 -->
                <div class="col-md-6 edu-item" data-search="antibiotics viral cold flu myth fact kills virus">
                    <div class="card-custom p-4 h-100 border-start border-4 border-warning">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <span class="badge bg-danger bg-opacity-10 text-danger border border-danger border-opacity-25 fw-bold px-3 py-1">COMMON MYTH</span>
                            <i class="bi bi-x-circle-fill text-danger fs-4"></i>
                        </div>
                        <h5 class="fw-bold mb-2">"Antibiotics cure severe colds and bronchitis."</h5>
                        <div class="p-3 rounded-3 bg-card-subtle border mb-3">
                            <div class="fw-bold text-success mb-1"><i class="bi bi-check-circle-fill me-1"></i> Clinical Reality:</div>
                            <p class="small text-muted mb-0">
                                Antibiotics kill bacteria exclusively and have absolutely zero effect against viral organisms. Taking antibiotics for viral colds or uncomplicated acute bronchitis destroys beneficial gut microbes and directly accelerates antibiotic-resistant superbugs.
                            </p>
                        </div>
                    </div>
                </div>

                <!-- Myth 4 -->
                <div class="col-md-6 edu-item" data-search="blood pressure headache hypertension symptoms myth fact silent">
                    <div class="card-custom p-4 h-100 border-start border-4 border-warning">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <span class="badge bg-danger bg-opacity-10 text-danger border border-danger border-opacity-25 fw-bold px-3 py-1">COMMON MYTH</span>
                            <i class="bi bi-x-circle-fill text-danger fs-4"></i>
                        </div>
                        <h5 class="fw-bold mb-2">"You will feel a headache or dizziness if your blood pressure is high."</h5>
                        <div class="p-3 rounded-3 bg-card-subtle border mb-3">
                            <div class="fw-bold text-success mb-1"><i class="bi bi-check-circle-fill me-1"></i> Clinical Reality:</div>
                            <p class="small text-muted mb-0">
                                Hypertension is clinically coined "The Silent Killer" because millions of individuals walk around with dangerously elevated readings (e.g. 150/95 mmHg) feeling completely energetic. Routine sphygmomanometer measurement is the only reliable detection tool.
                            </p>
                        </div>
                    </div>
                </div>

                <!-- Myth 5 -->
                <div class="col-md-6 edu-item" data-search="cracking knuckles arthritis joints bones myth fact">
                    <div class="card-custom p-4 h-100 border-start border-4 border-warning">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <span class="badge bg-danger bg-opacity-10 text-danger border border-danger border-opacity-25 fw-bold px-3 py-1">COMMON MYTH</span>
                            <i class="bi bi-x-circle-fill text-danger fs-4"></i>
                        </div>
                        <h5 class="fw-bold mb-2">"Cracking your knuckles causes arthritis in your hands."</h5>
                        <div class="p-3 rounded-3 bg-card-subtle border mb-3">
                            <div class="fw-bold text-success mb-1"><i class="bi bi-check-circle-fill me-1"></i> Clinical Reality:</div>
                            <p class="small text-muted mb-0">
                                The popping sound comes from gas bubbles collapsing within the synovial fluid of the joint capsule when negative pressure is created. Long-term observational studies show knuckle crackers do not have higher rates of osteoarthritis compared to non-crackers.
                            </p>
                        </div>
                    </div>
                </div>

                <!-- Myth 6 -->
                <div class="col-md-6 edu-item" data-search="sunscreen clouds shade winter uv melanoma skin myth fact">
                    <div class="card-custom p-4 h-100 border-start border-4 border-warning">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <span class="badge bg-danger bg-opacity-10 text-danger border border-danger border-opacity-25 fw-bold px-3 py-1">COMMON MYTH</span>
                            <i class="bi bi-x-circle-fill text-danger fs-4"></i>
                        </div>
                        <h5 class="fw-bold mb-2">"You don't need sunscreen on cloudy or overcast days."</h5>
                        <div class="p-3 rounded-3 bg-card-subtle border mb-3">
                            <div class="fw-bold text-success mb-1"><i class="bi bi-check-circle-fill me-1"></i> Clinical Reality:</div>
                            <p class="small text-muted mb-0">
                                Up to 80% of ultraviolet A (UVA) rays penetrate directly through dense cloud cover and window glass. UVA rays penetrate into deep dermal layers, degrading collagen and creating cellular mutations that induce skin malignancies regardless of visible sunshine.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 3. MEDICAL TERMINOLOGY GLOSSARY -->
        <div class="tab-pane fade" id="content-terms" role="tabpanel">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <div>
                    <h3 class="fw-bold mb-1"><i class="bi bi-translate text-info me-2"></i> Clinical Terminology Glossary</h3>
                    <p class="text-muted small mb-0">Understand common medical terms, lab markers, and diagnostic abbreviations.</p>
                </div>
                <div class="d-none d-md-flex gap-1" id="glossaryLetterNav">
                    <!-- Letter filters dynamically or statically -->
                    <span class="badge bg-info text-white px-2 py-1">A-Z Directory</span>
                </div>
            </div>

            <div class="row g-3" id="glossaryGrid">
                <!-- Term 1 -->
                <div class="col-md-6 edu-item" data-search="arrhythmia heart rhythm tachycardia bradycardia flutter">
                    <div class="card-custom p-3 h-100">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <h6 class="fw-bold text-info mb-0">Arrhythmia</h6>
                            <span class="badge bg-card-subtle text-muted border">Cardiology</span>
                        </div>
                        <p class="small text-muted mb-0">
                            An irregularity in the rhythm or rate of the heartbeat caused by disruptions in the cardiac electrical conduction pathway. May manifest as tachycardia (abnormally rapid), bradycardia (abnormally slow), or fibrillation.
                        </p>
                    </div>
                </div>

                <!-- Term 2 -->
                <div class="col-md-6 edu-item" data-search="biomarker biological marker blood test diagnostic psa hba1c troponin">
                    <div class="card-custom p-3 h-100">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <h6 class="fw-bold text-info mb-0">Biomarker</h6>
                            <span class="badge bg-card-subtle text-muted border">Diagnostics</span>
                        </div>
                        <p class="small text-muted mb-0">
                            A measurable indicator of the severity or presence of some disease state or physiological condition (e.g., HbA1c for glucose regulation, troponin for myocardial necrosis, or CRP for systemic inflammation).
                        </p>
                    </div>
                </div>

                <!-- Term 3 -->
                <div class="col-md-6 edu-item" data-search="dyspnea shortness of breath breathing difficulty asthma copd">
                    <div class="card-custom p-3 h-100">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <h6 class="fw-bold text-info mb-0">Dyspnea</h6>
                            <span class="badge bg-card-subtle text-muted border">Pulmonology</span>
                        </div>
                        <p class="small text-muted mb-0">
                            The clinical term for difficult, labored, or uncomfortable breathing; a subjective experience of breathing discomfort that consists of qualitatively distinct sensations that vary in intensity.
                        </p>
                    </div>
                </div>

                <!-- Term 4 -->
                <div class="col-md-6 edu-item" data-search="hba1c glycated hemoglobin diabetes blood sugar 3 month average">
                    <div class="card-custom p-3 h-100">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <h6 class="fw-bold text-info mb-0">HbA1c (Glycated Hemoglobin)</h6>
                            <span class="badge bg-card-subtle text-muted border">Endocrinology</span>
                        </div>
                        <p class="small text-muted mb-0">
                            A laboratory blood test measuring the percentage of hemoglobin molecules in red blood cells that have bonded with glucose. Reflects average circulating blood glucose over the preceding 2 to 3 months.
                        </p>
                    </div>
                </div>

                <!-- Term 5 -->
                <div class="col-md-6 edu-item" data-search="hypertension high blood pressure systolic diastolic 130 80">
                    <div class="card-custom p-3 h-100">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <h6 class="fw-bold text-info mb-0">Hypertension</h6>
                            <span class="badge bg-card-subtle text-muted border">Cardiology</span>
                        </div>
                        <p class="small text-muted mb-0">
                            Sustained elevation of systemic arterial blood pressure, clinically defined in adults as systolic BP &ge; 130 mmHg or diastolic BP &ge; 80 mmHg on repeated clinical visits.
                        </p>
                    </div>
                </div>

                <!-- Term 6 -->
                <div class="col-md-6 edu-item" data-search="ischemia reduced blood flow oxygen tissue heart brain stroke">
                    <div class="card-custom p-3 h-100">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <h6 class="fw-bold text-info mb-0">Ischemia</h6>
                            <span class="badge bg-card-subtle text-muted border">Pathophysiology</span>
                        </div>
                        <p class="small text-muted mb-0">
                            An inadequate blood supply to an organ or part of the body, especially the heart muscles (myocardial ischemia) or brain (cerebral ischemia), resulting in localized cellular hypoxia.
                        </p>
                    </div>
                </div>

                <!-- Term 7 -->
                <div class="col-md-6 edu-item" data-search="sepsis systemic infection immune response organ failure emergency">
                    <div class="card-custom p-3 h-100">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <h6 class="fw-bold text-info mb-0">Sepsis</h6>
                            <span class="badge bg-card-subtle text-muted border">Critical Care</span>
                        </div>
                        <p class="small text-muted mb-0">
                            A life-threatening medical emergency caused by the body's dysregulated, systemic inflammatory response to an infection, leading to widespread tissue damage, hypotension, and multiorgan failure.
                        </p>
                    </div>
                </div>

                <!-- Term 8 -->
                <div class="col-md-6 edu-item" data-search="pruritus itching skin dermatitis urticaria rash">
                    <div class="card-custom p-3 h-100">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <h6 class="fw-bold text-info mb-0">Pruritus</h6>
                            <span class="badge bg-card-subtle text-muted border">Dermatology</span>
                        </div>
                        <p class="small text-muted mb-0">
                            Severe itching of the skin, mediated by histamine, substance P, and non-histaminergic nerve pathways. A primary feature of eczema, urticaria, cholestasis, and contact dermatitis.
                        </p>
                    </div>
                </div>
            </div>
        </div>

        <!-- 4. FREQUENTLY ASKED QUESTIONS (FAQS) -->
        <div class="tab-pane fade" id="content-faqs" role="tabpanel">
            <div class="mb-4">
                <h3 class="fw-bold mb-1"><i class="bi bi-question-circle-fill text-info me-2"></i> Frequently Asked Medical & Screening Questions</h3>
                <p class="text-muted small">Answers to common clinical, preventative, and diagnostic inquiries.</p>
            </div>

            <div class="accordion" id="faqAccordion">
                <!-- FAQ 1 -->
                <div class="accordion-item card-custom mb-3 border-0 edu-item" data-search="how often doctor routine checkup screening blood test physical">
                    <h2 class="accordion-header" id="headingFaq1">
                        <button class="accordion-button collapsed bg-transparent fw-bold" type="button" data-bs-toggle="collapse" data-bs-target="#collapseFaq1">
                            How often should healthy adults undergo routine blood screenings?
                        </button>
                    </h2>
                    <div id="collapseFaq1" class="accordion-collapse collapse" data-bs-parent="#faqAccordion">
                        <div class="accordion-body text-muted small pt-0">
                            Generally, adults aged 18 to 39 with normal blood pressure and no chronic disease indicators benefit from a comprehensive wellness checkup and lipid panel every 3 to 5 years. Adults 40 and older, or those with family histories of diabetes, cardiovascular events, or renal conditions, should undergo annual comprehensive metabolic panels, lipid testing, and blood pressure surveillance.
                        </div>
                    </div>
                </div>

                <!-- FAQ 2 -->
                <div class="accordion-item card-custom mb-3 border-0 edu-item" data-search="bmi limitation muscle fat athlete health risk calculator">
                    <h2 class="accordion-header" id="headingFaq2">
                        <button class="accordion-button collapsed bg-transparent fw-bold" type="button" data-bs-toggle="collapse" data-bs-target="#collapseFaq2">
                            What are the clinical limitations of Body Mass Index (BMI)?
                        </button>
                    </h2>
                    <div id="collapseFaq2" class="accordion-collapse collapse" data-bs-parent="#faqAccordion">
                        <div class="accordion-body text-muted small pt-0">
                            Body Mass Index calculates weight divided by height squared, but cannot differentiate between lean skeletal muscle mass and visceral adipose tissue. Highly muscular athletes may be categorized as "overweight" while possessing optimal metabolic markers. Clinicians utilize waist-to-hip ratio, DEXA body composition, and blood biomarker panels alongside BMI for accurate risk assessment.
                        </div>
                    </div>
                </div>

                <!-- FAQ 3 -->
                <div class="accordion-item card-custom mb-3 border-0 edu-item" data-search="fever when see doctor temperature children adults emergency">
                    <h2 class="accordion-header" id="headingFaq3">
                        <button class="accordion-button collapsed bg-transparent fw-bold" type="button" data-bs-toggle="collapse" data-bs-target="#collapseFaq3">
                            At what temperature does a fever become medically dangerous?
                        </button>
                    </h2>
                    <div id="collapseFaq3" class="accordion-collapse collapse" data-bs-parent="#faqAccordion">
                        <div class="accordion-body text-muted small pt-0">
                            In healthy adults, temperatures up to 102°F (38.9°C) are typically a beneficial immune response fighting microbial pathogens. Immediate medical attention is warranted if adult fever exceeds 103°F (39.4°C), lasts more than 72 hours continuously, or occurs with a stiff neck, mental confusion, or difficulty breathing. In infants under 3 months, any rectal temperature &ge; 100.4°F (38.0°C) is an immediate medical emergency.
                        </div>
                    </div>
                </div>

                <!-- FAQ 4 -->
                <div class="accordion-item card-custom mb-3 border-0 edu-item" data-search="water daily ounces liters hydration kidney rule">
                    <h2 class="accordion-header" id="headingFaq4">
                        <button class="accordion-button collapsed bg-transparent fw-bold" type="button" data-bs-toggle="collapse" data-bs-target="#collapseFaq4">
                            Is the "8 glasses of water a day" rule clinically accurate?
                        </button>
                    </h2>
                    <div id="collapseFaq4" class="accordion-collapse collapse" data-bs-parent="#faqAccordion">
                        <div class="accordion-body text-muted small pt-0">
                            The "8x8 rule" is an arbitrary guideline. Real physiological fluid requirements vary based on body mass, ambient climate, sweat rates, diet, and renal function. The US National Academies recommend approximately 3.7 liters (125 oz) total water intake for men and 2.7 liters (91 oz) for women daily from all beverages and moisture-rich foods combined. Observing pale, light-straw-colored urine is the best personal indicator of adequate hydration.
                        </div>
                    </div>
                </div>

                <!-- FAQ 5 -->
                <div class="accordion-item card-custom mb-3 border-0 edu-item" data-search="ai replace doctor medisense diagnosis algorithm machine learning">
                    <h2 class="accordion-header" id="headingFaq5">
                        <button class="accordion-button collapsed bg-transparent fw-bold" type="button" data-bs-toggle="collapse" data-bs-target="#collapseFaq5">
                            Can MediSense AI or machine learning replace my primary physician?
                        </button>
                    </h2>
                    <div id="collapseFaq5" class="accordion-collapse collapse" data-bs-parent="#faqAccordion">
                        <div class="accordion-body text-muted small pt-0">
                            No. MediSense AI is engineered strictly as an educational triage and risk stratification intelligence system. AI models detect statistical patterns across symptoms and visual textures, but cannot perform physical palpation, listen with stethoscopes, order biopsy pathology, or evaluate nuanced patient social context. Always confirm results with a qualified healthcare provider.
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 5. AI IN HEALTHCARE EDUCATION -->
        <div class="tab-pane fade" id="content-ai" role="tabpanel">
            <div class="mb-4">
                <h3 class="fw-bold mb-1"><i class="bi bi-cpu-fill text-info me-2"></i> Artificial Intelligence in Modern Healthcare</h3>
                <p class="text-muted small">Learn how machine learning models analyze clinical patterns, manage uncertainty, and augment diagnostic accuracy.</p>
            </div>

            <div class="row g-4">
                <div class="col-lg-6">
                    <div class="card-custom p-4 h-100">
                        <div class="d-flex align-items-center gap-3 mb-3">
                            <div class="p-3 bg-info bg-opacity-10 text-info rounded-3">
                                <i class="bi bi-diagram-3-fill fs-3"></i>
                            </div>
                            <div>
                                <h5 class="fw-bold mb-0">Multimodal Pattern Recognition</h5>
                                <span class="text-muted small">Supervised Learning & Neural Embeddings</span>
                            </div>
                        </div>
                        <p class="text-muted small mb-3">
                            Modern clinical AI pairs tabular symptom data with image tensors and clinical biomarker vectors. By analyzing thousands of historical patient profiles simultaneously, ensemble models identify subtle non-linear correlations that human clinicians might overlook during brief consultations.
                        </p>
                        <ul class="list-unstyled small text-muted mb-0">
                            <li class="mb-2"><i class="bi bi-check2 text-info me-2"></i> <strong>Random Forests & Gradient Boosting:</strong> Robust to sparse symptom inputs and high feature collinearity.</li>
                            <li class="mb-2"><i class="bi bi-check2 text-info me-2"></i> <strong>Computer Vision (CNNs):</strong> Segment visual lesions, measuring border irregularity and chromic variance.</li>
                            <li><i class="bi bi-check2 text-info me-2"></i> <strong>Confidence Calibration:</strong> Outputs Bayesian likelihoods rather than rigid binary claims.</li>
                        </ul>
                    </div>
                </div>

                <div class="col-lg-6">
                    <div class="card-custom p-4 h-100">
                        <div class="d-flex align-items-center gap-3 mb-3">
                            <div class="p-3 bg-warning bg-opacity-10 text-warning rounded-3">
                                <i class="bi bi-shield-lock-fill fs-3"></i>
                            </div>
                            <div>
                                <h5 class="fw-bold mb-0">Safety, Bias & The "Human-in-the-Loop"</h5>
                                <span class="text-muted small">Ethical AI Principles in Medicine</span>
                            </div>
                        </div>
                        <p class="text-muted small mb-3">
                            An AI model is only as unbiased as the clinical training cohort it learns from. If skin lesion datasets underrepresent darker Fitzpatrick phototypes, diagnostic accuracy can degrade. MediSense AI adheres to ethical guardrails:
                        </p>
                        <div class="p-3 bg-card-subtle rounded-3 border">
                            <h6 class="fw-bold small text-info mb-1"><i class="bi bi-info-circle-fill me-1"></i> Core Safety Tenet</h6>
                            <p class="small text-muted mb-0" style="font-size: 0.8rem;">
                                AI serves to <strong>augment</strong> human clinical judgment, never circumvent it. A computer does not possess clinical accountability or holistic bedside empathy. Triage scores empower patients to have richer, better-informed dialogues with their doctors.
                            </p>
                        </div>
                    </div>
                </div>

                <div class="col-12">
                    <div class="card-custom p-4 bg-gradient">
                        <div class="row align-items-center">
                            <div class="col-md-8">
                                <h4 class="fw-bold mb-2">Explore the MediSense AI Predictive Architecture</h4>
                                <p class="text-muted small mb-0">
                                    Curious how our 58 clinical symptom inputs correlate with 73 conditions? Explore the interactive AI prediction engine or review our clinical simulator.
                                </p>
                            </div>
                            <div class="col-md-4 text-md-end mt-3 mt-md-0">
                                <a href="prediction.php" class="btn btn-info text-white rounded-pill px-4 py-2 fw-semibold me-2">
                                    <i class="bi bi-cpu-fill me-1"></i> Launch Predictor
                                </a>
                                <a href="simulator.php" class="btn btn-outline-secondary rounded-pill px-3 py-2 fw-semibold">
                                    Simulator
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

    </div>

    <!-- Empty Search State -->
    <div id="eduEmptySearch" class="card-custom p-5 text-center my-4" style="display: none;">
        <i class="bi bi-search text-muted display-4 mb-3"></i>
        <h4 class="fw-bold">No Matching Education Items Found</h4>
        <p class="text-muted small mb-3">Try different keywords or browse our tabs above.</p>
        <button type="button" class="btn btn-outline-info rounded-pill px-4" onclick="document.getElementById('eduSearchInput').value=''; filterEduItems('');">
            Reset Search
        </button>
    </div>

    <!-- Educational Disclaimer -->
    <div class="disclaimer-banner my-5 text-start p-4">
        <h5 class="fw-bold mb-2 text-warning"><i class="bi bi-info-circle-fill me-2"></i> Clinical Education Disclaimer</h5>
        <p class="small text-muted mb-0">
            The health education resources, myth analyses, glossaries, and FAQs provided by MediSense AI are developed for general educational and informational purposes only. This content does not constitute medical advice, diagnosis, or clinical treatment plans. Never disregard professional medical advice or delay seeking it because of something you have read on MediSense AI.
        </p>
    </div>
</div>

<script>
function filterEduItems(query) {
    const q = (query || '').toLowerCase().trim();
    const items = document.querySelectorAll('.edu-item');
    let visibleCount = 0;

    items.forEach(el => {
        const text = (el.getAttribute('data-search') || '') + ' ' + el.textContent.toLowerCase();
        if (!q || text.includes(q)) {
            el.style.display = '';
            visibleCount++;
        } else {
            el.style.display = 'none';
        }
    });

    const emptyBox = document.getElementById('eduEmptySearch');
    if (emptyBox) {
        emptyBox.style.display = (visibleCount === 0 && q.length > 0) ? 'block' : 'none';
    }
}

document.getElementById('eduSearchInput')?.addEventListener('input', function(e) {
    filterEduItems(e.target.value);
});
</script>

<?php
require_once __DIR__ . '/includes/footer.php';
?>
