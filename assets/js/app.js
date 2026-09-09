// ==========================================================================
// AI Healthcare Client Application Engine
// Theme Toggle | Symptom Tiles (Matte/Glossy) | Counter Animation | Search
// ==========================================================================

// Global Theme Initializer (prevents FOUC)
(function() {
    const savedTheme = localStorage.getItem('ai_healthcare_theme');
    const systemPrefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    const initialTheme = savedTheme ? savedTheme : (systemPrefersDark ? 'dark' : 'dark'); // default dark
    document.documentElement.setAttribute('data-theme', initialTheme);
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
    const toggleBtns = document.querySelectorAll('.theme-toggle-btn');
    if (!toggleBtns.length) return;

    function updateToggleUI(currentTheme) {
        toggleBtns.forEach(btn => {
            const darkIcon = btn.querySelector('.theme-icon-dark');
            const lightIcon = btn.querySelector('.theme-icon-light');
            const label = btn.querySelector('.theme-text');

            if (currentTheme === 'light') {
                if (darkIcon) darkIcon.classList.add('d-none');
                if (lightIcon) lightIcon.classList.remove('d-none');
                if (label) label.textContent = 'Light';
            } else {
                if (darkIcon) darkIcon.classList.remove('d-none');
                if (lightIcon) lightIcon.classList.add('d-none');
                if (label) label.textContent = 'Dark';
            }
        });
    }

    const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
    updateToggleUI(currentTheme);

    toggleBtns.forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const activeTheme = document.documentElement.getAttribute('data-theme') || 'dark';
            const newTheme = activeTheme === 'dark' ? 'light' : 'dark';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('ai_healthcare_theme', newTheme);
            updateToggleUI(newTheme);
        });
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
    const diabetesFields = document.getElementById('diabetes_fields');
    const heartFields = document.getElementById('heart_fields');

    if (!diseaseSelector || !diabetesFields || !heartFields) return;

    function toggleFields() {
        const selected = diseaseSelector.value;
        if (selected === 'diabetes') {
            diabetesFields.style.display = 'block';
            heartFields.style.display = 'none';
            enableInputs(diabetesFields, true);
            enableInputs(heartFields, false);
        } else if (selected === 'heart') {
            diabetesFields.style.display = 'none';
            heartFields.style.display = 'block';
            enableInputs(diabetesFields, false);
            enableInputs(heartFields, true);
        }
    }

    function enableInputs(container, enable) {
        const inputs = container.querySelectorAll('input, select');
        inputs.forEach(input => {
            if (enable) input.removeAttribute('disabled');
            else input.setAttribute('disabled', 'disabled');
        });
    }

    diseaseSelector.addEventListener('change', toggleFields);
    toggleFields();
}

// ==========================================================================
// 7. Range Sliders Value Display
// ==========================================================================
function initRangeSliders() {
    const rangeSliders = document.querySelectorAll('.sync-slider');
    rangeSliders.forEach(slider => {
        const targetId = slider.getAttribute('data-target');
        const targetElem = document.getElementById(targetId);
        if (targetElem) {
            slider.addEventListener('input', function() {
                targetElem.innerText = slider.value;
            });
        }
    });
}
