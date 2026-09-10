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
        // Resolve target display span ID: explicit data-target or convention val_{name}
        const targetId = slider.getAttribute('data-target') || (slider.name ? 'val_' + slider.name.toLowerCase() : null);
        const targetElem = targetId ? document.getElementById(targetId) : null;
        
        function syncSliderValue() {
            const currentVal = slider.value;
            if (targetElem) {
                targetElem.textContent = currentVal;
            }
            
            // If there is an adjacent or paired number input with the same name, sync it
            const pairedInputs = document.querySelectorAll(`input[type="number"][name="${slider.name}"]`);
            pairedInputs.forEach(paired => {
                if (paired !== slider && paired.value !== currentVal) {
                    paired.value = currentVal;
                }
            });
        }

        // Listen on input, change, and touch events for seamless desktop & mobile operation
        slider.addEventListener('input', syncSliderValue);
        slider.addEventListener('change', syncSliderValue);
        slider.addEventListener('touchmove', syncSliderValue);
        
        // Run initial synchronization so displayed numbers are never hardcoded or blank
        syncSliderValue();
    });

    // Two-way sync: When user types into a paired number input, immediately update the slider and readout
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
