// ==========================================================================
// MediSense AI Client Application Engine
// Theme Toggle | Symptom Tiles (Matte/Glossy) | Counter Animation | Search
// ==========================================================================

// Global Theme Initializer (prevents FOUC)
(function() {
    const savedTheme = localStorage.getItem('ai_healthcare_theme') || localStorage.getItem('theme');
    const initialTheme = (savedTheme === 'light' || savedTheme === 'dark') ? savedTheme : 'dark';
    document.documentElement.setAttribute('data-theme', initialTheme);
    document.documentElement.setAttribute('data-bs-theme', initialTheme);
})();

document.addEventListener('DOMContentLoaded', function () {
    initThemeToggle();
    initSymptomTiles();
    initCounterAnimations();
    initPredictionFormLoader();
    initSymptomsGuideSearch();
    initAssessmentSwitcher();
    initRangeSliders();
    initGlobalSearch();
});

// ==========================================================================
// 1. Dark / Light Theme Toggle Engine
// ==========================================================================
function initThemeToggle() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
    if (typeof window.applyTheme === 'function') {
        window.applyTheme(currentTheme);
    }

    const toggleBtns = document.querySelectorAll('.theme-toggle-btn, #themeToggleBtn');
    if (!toggleBtns.length) return;

    toggleBtns.forEach(btn => {
        // Prevent duplicate handlers by using a single direct onclick assignment
        btn.removeAttribute('onclick');
        btn.onclick = function (e) {
            if (e) e.preventDefault();
            if (typeof window.toggleSiteTheme === 'function') {
                window.toggleSiteTheme();
            } else {
                const active = document.documentElement.getAttribute('data-theme') || 'dark';
                const next = (active === 'dark') ? 'light' : 'dark';
                document.documentElement.setAttribute('data-theme', next);
                document.documentElement.setAttribute('data-bs-theme', next);
                try {
                    localStorage.setItem('ai_healthcare_theme', next);
                    localStorage.setItem('theme', next);
                } catch(err) {}

                const darkIcon = btn.querySelector('.theme-icon-dark');
                const lightIcon = btn.querySelector('.theme-icon-light');
                const label = btn.querySelector('.theme-text');
                if (next === 'light') {
                    if (darkIcon) darkIcon.classList.add('d-none');
                    if (lightIcon) lightIcon.classList.remove('d-none');
                    if (label) label.textContent = 'Theme';
                    btn.setAttribute('title', 'Switch to dark mode');
                    btn.setAttribute('aria-label', 'Switch to dark mode');
                } else {
                    if (darkIcon) darkIcon.classList.remove('d-none');
                    if (lightIcon) lightIcon.classList.add('d-none');
                    if (label) label.textContent = 'Theme';
                    btn.setAttribute('title', 'Switch to light mode');
                    btn.setAttribute('aria-label', 'Switch to light mode');
                }
            }
        };
    });
}

// ==========================================================================
// 2. Symptom Tiles: Matte (Unselected) to Glossy (Selected)
// ==========================================================================
function initSymptomTiles() {
    const tiles = document.querySelectorAll('.symptom-tile');
    if (!tiles.length) return;

    // Check URL parameters for pre-selected symptoms (e.g. ?symptom=fever)
    const urlParams = new URLSearchParams(window.location.search);
    const preselected = [];
    if (urlParams.has('symptom')) {
        preselected.push(urlParams.get('symptom').trim().toLowerCase());
    }
    urlParams.getAll('symptoms[]').forEach(s => preselected.push(s.trim().toLowerCase()));

    tiles.forEach(tile => {
        const checkbox = tile.querySelector('.symptom-checkbox');
        if (!checkbox) return;

        // Apply pre-selection if URL contains symptom key
        if (preselected.includes(checkbox.value.toLowerCase())) {
            checkbox.checked = true;
        }

        // Synchronize initial state
        if (checkbox.checked) {
            tile.classList.add('selected');
            tile.setAttribute('aria-checked', 'true');
        } else {
            tile.classList.remove('selected');
            tile.setAttribute('aria-checked', 'false');
        }

        // Toggle state function
        function toggleTileState(checked) {
            checkbox.checked = checked;
            if (checked) {
                tile.classList.add('selected');
                tile.setAttribute('aria-checked', 'true');
            } else {
                tile.classList.remove('selected');
                tile.setAttribute('aria-checked', 'false');
            }
        }

        // Click Handler (entire tile is clickable)
        tile.addEventListener('click', function (e) {
            if (e.target !== checkbox) {
                e.preventDefault();
                toggleTileState(!checkbox.checked);
            } else {
                toggleTileState(checkbox.checked);
            }
        });

        // Accessible Keyboard Navigation (Space & Enter)
        tile.addEventListener('keydown', function (e) {
            if (e.key === ' ' || e.key === 'Enter') {
                e.preventDefault();
                toggleTileState(!checkbox.checked);
            }
        });
    });
}

// ==========================================================================
// 3. Digital Upward Number Counter Animation
// ==========================================================================
function animateNumberCounter(element, finalValue, durationMs = 1300) {
    if (!element || isNaN(finalValue)) return;

    const startTime = performance.now();
    const startValue = 0.0;
    const isDecimal = finalValue.toString().includes('.');
    const decimalPlaces = isDecimal ? (finalValue.toString().split('.')[1] || '').length : 1;

    element.classList.add('counter-animating');

    function step(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / durationMs, 1.0);

        // easeOutCubic curve for smooth digital slowing at the top
        const easeProgress = 1 - Math.pow(1 - progress, 3);
        const currentValue = startValue + (finalValue - startValue) * easeProgress;

        element.textContent = currentValue.toFixed(decimalPlaces) + '%';

        if (progress < 1.0) {
            requestAnimationFrame(step);
        } else {
            // Guarantee 100% exact stop at finalValue
            element.textContent = finalValue.toFixed(decimalPlaces) + '%';
            element.classList.remove('counter-animating');
        }
    }

    requestAnimationFrame(step);
}

function initCounterAnimations() {
    const counterElements = document.querySelectorAll('.animate-counter');
    counterElements.forEach(elem => {
        const target = parseFloat(elem.getAttribute('data-target') || elem.textContent.replace('%', '').trim());
        if (!isNaN(target)) {
            elem.textContent = '00.0%';
            setTimeout(() => {
                animateNumberCounter(elem, target, 1200);
            }, 150);
        }
    });
}

// ==========================================================================
// 4. Multi-Step Animated Loader on Prediction Submission
// ==========================================================================
function initPredictionFormLoader() {
    const form = document.querySelector('form.prediction-form, form[action="prediction.php"]');
    if (!form) return;

    const loadingContainer = document.getElementById('ai-loading-state');
    const submitBtn = form.querySelector('button[type="submit"]');

    form.addEventListener('submit', function (e) {
        const checkedSymptoms = form.querySelectorAll('.symptom-checkbox:checked');
        if (checkedSymptoms.length === 0) {
            // Let the backend validate or highlight
            return;
        }

        if (loadingContainer) {
            loadingContainer.style.display = 'block';
            if (submitBtn) {
                submitBtn.setAttribute('disabled', 'disabled');
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Evaluating Diagnostic Model...';
            }

            // Animate through progression steps
            const steps = loadingContainer.querySelectorAll('.loading-step-item');
            if (steps.length >= 4) {
                setTimeout(() => { steps[0].classList.add('completed'); steps[1].classList.add('active'); }, 300);
                setTimeout(() => { steps[1].classList.add('completed'); steps[2].classList.add('active'); }, 700);
                setTimeout(() => { steps[2].classList.add('completed'); steps[3].classList.add('active'); }, 1100);
            }
        }
    });
}

// ==========================================================================
// 5. Symptoms Guide Live Search & Category Filtering
// ==========================================================================
function initSymptomsGuideSearch() {
    const searchInput = document.getElementById('symptomSearchInput');
    const filterPills = document.querySelectorAll('.symptom-filter-pill');
    const symptomCards = document.querySelectorAll('.symptom-guide-card');

    if (!symptomCards.length) return;

    function applyFilter() {
        const query = searchInput ? searchInput.value.toLowerCase().trim() : '';
        const activePill = document.querySelector('.symptom-filter-pill.active');
        const selectedCategory = activePill ? activePill.getAttribute('data-category').toLowerCase() : 'all';

        let visibleCount = 0;

        symptomCards.forEach(card => {
            const name = card.getAttribute('data-name') || '';
            const category = card.getAttribute('data-category') || '';
            const desc = card.getAttribute('data-desc') || '';

            const matchesSearch = query === '' || name.toLowerCase().includes(query) || desc.toLowerCase().includes(query);
            const matchesCategory = selectedCategory === 'all' || category.toLowerCase() === selectedCategory;

            if (matchesSearch && matchesCategory) {
                card.style.display = 'block';
                visibleCount++;
            } else {
                card.style.display = 'none';
            }
        });

        const emptyMsg = document.getElementById('symptomsEmptySearch');
        if (emptyMsg) {
            emptyMsg.style.display = visibleCount === 0 ? 'block' : 'none';
        }
    }

    if (searchInput) {
        searchInput.addEventListener('input', applyFilter);
    }

    filterPills.forEach(pill => {
        pill.addEventListener('click', function () {
            filterPills.forEach(p => p.classList.remove('active', 'btn-info', 'text-white'));
            filterPills.forEach(p => p.classList.add('btn-outline-secondary'));
            
            this.classList.remove('btn-outline-secondary');
            this.classList.add('active', 'btn-info', 'text-white');
            applyFilter();
        });
    });
}

// ==========================================================================
// 6. Clinical Assessment Form Dynamic Condition Switcher
// ==========================================================================
function initAssessmentSwitcher() {
    const diseaseSelector = document.getElementById('disease_type');
    if (!diseaseSelector) return;

    const sections = {
        'diabetes': document.getElementById('diabetes_fields'),
        'heart': document.getElementById('heart_fields'),
        'hypertension': document.getElementById('hypertension_fields'),
        'respiratory': document.getElementById('respiratory_fields'),
        'lifestyle': document.getElementById('lifestyle_fields')
    };

    function toggleFields() {
        const selected = diseaseSelector.value;
        Object.keys(sections).forEach(key => {
            const sec = sections[key];
            if (sec) {
                if (key === selected) {
                    sec.style.display = 'block';
                    enableInputs(sec, true);
                } else {
                    sec.style.display = 'none';
                    enableInputs(sec, false);
                }
            }
        });
    }

    function enableInputs(container, enable) {
        const inputs = container.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            if (enable) {
                input.removeAttribute('disabled');
            } else {
                input.setAttribute('disabled', 'disabled');
            }
        });
    }

    diseaseSelector.addEventListener('change', toggleFields);
    toggleFields();
}

// ==========================================================================
// 7. Range Sliders Live Synchronized Value Display & Control
// ==========================================================================
function initRangeSliders() {
    const rangeSliders = document.querySelectorAll('.sync-slider, input[type="range"]');
    rangeSliders.forEach(slider => {
        const targetId = slider.getAttribute('data-target') || (slider.name ? 'val_' + slider.name.toLowerCase() : null);
        const targetElem = targetId ? document.getElementById(targetId) : null;
        
        function syncSliderValue() {
            const currentVal = slider.value;
            if (targetElem) {
                targetElem.textContent = currentVal;
            }
            const pairedInputs = document.querySelectorAll(`input[type="number"][name="${slider.name}"]`);
            pairedInputs.forEach(paired => {
                if (paired !== slider && paired.value !== currentVal) {
                    paired.value = currentVal;
                }
            });
        }

        slider.addEventListener('input', syncSliderValue);
        slider.addEventListener('change', syncSliderValue);
        slider.addEventListener('touchmove', syncSliderValue);
        syncSliderValue();
    });

    const numberInputs = document.querySelectorAll('input[type="number"]');
    numberInputs.forEach(numInput => {
        const pairedSlider = document.querySelector(`input[type="range"][name="${numInput.name}"]`);
        if (pairedSlider) {
            numInput.addEventListener('input', function() {
                pairedSlider.value = numInput.value;
                const targetId = pairedSlider.getAttribute('data-target') || (numInput.name ? 'val_' + numInput.name.toLowerCase() : null);
                const targetElem = targetId ? document.getElementById(targetId) : null;
                if (targetElem) {
                    targetElem.textContent = numInput.value;
                }
            });
        }
    });
}

// ==========================================================================
// 8. Global Categorized Search Engine (Section 14)
// ==========================================================================
function initGlobalSearch() {
    const searchModal = document.getElementById('globalSearchModal');
    const searchInput = document.getElementById('globalSearchInput');
    const resultsContainer = document.getElementById('searchResultsContainer');
    const quickChips = document.querySelectorAll('.quick-search-chip');
    if (!searchModal || !searchInput || !resultsContainer) return;

    // Search Database Index
    const searchIndex = [
        // Clinical Tools
        { type: 'tool', title: 'Clinical Risk Assessment', cat: 'Clinical Tools', desc: 'Comprehensive multi-parameter clinical evaluation and statistical risk profiling.', url: 'assessment.php', icon: 'bi-shield-check', color: 'text-info' },
        { type: 'tool', title: 'Health Risk Calculator', cat: 'Clinical Tools', desc: 'Interactive calculator for BMI, diabetes, cardiac, blood pressure, and lifestyle metrics.', url: 'risk_calculator.php', icon: 'bi-calculator', color: 'text-warning' },
        { type: 'tool', title: 'AI Symptom Checker', cat: 'Clinical Tools', desc: 'Multi-symptom intelligent machine-learning disease correlation prediction.', url: 'prediction.php', icon: 'bi-cpu-fill', color: 'text-primary' },
        { type: 'tool', title: 'Health Simulator', cat: 'Clinical Tools', desc: 'Interactive parameter simulator exploring how lifestyle adjustments affect risk.', url: 'simulator.php', icon: 'bi-sliders', color: 'text-success' },
        { type: 'tool', title: 'Health Reports', cat: 'Clinical Tools', desc: 'View, generate, and download professional printable PDF health summaries.', url: 'report.php', icon: 'bi-file-earmark-medical', color: 'text-info' },
        { type: 'tool', title: 'Injury & Skin Scanner', cat: 'Clinical Tools', desc: 'Computer-vision screening for superficial injuries, acute infections, and concerning skin lesions.', url: 'image_scanner.php', icon: 'bi-camera', color: 'text-danger' },
        { type: 'tool', title: 'AI Health Assistant', cat: 'Clinical Tools', desc: 'Interactive conversational medical education assistant providing guidance on symptoms and wellness.', url: 'health_assistant.php', icon: 'bi-chat-heart', color: 'text-info' },
        { type: 'tool', title: 'Personal Health Profile', cat: 'Clinical Tools', desc: 'Manage your biometric profile, lifestyle metrics, and personal health targets.', url: 'profile.php', icon: 'bi-person-lines-fill', color: 'text-info' },
        { type: 'tool', title: 'Assessment History', cat: 'Clinical Tools', desc: 'Review complete historical records of your AI predictions and clinical assessments.', url: 'history.php', icon: 'bi-clock-history', color: 'text-primary' },
        { type: 'tool', title: 'Health Dashboard', cat: 'Clinical Tools', desc: 'Personalized health overview, quick actions, statistics, and prevention reminders.', url: 'dashboard.php', icon: 'bi-speedometer2', color: 'text-info' },

        // Emergency Guide
        { type: 'emergency', title: 'Emergency / Red-Flag Guide', cat: 'Emergency', desc: 'Critical life-threatening warning signs requiring immediate emergency medical care (911 / 112).', url: 'emergency.php', icon: 'bi-hospital', color: 'text-danger' },

        // Prevention Domains
        { type: 'prevention', title: 'Diabetes Prevention', cat: 'Prevention', desc: 'Dietary glycemic management, physical exercise routines, and insulin sensitivity guidance.', url: 'prevention.php#diabetes', icon: 'bi-droplet-half', color: 'text-success' },
        { type: 'prevention', title: 'Cardiovascular & Heart Health', cat: 'Prevention', desc: 'DASH diet protocols, sodium management, aerobic conditioning, and blood pressure control.', url: 'prevention.php#heart', icon: 'bi-heart-pulse', color: 'text-danger' },
        { type: 'prevention', title: 'Respiratory Health', cat: 'Prevention', desc: 'Airway hygiene, tobacco cessation, indoor ventilation, and allergen avoidance.', url: 'prevention.php#respiratory', icon: 'bi-lungs', color: 'text-info' },
        { type: 'prevention', title: 'Skin Health & UV Safety', cat: 'Prevention', desc: 'Broad-spectrum SPF sun protection, mole self-exams, and skin barrier maintenance.', url: 'prevention.php#skin', icon: 'bi-sun', color: 'text-warning' },
        { type: 'prevention', title: 'Nutrition & Balanced Diet', cat: 'Prevention', desc: 'Whole food dietary principles, micronutrient adequacy, and anti-inflammatory nutrition.', url: 'prevention.php#nutrition', icon: 'bi-egg-fried', color: 'text-success' },
        { type: 'prevention', title: 'Physical Activity & Fitness', cat: 'Prevention', desc: '150 minutes/week moderate aerobic guidelines, resistance training, and sedentary break habits.', url: 'prevention.php#activity', icon: 'bi-bicycle', color: 'text-info' },
        { type: 'prevention', title: 'Sleep Hygiene & Rest', cat: 'Prevention', desc: 'Consistent circadian rhythms, bedroom dark environments, and blue-light moderation.', url: 'prevention.php#sleep', icon: 'bi-moon-stars', color: 'text-primary' },
        { type: 'prevention', title: 'Stress Management & Mindfulness', cat: 'Prevention', desc: 'Cortisol regulation, breathing exercises, cognitive stress coping mechanisms.', url: 'prevention.php#stress', icon: 'bi-emoji-smile', color: 'text-warning' },
        { type: 'prevention', title: 'Infection Prevention & Hygiene', cat: 'Prevention', desc: 'Hand hygiene, barrier protections, food safety, and routine immunization schedules.', url: 'prevention.php#infection', icon: 'bi-shield-plus', color: 'text-success' },
        { type: 'prevention', title: 'General Preventive Health Checkups', cat: 'Prevention', desc: 'Age-appropriate screening guidelines, blood pressure, lipids, and cancer screenings.', url: 'prevention.php#general', icon: 'bi-clipboard-check', color: 'text-info' },

        // Health Education
        { type: 'education', title: 'Health Education Hub', cat: 'Education', desc: 'Comprehensive medical articles, FAQs, glossary, and myth-busting information.', url: 'education.php', icon: 'bi-book-half', color: 'text-warning' },
        { type: 'education', title: 'AI in Healthcare Guide', cat: 'Education', desc: 'Understanding machine learning algorithms, decision support ethics, and safety guardrails.', url: 'education.php#ai-guide', icon: 'bi-robot', color: 'text-info' },
        { type: 'education', title: 'Medical Terminology Glossary', cat: 'Education', desc: 'Quick definitions for common clinical terms: Atherosclerosis, Erythema, Dyspnea, etc.', url: 'education.php#glossary', icon: 'bi-alphabet-uppercase', color: 'text-info' },
        { type: 'education', title: 'Health Myths vs Facts', cat: 'Education', desc: 'Debunking common misconceptions about diabetes, cholesterol, vaccines, and diet.', url: 'education.php#myths', icon: 'bi-patch-question', color: 'text-warning' },

        // Top Diseases
        { type: 'disease', title: 'Diabetes Mellitus', cat: 'Diseases', desc: 'Chronic metabolic disease characterized by elevated blood glucose levels and insulin resistance.', url: 'disease_detail.php?id=1', icon: 'bi-droplet-fill', color: 'text-danger' },
        { type: 'disease', title: 'Hypertension', cat: 'Diseases', desc: 'Chronic high blood pressure against arterial walls increasing cardiac workload and stroke risk.', url: 'disease_detail.php?id=2', icon: 'bi-heart-pulse-fill', color: 'text-danger' },
        { type: 'disease', title: 'Coronary Artery Disease', cat: 'Diseases', desc: 'Atherosclerotic plaque accumulation in coronary vessels causing myocardial ischemia.', url: 'diseases.php?search=Coronary', icon: 'bi-heart-fill', color: 'text-danger' },
        { type: 'disease', title: 'Heart Failure', cat: 'Diseases', desc: 'Progressive inability of cardiac ventricles to pump sufficient blood for systemic demands.', url: 'disease_detail.php?id=29', icon: 'bi-heartbreak-fill', color: 'text-danger' },
        { type: 'disease', title: 'Asthma', cat: 'Diseases', desc: 'Chronic bronchial inflammatory airway disease causing episodic wheezing and dyspnea.', url: 'disease_detail.php?id=4', icon: 'bi-lungs-fill', color: 'text-info' },
        { type: 'disease', title: 'Pneumonia', cat: 'Diseases', desc: 'Infection of pulmonary alveolar spaces with purulent fluid exudate causing fever and cough.', url: 'disease_detail.php?id=5', icon: 'bi-lungs', color: 'text-info' },
        { type: 'disease', title: 'COPD', cat: 'Diseases', desc: 'Progressive airflow limitation caused by emphysema and chronic bronchial inflammation.', url: 'disease_detail.php?id=16', icon: 'bi-lungs-fill', color: 'text-info' },
        { type: 'disease', title: 'Bronchitis', cat: 'Diseases', desc: 'Acute or chronic inflammation of the tracheobronchial tree causing productive cough.', url: 'disease_detail.php?id=17', icon: 'bi-lungs', color: 'text-info' },
        { type: 'disease', title: 'Fever', cat: 'Diseases', desc: 'Systemic pyrexial immune defense response with body temperature elevation above 38°C.', url: 'diseases.php?search=Fever', icon: 'bi-thermometer-high', color: 'text-warning' },
        { type: 'disease', title: 'Common Cold', cat: 'Diseases', desc: 'Acute upper respiratory rhinovirus infection causing rhinorrhea, sneezing and sore throat.', url: 'disease_detail.php?id=26', icon: 'bi-thermometer-half', color: 'text-info' },
        { type: 'disease', title: 'Influenza', cat: 'Diseases', desc: 'Acute respiratory viral infection causing high fever, myalgia, severe fatigue, and chills.', url: 'disease_detail.php?id=8', icon: 'bi-virus', color: 'text-danger' },
        { type: 'disease', title: 'Dehydration', cat: 'Diseases', desc: 'Severe systemic water deficit leading to electrolyte imbalance, dry mucosa, and hypotension.', url: 'diseases.php?search=Dehydration', icon: 'bi-droplet', color: 'text-info' },
        { type: 'disease', title: 'Fatigue', cat: 'Diseases', desc: 'Persistent systemic exhaustion and low physical energy not relieved by sleep.', url: 'diseases.php?search=Fatigue', icon: 'bi-battery-half', color: 'text-warning' },
        { type: 'disease', title: 'Stroke', cat: 'Diseases', desc: 'Acute disruption of cerebral arterial perfusion causing rapid focal neurological deficits.', url: 'emergency.php#stroke', icon: 'bi-exclamation-octagon-fill', color: 'text-danger' },
        { type: 'disease', title: 'Migraine', cat: 'Diseases', desc: 'Recurrent neurovascular headache disorder with throbbing unilateral pain and photophobia.', url: 'disease_detail.php?id=12', icon: 'bi-lightning-charge-fill', color: 'text-warning' },
        { type: 'disease', title: 'Epilepsy', cat: 'Diseases', desc: 'Central nervous system disorder characterized by recurrent unprovoked electrical seizures.', url: 'disease_detail.php?id=13', icon: 'bi-activity', color: 'text-warning' },
        { type: 'disease', title: 'Parkinson\'s Disease', cat: 'Diseases', desc: 'Neurodegenerative dopamine deficit disorder causing resting tremors, rigidity, and bradykinesia.', url: 'disease_detail.php?id=14', icon: 'bi-person-walking', color: 'text-info' },
        { type: 'disease', title: 'Gastritis', cat: 'Diseases', desc: 'Erosive or non-erosive inflammation of the protective gastric mucosal barrier.', url: 'disease_detail.php?id=18', icon: 'bi-shield-slash', color: 'text-warning' },
        { type: 'disease', title: 'GERD (Acid Reflux)', cat: 'Diseases', desc: 'Retrograde flow of gastric acid into the esophagus causing pyrosis and regurgitation.', url: 'disease_detail.php?id=36', icon: 'bi-fire', color: 'text-danger' },
        { type: 'disease', title: 'Gastroenteritis', cat: 'Diseases', desc: 'Acute gastrointestinal infectious inflammation causing nausea, diarrhea, and abdominal cramps.', url: 'disease_detail.php?id=38', icon: 'bi-exclamation-triangle', color: 'text-warning' },
        { type: 'disease', title: 'Irritable Bowel Syndrome (IBS)', cat: 'Diseases', desc: 'Functional disorder of gut-brain axis with recurrent abdominal discomfort and altered motility.', url: 'disease_detail.php?id=39', icon: 'bi-arrow-left-right', color: 'text-info' },
        { type: 'disease', title: 'Hypothyroidism', cat: 'Diseases', desc: 'Endocrine deficiency of thyroxine hormones causing fatigue, weight gain, and cold intolerance.', url: 'disease_detail.php?id=24', icon: 'bi-speedometer', color: 'text-info' },
        { type: 'disease', title: 'Hyperthyroidism', cat: 'Diseases', desc: 'Excessive thyroid hormone secretion causing tachycardia, weight loss, heat intolerance and tremors.', url: 'disease_detail.php?id=25', icon: 'bi-speedometer2', color: 'text-danger' },
        { type: 'disease', title: 'Obesity', cat: 'Diseases', desc: 'Chronic multifactorial adiposity with BMI >= 30, elevating risks of diabetes and heart disease.', url: 'disease_detail.php?id=34', icon: 'bi-person-bounding-box', color: 'text-warning' },
        { type: 'disease', title: 'Acne Vulgaris', cat: 'Diseases', desc: 'Chronic inflammation of pilosebaceous units with comedones, papules, and pustules.', url: 'disease_detail.php?id=47', icon: 'bi-circle-fill', color: 'text-warning' },
        { type: 'disease', title: 'Eczema (Atopic Dermatitis)', cat: 'Diseases', desc: 'Pruritic, erythematous, dry skin barrier breakdown driven by immune dysregulation.', url: 'disease_detail.php?id=48', icon: 'bi-shield-exclamation', color: 'text-info' },
        { type: 'disease', title: 'Psoriasis', cat: 'Diseases', desc: 'Autoimmune hyperproliferative skin disease causing silvery scaled erythematous plaques.', url: 'disease_detail.php?id=49', icon: 'bi-layers-fill', color: 'text-danger' },
        { type: 'disease', title: 'Contact Dermatitis', cat: 'Diseases', desc: 'Localized allergic or irritant skin reaction elicited by external chemical contact.', url: 'disease_detail.php?id=50', icon: 'bi-hand-index', color: 'text-warning' },
        { type: 'disease', title: 'Melanoma', cat: 'Diseases', desc: 'Malignant skin lesion arising from melanocytes, requiring rapid dermatological excision.', url: 'diseases.php?search=Melanoma', icon: 'bi-exclamation-diamond-fill', color: 'text-danger' },
        { type: 'disease', title: 'Basal Cell Carcinoma', cat: 'Diseases', desc: 'Commonest cutaneous cancer presenting as pearly translucent papules with telangiectasia.', url: 'diseases.php?search=Basal', icon: 'bi-shield-slash-fill', color: 'text-danger' },
        { type: 'disease', title: 'Actinic Keratosis', cat: 'Diseases', desc: 'Pre-cancerous solar keratotic scaly macules on sun-damaged skin areas.', url: 'diseases.php?search=Actinic', icon: 'bi-sun-fill', color: 'text-warning' },

        // Top Symptoms
        { type: 'symptom', title: 'Chest Pain or Discomfort', cat: 'Symptoms', desc: 'Pressure or squeezing in chest; could indicate cardiac ischemia or costochondritis.', url: 'symptoms_guide.php#chest_pain', icon: 'bi-heart-pulse', color: 'text-danger' },
        { type: 'symptom', title: 'Shortness of Breath (Dyspnea)', cat: 'Symptoms', desc: 'Airway difficulty breathing, wheezing, or exertional breathlessness.', url: 'symptoms_guide.php#breathlessness', icon: 'bi-lungs', color: 'text-danger' },
        { type: 'symptom', title: 'High Fever & Chills', cat: 'Symptoms', desc: 'Core body temperature spike accompanied by rigors, sweating, and malaise.', url: 'symptoms_guide.php#high_fever', icon: 'bi-thermometer-high', color: 'text-warning' },
        { type: 'symptom', title: 'Chronic Fatigue & Lethargy', cat: 'Symptoms', desc: 'Profound persistent exhaustion, low mental alertness, or muscle weakness.', url: 'symptoms_guide.php#fatigue', icon: 'bi-battery-half', color: 'text-info' },
        { type: 'symptom', title: 'Persistent Cough', cat: 'Symptoms', desc: 'Dry or productive mucous cough lasting longer than 10-14 days.', url: 'symptoms_guide.php#cough', icon: 'bi-soundwave', color: 'text-info' },
        { type: 'symptom', title: 'Headache & Throbbing Pain', cat: 'Symptoms', desc: 'Cephalic pain across temple, forehead or occipital regions.', url: 'symptoms_guide.php#headache', icon: 'bi-lightning', color: 'text-warning' },
        { type: 'symptom', title: 'Joint Pain & Swelling', cat: 'Symptoms', desc: 'Inflammatory tenderness, stiffness, or fluid effusion in articulating joints.', url: 'symptoms_guide.php#joint_pain', icon: 'bi-person', color: 'text-warning' },
        { type: 'symptom', title: 'Skin Rash & Irritation', cat: 'Symptoms', desc: 'Cutaneous erythema, pruritus, wheals, or vesicular lesions.', url: 'symptoms_guide.php#skin_rash', icon: 'bi-app-indicator', color: 'text-danger' }
    ];

    function renderResults(query) {
        query = query.trim().toLowerCase();
        if (query.length < 2) {
            resultsContainer.innerHTML = `
                <div class="text-center py-4 text-muted">
                    <i class="bi bi-search fs-1 opacity-25 d-block mb-2"></i>
                    Type at least 2 characters to search across MediSense AI...
                </div>
            `;
            return;
        }

        const matches = searchIndex.filter(item => {
            return item.title.toLowerCase().includes(query) ||
                   item.desc.toLowerCase().includes(query) ||
                   item.cat.toLowerCase().includes(query);
        });

        if (matches.length === 0) {
            resultsContainer.innerHTML = `
                <div class="text-center py-4 text-muted">
                    <i class="bi bi-emoji-neutral fs-2 text-warning d-block mb-2"></i>
                    No direct matches found for "<strong>${escapeHtml(query)}</strong>".
                    <div class="mt-2">
                        <a href="diseases.php" class="btn btn-sm btn-outline-info rounded-pill">Browse Disease Library</a>
                    </div>
                </div>
            `;
            return;
        }

        // Group by category
        const groups = {};
        matches.forEach(item => {
            if (!groups[item.cat]) groups[item.cat] = [];
            groups[item.cat].push(item);
        });

        let html = '';
        for (const catName in groups) {
            html += `<h6 class="small fw-bold text-uppercase text-muted mt-3 mb-2 px-1"><i class="bi bi-tag-fill me-1 text-info"></i> ${catName} (${groups[catName].length})</h6>`;
            html += '<div class="list-group list-group-flush rounded-3 border mb-2">';
            groups[catName].forEach(item => {
                html += `
                    <a href="${item.url}" class="list-group-item list-group-item-action d-flex align-items-start gap-3 py-2 px-3 border-secondary border-opacity-10">
                        <i class="bi ${item.icon} fs-5 ${item.color} mt-1"></i>
                        <div class="flex-grow-1">
                            <div class="d-flex justify-content-between align-items-center">
                                <span class="fw-bold text-body">${highlightQuery(item.title, query)}</span>
                                <span class="badge bg-secondary-subtle text-secondary small py-1 px-2 rounded-pill">${item.cat}</span>
                            </div>
                            <p class="small text-muted mb-0">${highlightQuery(item.desc, query)}</p>
                        </div>
                    </a>
                `;
            });
            html += '</div>';
        }

        resultsContainer.innerHTML = html;
    }

    function highlightQuery(text, query) {
        if (!query) return escapeHtml(text);
        const escapedQuery = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const regex = new RegExp(`(${escapedQuery})`, 'gi');
        return escapeHtml(text).replace(regex, '<mark class="bg-info bg-opacity-25 text-body p-0 rounded">$1</mark>');
    }

    function escapeHtml(str) {
        return String(str).replace(/[&<>"']/g, function(m) {
            return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m];
        });
    }

    // Input listener
    searchInput.addEventListener('input', function() {
        renderResults(this.value);
    });

    // Quick chip listeners
    quickChips.forEach(chip => {
        chip.addEventListener('click', function() {
            const term = this.getAttribute('data-term') || '';
            searchInput.value = term;
            renderResults(term);
            searchInput.focus();
        });
    });

    // Keyboard shortcut (Ctrl+K or Cmd+K or /)
    window.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
            e.preventDefault();
            const modalInstance = bootstrap.Modal.getOrCreateInstance(searchModal);
            modalInstance.show();
        } else if (e.key === '/' && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
            e.preventDefault();
            const modalInstance = bootstrap.Modal.getOrCreateInstance(searchModal);
            modalInstance.show();
        }
    });

    // Focus input on modal open
    searchModal.addEventListener('shown.bs.modal', function() {
        searchInput.focus();
    });
}

