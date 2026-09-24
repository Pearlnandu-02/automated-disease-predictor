/**
 * assets/js/symptom_prediction.js
 * MediSense AI - Symptom-Based Disease Prediction Feature Engine
 * Handles natural language symptom normalization, chip management,
 * clinical context, explainable multi-condition matching, follow-up questions,
 * and emergency red-flag triaging.
 */

(function () {
    'use strict';

    // Application State
    const state = {
        symptoms: [],
        diseases: [],
        selectedSymptoms: new Set(),
        categoryFilter: 'all',
        clinicalContext: {
            ageGroup: 'adult',
            duration: '1_3_days',
            severity: 'moderate',
            trajectory: 'same'
        },
        followUpAnswers: {},
        currentAnalysis: null
    };

    // DOM Elements
    const elements = {
        searchInput: document.getElementById('symptomSearchInput'),
        autocompleteList: document.getElementById('symptomAutocompleteList'),
        chipsContainer: document.getElementById('selectedSymptomChips'),
        emptyChipsNotice: document.getElementById('emptyChipsNotice'),
        selectedCountBadge: document.getElementById('selectedCountBadge'),
        clearAllBtn: document.getElementById('clearSymptomsBtn'),
        analyzeBtn: document.getElementById('analyzeSymptomsBtn'),
        categoryPills: document.querySelectorAll('.symptom-category-pill'),
        popularPills: document.querySelectorAll('.symptom-popular-pill'),
        browserContainer: document.getElementById('symptomBrowserContainer'),
        loadingState: document.getElementById('ai-loading-state'),
        resultsContainer: document.getElementById('symptomResultsContainer'),
        emptyResultsContainer: document.getElementById('emptyResultsContainer'),
        refineContainer: document.getElementById('refineQuestionsContainer'),
        emergencyContainer: document.getElementById('emergencyAlertContainer'),
        methodologyModal: document.getElementById('methodologyModal')
    };

    /**
     * Initialize Engine
     */
    async function init() {
        try {
            // Load datasets
            const [symRes, disRes] = await Promise.all([
                fetch('data/symptoms.json'),
                fetch('data/diseases.json')
            ]);

            state.symptoms = await symRes.json();
            state.diseases = await disRes.json();

            setupEventListeners();
            renderSymptomBrowser();

            // Check if pre-selected symptom exists in URL parameter
            const urlParams = new URLSearchParams(window.location.search);
            const paramSym = urlParams.get('symptom');
            if (paramSym) {
                addSymptom(paramSym);
            }
        } catch (err) {
            console.error('Failed to initialize symptom prediction engine:', err);
        }
    }

    /**
     * Setup Event Listeners
     */
    function setupEventListeners() {
        // Search Input
        if (elements.searchInput) {
            elements.searchInput.addEventListener('input', handleSearchInput);
            elements.searchInput.addEventListener('keydown', handleSearchKeydown);
            document.addEventListener('click', (e) => {
                if (!elements.searchInput.contains(e.target) && !elements.autocompleteList.contains(e.target)) {
                    elements.autocompleteList.style.display = 'none';
                }
            });
        }

        // Clear All Button
        if (elements.clearAllBtn) {
            elements.clearAllBtn.addEventListener('click', clearAllSymptoms);
        }

        // Analyze Button
        if (elements.analyzeBtn) {
            elements.analyzeBtn.addEventListener('click', triggerAnalysis);
        }

        // Category Filter Pills
        elements.categoryPills.forEach((btn) => {
            btn.addEventListener('click', () => {
                elements.categoryPills.forEach((b) => b.classList.remove('active', 'btn-info', 'text-white'));
                elements.categoryPills.forEach((b) => b.classList.add('btn-outline-secondary'));
                btn.classList.add('active', 'btn-info', 'text-white');
                btn.classList.remove('btn-outline-secondary');
                state.categoryFilter = btn.dataset.category || 'all';
                renderSymptomBrowser();
            });
        });

        // Popular Symptom Pills
        elements.popularPills.forEach((btn) => {
            btn.addEventListener('click', () => {
                const symKey = btn.dataset.symptom;
                if (symKey) {
                    addSymptom(symKey);
                }
            });
        });

        // Clinical Context Selects / Radios
        const ageSelect = document.getElementById('contextAgeGroup');
        const durationSelect = document.getElementById('contextDuration');
        const severitySelect = document.getElementById('contextSeverity');
        const trajectorySelect = document.getElementById('contextTrajectory');

        if (ageSelect) ageSelect.addEventListener('change', (e) => state.clinicalContext.ageGroup = e.target.value);
        if (durationSelect) durationSelect.addEventListener('change', (e) => state.clinicalContext.duration = e.target.value);
        if (severitySelect) severitySelect.addEventListener('change', (e) => state.clinicalContext.severity = e.target.value);
        if (trajectorySelect) trajectorySelect.addEventListener('change', (e) => state.clinicalContext.trajectory = e.target.value);
    }

    /**
     * Tolerant Natural Language Symptom Search
     */
    function normalizeQuery(raw) {
        return (raw || '').toLowerCase().trim().replace(/[^\w\s]/g, '');
    }

    function searchSymptoms(query) {
        const q = normalizeQuery(query);
        if (!q || q.length < 2) return [];

        const matches = [];

        state.symptoms.forEach((sym) => {
            let score = 0;
            const keyNorm = normalizeQuery(sym.key);
            const nameNorm = normalizeQuery(sym.name);

            // Exact match
            if (nameNorm === q || keyNorm === q) score += 100;
            else if (nameNorm.startsWith(q)) score += 50;
            else if (nameNorm.includes(q)) score += 30;

            // Synonym matches
            if (sym.synonyms && Array.isArray(sym.synonyms)) {
                for (const syn of sym.synonyms) {
                    const synNorm = normalizeQuery(syn);
                    if (synNorm === q) {
                        score += 90;
                        break;
                    } else if (synNorm.startsWith(q)) {
                        score += 40;
                        break;
                    } else if (synNorm.includes(q)) {
                        score += 25;
                        break;
                    }
                }
            }

            if (score > 0) {
                matches.push({ symptom: sym, score });
            }
        });

        matches.sort((a, b) => b.score - a.score);
        return matches.slice(0, 8).map((m) => m.symptom);
    }

    function handleSearchInput(e) {
        const query = e.target.value;
        const matches = searchSymptoms(query);

        if (!matches || matches.length === 0) {
            elements.autocompleteList.innerHTML = `
                <div class="p-3 text-muted small text-center">
                    <i class="bi bi-info-circle me-1"></i> No matching symptom found. Try "fever", "headache", "cough", or "stomach pain".
                </div>
            `;
            elements.autocompleteList.style.display = query.trim().length >= 2 ? 'block' : 'none';
            return;
        }

        elements.autocompleteList.innerHTML = matches.map((sym) => {
            const isSelected = state.selectedSymptoms.has(sym.key);
            return `
                <button type="button" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center ${isSelected ? 'disabled bg-card-subtle' : ''}" data-key="${sym.key}">
                    <div>
                        <div class="fw-bold ${isSelected ? 'text-muted' : 'text-primary'}">${escapeHtml(sym.name)}</div>
                        <small class="text-muted">${escapeHtml(sym.category)}</small>
                    </div>
                    ${isSelected ? '<span class="badge bg-secondary">Added</span>' : '<i class="bi bi-plus-circle text-info fs-5"></i>'}
                </button>
            `;
        }).join('');

        elements.autocompleteList.querySelectorAll('button[data-key]').forEach((btn) => {
            btn.addEventListener('click', () => {
                addSymptom(btn.dataset.key);
                elements.searchInput.value = '';
                elements.autocompleteList.style.display = 'none';
                elements.searchInput.focus();
            });
        });

        elements.autocompleteList.style.display = 'block';
    }

    function handleSearchKeydown(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            const firstOption = elements.autocompleteList.querySelector('button[data-key]:not(.disabled)');
            if (firstOption) {
                firstOption.click();
            }
        } else if (e.key === 'Escape') {
            elements.autocompleteList.style.display = 'none';
        }
    }

    /**
     * Add & Remove Symptom Chips
     */
    function addSymptom(key) {
        if (state.selectedSymptoms.has(key)) {
            // Already added
            return;
        }

        const sym = state.symptoms.find((s) => s.key === key);
        if (!sym) return;

        state.selectedSymptoms.add(key);
        renderSelectedChips();
        updateBrowserActiveStates();
    }

    function removeSymptom(key) {
        state.selectedSymptoms.delete(key);
        renderSelectedChips();
        updateBrowserActiveStates();

        // If results are open and we drop below 2 symptoms, clear results
        if (state.selectedSymptoms.size < 2 && elements.resultsContainer) {
            elements.resultsContainer.style.display = 'none';
            if (elements.emptyResultsContainer) {
                elements.emptyResultsContainer.style.display = 'flex';
            }
        }
    }

    function clearAllSymptoms() {
        state.selectedSymptoms.clear();
        state.followUpAnswers = {};
        renderSelectedChips();
        updateBrowserActiveStates();

        if (elements.resultsContainer) elements.resultsContainer.style.display = 'none';
        if (elements.emptyResultsContainer) elements.emptyResultsContainer.style.display = 'flex';
        if (elements.refineContainer) elements.refineContainer.style.display = 'none';
        if (elements.emergencyContainer) elements.emergencyContainer.style.display = 'none';
    }

    function renderSelectedChips() {
        if (!elements.chipsContainer) return;

        const count = state.selectedSymptoms.size;

        if (elements.selectedCountBadge) {
            elements.selectedCountBadge.textContent = count === 0
                ? '0 symptoms selected'
                : `${count} symptom${count > 1 ? 's' : ''} selected`;
            elements.selectedCountBadge.className = count >= 2
                ? 'badge bg-info text-white'
                : 'badge bg-secondary bg-opacity-50 text-muted';
        }

        if (count === 0) {
            elements.chipsContainer.innerHTML = '';
            if (elements.emptyChipsNotice) elements.emptyChipsNotice.style.display = 'block';
            return;
        }

        if (elements.emptyChipsNotice) elements.emptyChipsNotice.style.display = 'none';

        elements.chipsContainer.innerHTML = Array.from(state.selectedSymptoms).map((key) => {
            const sym = state.symptoms.find((s) => s.key === key) || { name: key, category: 'General' };
            return `
                <div class="symptom-chip animate-fade-in" data-key="${sym.key}">
                    <span class="chip-name">${escapeHtml(sym.name)}</span>
                    <button type="button" class="chip-remove-btn" aria-label="Remove ${escapeHtml(sym.name)}" data-remove="${sym.key}">
                        <i class="bi bi-x"></i>
                    </button>
                </div>
            `;
        }).join('');

        elements.chipsContainer.querySelectorAll('[data-remove]').forEach((btn) => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                removeSymptom(btn.dataset.remove);
            });
        });
    }

    /**
     * Render Body System Symptoms Browser
     */
    function renderSymptomBrowser() {
        if (!elements.browserContainer) return;

        const filter = state.categoryFilter.toLowerCase();
        const filteredSymptoms = state.symptoms.filter((sym) => {
            if (filter === 'all') return true;
            return sym.category.toLowerCase().includes(filter);
        });

        elements.browserContainer.innerHTML = filteredSymptoms.map((sym) => {
            const isSelected = state.selectedSymptoms.has(sym.key);
            return `
                <button type="button" class="symptom-browser-tile ${isSelected ? 'selected' : ''}" data-key="${sym.key}">
                    <span class="tile-label">${escapeHtml(sym.name)}</span>
                    <i class="bi ${isSelected ? 'bi-check-circle-fill text-info' : 'bi-plus-circle text-muted'}"></i>
                </button>
            `;
        }).join('');

        elements.browserContainer.querySelectorAll('[data-key]').forEach((btn) => {
            btn.addEventListener('click', () => {
                const key = btn.dataset.key;
                if (state.selectedSymptoms.has(key)) {
                    removeSymptom(key);
                } else {
                    addSymptom(key);
                }
            });
        });
    }

    function updateBrowserActiveStates() {
        if (!elements.browserContainer) return;
        elements.browserContainer.querySelectorAll('[data-key]').forEach((btn) => {
            const isSelected = state.selectedSymptoms.has(btn.dataset.key);
            btn.classList.toggle('selected', isSelected);
            const icon = btn.querySelector('i');
            if (icon) {
                icon.className = isSelected ? 'bi bi-check-circle-fill text-info' : 'bi bi-plus-circle text-muted';
            }
        });

        // Also update popular pills
        elements.popularPills.forEach((btn) => {
            const isSelected = state.selectedSymptoms.has(btn.dataset.symptom);
            btn.classList.toggle('active', isSelected);
            btn.classList.toggle('btn-info', isSelected);
            btn.classList.toggle('text-white', isSelected);
            btn.classList.toggle('btn-outline-secondary', !isSelected);
        });
    }

    /**
     * Matching & Prediction Engine
     */
    function runPrediction() {
        const selectedSet = new Set(state.selectedSymptoms);
        const results = [];

        state.diseases.forEach((d) => {
            const common = new Set(d.commonSymptoms || []);
            const less = new Set(d.lessCommonSymptoms || []);
            const allSyms = new Set(d.symptoms || []);

            const matchedCommon = [];
            const matchedLess = [];
            const allMatched = [];

            selectedSet.forEach((s) => {
                if (common.has(s)) matchedCommon.push(s);
                if (less.has(s)) matchedLess.push(s);
                if (allSyms.has(s)) allMatched.push(s);
            });

            if (allMatched.length === 0) return;

            // Weights: Characteristic symptoms weight 3.0, secondary weight 1.5
            const wMatched = (matchedCommon.length * 3.0) + (matchedLess.length * 1.5);
            const wExpected = (common.size * 3.0) + (less.size * 1.5);
            if (wExpected === 0) return;

            const recall = wMatched / wExpected;

            // Penalty for mismatch
            let wSelected = 0.0;
            selectedSet.forEach((s) => {
                if (common.has(s)) wSelected += 3.0;
                else if (less.has(s)) wSelected += 1.5;
                else wSelected += 2.0; // mismatch penalty
            });

            const precision = wSelected > 0 ? (wMatched / wSelected) : 0;

            // F0.8 Score
            const beta = 0.8;
            const betaSq = beta * beta;
            let fScore = 0;
            if ((betaSq * precision + recall) > 0) {
                fScore = ((1 + betaSq) * precision * recall) / ((betaSq * precision) + recall);
            }

            // Adjust with follow-up answers if present
            let bonus = 0;
            if (state.followUpAnswers.cough_type === 'with_phlegm' && d.id === 'pneumonia') bonus += 5;
            if (state.followUpAnswers.cough_type === 'dry' && (d.id === 'asthma' || d.id === 'common-cold')) bonus += 5;
            if (state.followUpAnswers.headache_location === 'one_sided' && d.id === 'migraine') bonus += 7;
            if (state.followUpAnswers.headache_location === 'band' && d.id === 'tension-headache') bonus += 7;
            if (state.followUpAnswers.rash_character === 'wheals' && d.id === 'urticaria-hives') bonus += 7;

            let scoreVal = Math.min(100, Math.max(0, Math.round((fScore * 100) + bonus)));

            if (scoreVal < 20) return;

            let matchLevel = 'Limited';
            if (scoreVal >= 70) matchLevel = 'High';
            else if (scoreVal >= 40) matchLevel = 'Moderate';

            const unmatchedExpected = Array.from(allSyms).filter((s) => !selectedSet.has(s));

            results.push({
                id: d.id,
                name: d.name,
                category: d.category,
                score: scoreVal,
                matchLevel: matchLevel,
                matchedSymptoms: allMatched,
                matchedCommon: matchedCommon,
                matchedLess: matchedLess,
                otherSymptoms: unmatchedExpected.slice(0, 4),
                description: d.description,
                causes: d.causes,
                riskFactors: d.riskFactors || [],
                prevention: d.prevention || [],
                redFlags: d.redFlags || [],
                differentiating: d.differentiatingFeatures || '',
                whenToSeekCare: d.whenToSeekCare || '',
                source: d.source || 'CDC Guidelines / WHO Disease Reference'
            });
        });

        results.sort((a, b) => b.score - a.score);
        return results.slice(0, 5);
    }

    /**
     * Trigger Multi-Step Animated Analysis
     */
    async function triggerAnalysis() {
        if (state.selectedSymptoms.size < 2) {
            alert('Please select at least 2 symptoms to begin an educational analysis.');
            elements.searchInput?.focus();
            return;
        }

        // Show Loading Animation
        if (elements.emptyResultsContainer) elements.emptyResultsContainer.style.display = 'none';
        if (elements.resultsContainer) elements.resultsContainer.style.display = 'none';
        if (elements.loadingState) elements.loadingState.style.display = 'block';

        // Animate Step dots
        const steps = ['loading-step-1', 'loading-step-2', 'loading-step-3', 'loading-step-4'];
        for (let i = 0; i < steps.length; i++) {
            const stepEl = document.getElementById(steps[i]);
            if (stepEl) {
                stepEl.classList.add('active');
            }
            await new Promise((r) => setTimeout(r, 260));
        }

        // Compute results
        const conditions = runPrediction();
        state.currentAnalysis = conditions;

        // Hide Loading Animation
        if (elements.loadingState) elements.loadingState.style.display = 'none';

        // Render Results
        renderResults(conditions);

        // Render Follow-Up Questions (Phase 11)
        renderFollowUpQuestions();

        // Record history to database asynchronously (if user is logged in)
        if (conditions.length > 0) {
            recordPredictionHistory(conditions[0]);
        }
    }

    /**
     * Render Condition Cards & Overlap Advisory
     */
    function renderResults(conditions) {
        if (!elements.resultsContainer) return;

        if (!conditions || conditions.length === 0) {
            elements.resultsContainer.innerHTML = `
                <div class="card-custom p-5 text-center">
                    <i class="bi bi-question-circle display-4 text-warning mb-3"></i>
                    <h4 class="fw-bold">No High-Confidence Symptom Pattern Found</h4>
                    <p class="text-muted small">
                        The selected symptoms did not strongly correlate with a single defined clinical profile across our 73 cataloged conditions.
                    </p>
                    <p class="text-muted small mb-0">
                        Try adding additional symptoms or exploring our <a href="symptoms_guide.php" class="text-info text-decoration-underline">Symptoms Guide</a>.
                    </p>
                </div>
            `;
            elements.resultsContainer.style.display = 'block';
            return;
        }

        // Selected summary
        const selectedSymNames = Array.from(state.selectedSymptoms).map((k) => {
            const s = state.symptoms.find((sym) => sym.key === k);
            return s ? s.name : k;
        });

        const durationText = {
            'less_1_day': 'Less than 24 hours',
            '1_3_days': '1–3 days',
            '4_7_days': '4–7 days',
            'more_1_week': 'More than 1 week',
            'more_2_weeks': 'More than 2 weeks'
        }[state.clinicalContext.duration] || '1–3 days';

        const severityText = {
            'mild': 'Mild',
            'moderate': 'Moderate',
            'severe': 'Severe'
        }[state.clinicalContext.severity] || 'Moderate';

        // Check for emergency red flags in selected symptoms or top condition
        renderEmergencyRedFlags(conditions);

        let html = `
            <!-- Symptom Analysis Summary Header -->
            <div class="card-custom p-4 mb-4 border-info">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h5 class="fw-bold mb-0 text-info">
                        <i class="bi bi-clipboard-pulse me-2"></i> Symptom Profile Summary
                    </h5>
                    <span class="badge bg-info bg-opacity-20 text-info border border-info border-opacity-25 px-3 py-1">
                        Educational Decision Support
                    </span>
                </div>
                <div class="row g-3">
                    <div class="col-md-6">
                        <div class="small text-muted mb-1">Evaluated Symptoms:</div>
                        <div class="d-flex flex-wrap gap-1">
                            ${selectedSymNames.map((n) => `<span class="badge bg-card-subtle text-info border">${escapeHtml(n)}</span>`).join('')}
                        </div>
                    </div>
                    <div class="col-6 col-md-3">
                        <div class="small text-muted mb-1">Reported Duration:</div>
                        <strong class="small">${escapeHtml(durationText)}</strong>
                    </div>
                    <div class="col-6 col-md-3">
                        <div class="small text-muted mb-1">Reported Severity:</div>
                        <strong class="small">${escapeHtml(severityText)}</strong>
                    </div>
                </div>
            </div>

            <!-- Overlapping Symptoms Advisory -->
            <div class="alert alert-info border-0 shadow-sm d-flex align-items-start gap-3 p-3 mb-4" style="background: rgba(18, 191, 227, 0.08); border-left: 4px solid var(--accent-primary) !important;">
                <i class="bi bi-info-circle-fill text-info fs-4 flex-shrink-0 mt-1"></i>
                <div class="small text-muted">
                    <strong class="text-primary-theme d-block mb-1">Clinical Note on Overlapping Symptoms:</strong>
                    Many illnesses share non-specific indicators (such as fever, fatigue, and headaches). The results below represent educational condition possibilities based on co-occurrence weighting, not a confirmed medical diagnosis.
                </div>
            </div>

            <div class="d-flex justify-content-between align-items-center mb-3">
                <h4 class="fw-bold mb-0">Possible Conditions to Consider</h4>
                <span class="text-muted small">${conditions.length} Relevant Conditions Evaluated</span>
            </div>

            <!-- Condition Cards -->
            <div class="condition-cards-stack">
        `;

        conditions.forEach((c, idx) => {
            const badgeClass = c.matchLevel === 'High'
                ? 'symptom-match-badge-high'
                : (c.matchLevel === 'Moderate' ? 'symptom-match-badge-moderate' : 'symptom-match-badge-limited');

            const scoreColor = c.matchLevel === 'High' ? 'text-success' : (c.matchLevel === 'Moderate' ? 'text-info' : 'text-muted');

            const matchedNames = c.matchedSymptoms.map((k) => {
                const s = state.symptoms.find((sym) => sym.key === k);
                return s ? s.name : k.replace(/_/g, ' ');
            });

            const otherNames = c.otherSymptoms.map((k) => {
                const s = state.symptoms.find((sym) => sym.key === k);
                return s ? s.name : k.replace(/_/g, ' ');
            });

            html += `
                <div class="card-custom p-4 mb-4 condition-card ${idx === 0 ? 'border-primary border-2 shadow' : ''}">
                    <div class="d-flex flex-wrap justify-content-between align-items-start gap-2 mb-3">
                        <div>
                            <span class="badge bg-secondary bg-opacity-25 text-muted border border-secondary border-opacity-25 small mb-1">
                                ${escapeHtml(c.category)}
                            </span>
                            <h3 class="fw-bold mb-1 d-flex align-items-center gap-2">
                                ${escapeHtml(c.name)}
                                ${idx === 0 ? '<span class="badge bg-info text-white fs-6">Top Match</span>' : ''}
                            </h3>
                        </div>
                        <div class="text-end">
                            <span class="${badgeClass} px-3 py-1 rounded-pill fw-bold small d-inline-block mb-1">
                                Symptom Match: ${escapeHtml(c.matchLevel)}
                            </span>
                            <div class="small fw-bold ${scoreColor}">
                                Match Score: ${c.score}/100
                            </div>
                        </div>
                    </div>

                    <p class="text-muted small mb-3">
                        ${escapeHtml(c.description)}
                    </p>

                    <div class="p-3 bg-card-subtle rounded-3 border mb-3">
                        <div class="row g-3">
                            <div class="col-md-6">
                                <div class="fw-bold small text-success mb-1">
                                    <i class="bi bi-check-circle-fill me-1"></i> Matched Symptoms:
                                </div>
                                <ul class="list-unstyled small mb-0 ps-1">
                                    ${matchedNames.map((n) => `<li class="text-muted"><i class="bi bi-check2 text-success me-1"></i> ${escapeHtml(n)}</li>`).join('')}
                                </ul>
                            </div>
                            <div class="col-md-6">
                                <div class="fw-bold small text-muted mb-1">
                                    <i class="bi bi-circle me-1"></i> Other Characteristic Signs:
                                </div>
                                <ul class="list-unstyled small mb-0 ps-1">
                                    ${otherNames.length > 0 ? otherNames.map((n) => `<li class="text-muted">• ${escapeHtml(n)}</li>`).join('') : '<li class="text-muted italic">All core signs reported</li>'}
                                </ul>
                            </div>
                        </div>
                    </div>

                    <!-- Accordion: Why this result appeared -->
                    <div class="accordion accordion-flush mb-3" id="accordion-${c.id}">
                        <div class="accordion-item bg-transparent border-0">
                            <h2 class="accordion-header" id="heading-${c.id}">
                                <button class="accordion-button collapsed bg-transparent p-0 small fw-bold text-info shadow-none" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-${c.id}">
                                    <i class="bi bi-question-circle me-1"></i> Why this condition appeared & distinguishing features
                                </button>
                            </h2>
                            <div id="collapse-${c.id}" class="accordion-collapse collapse" data-bs-parent="#accordion-${c.id}">
                                <div class="accordion-body px-0 pt-2 pb-0 small text-muted">
                                    <div class="mb-2">
                                        <strong class="text-primary-theme">Clinical Rationale:</strong>
                                        This condition was ranked because your selected symptoms (${matchedNames.join(', ')}) strongly overlap with documented clinical presentation patterns.
                                    </div>
                                    ${c.differentiating ? `<div class="mb-2"><strong class="text-primary-theme">Differentiating Traits:</strong> ${escapeHtml(c.differentiating)}</div>` : ''}
                                    ${c.whenToSeekCare ? `<div><strong class="text-primary-theme">When to Seek Care:</strong> ${escapeHtml(c.whenToSeekCare)}</div>` : ''}
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="d-flex flex-wrap justify-content-between align-items-center gap-2 pt-3 border-top mt-2">
                        <small class="text-muted" style="font-size: 0.75rem;">
                            <i class="bi bi-journal-medical me-1"></i> Source: ${escapeHtml(c.source)}
                        </small>
                        <a href="disease_detail.php?name=${encodeURIComponent(c.name)}" class="btn btn-sm btn-outline-info rounded-pill px-3 fw-semibold">
                            <i class="bi bi-book me-1"></i> Learn More About ${escapeHtml(c.name)}
                        </a>
                    </div>
                </div>
            `;
        });

        html += `
            </div>

            <!-- Disclaimer Banner -->
            <div class="disclaimer-banner p-4 text-start my-4">
                <h6 class="fw-bold mb-2 text-warning">
                    <i class="bi bi-shield-exclamation me-1"></i> Educational Decision Support Disclaimer
                </h6>
                <p class="small mb-0 text-muted">
                    This tool provides educational symptom-based information and does NOT provide a medical diagnosis. The match scores (e.g. ${conditions[0].score}/100) quantify statistical symptom overlap with standard educational clinical profiles, NOT the likelihood or probability of disease. Always consult a qualified healthcare professional for medical diagnosis and care.
                </p>
            </div>
        `;

        elements.resultsContainer.innerHTML = html;
        elements.resultsContainer.style.display = 'block';
    }

    /**
     * Render Emergency Red Flags
     */
    function renderEmergencyRedFlags(conditions) {
        if (!elements.emergencyContainer) return;

        const emergencyTriggerSymptoms = ['chest_pain', 'shortness_of_breath', 'hemoptysis', 'seizures', 'blood_in_urine'];
        const hasEmergencySymptom = Array.from(state.selectedSymptoms).some((k) => emergencyTriggerSymptoms.includes(k));

        const collectedFlags = [];
        conditions.forEach((c) => {
            if (c.redFlags && Array.isArray(c.redFlags)) {
                c.redFlags.forEach((rf) => {
                    if (!collectedFlags.includes(rf)) collectedFlags.push(rf);
                });
            }
        });

        if (hasEmergencySymptom || collectedFlags.length > 0) {
            elements.emergencyContainer.innerHTML = `
                <div class="card border-danger border-2 p-4 mb-4" style="background: rgba(220, 53, 69, 0.08);">
                    <div class="d-flex align-items-start gap-3">
                        <div class="text-danger fs-2 flex-shrink-0">
                            <i class="bi bi-exclamation-octagon-fill"></i>
                        </div>
                        <div class="flex-grow-1">
                            <h5 class="fw-bold text-danger mb-1">Seek Urgent Emergency Care If You Experience:</h5>
                            <ul class="text-muted small ps-3 mb-2">
                                ${collectedFlags.slice(0, 3).map((f) => `<li><strong>${escapeHtml(f)}</strong></li>`).join('')}
                            </ul>
                            <div class="d-flex flex-wrap gap-2 align-items-center mt-2">
                                <a href="emergency.php" class="btn btn-sm btn-danger rounded-pill px-3 fw-bold">
                                    <i class="bi bi-shield-fill-exclamation me-1"></i> Open Emergency Guide
                                </a>
                                <a href="tel:911" class="btn btn-sm btn-outline-danger rounded-pill px-3 fw-bold">
                                    <i class="bi bi-telephone-fill me-1"></i> Call 911 / Emergency
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            elements.emergencyContainer.style.display = 'block';
        } else {
            elements.emergencyContainer.style.display = 'none';
        }
    }

    /**
     * Render Personalized Follow-Up Questions (Phase 11)
     */
    function renderFollowUpQuestions() {
        if (!elements.refineContainer) return;

        const selected = state.selectedSymptoms;
        const questions = [];

        if (selected.has('cough_with_sputum') || selected.has('dry_cough')) {
            questions.push({
                id: 'cough_type',
                title: 'You selected cough. How would you describe it?',
                options: [
                    { value: 'dry', label: 'Dry and tickly (no mucus)' },
                    { value: 'with_phlegm', label: 'Productive with colored phlegm/mucus' },
                    { value: 'not_sure', label: 'Not sure' }
                ]
            });
        }

        if (selected.has('headache')) {
            questions.push({
                id: 'headache_location',
                title: 'Where is the headache centered?',
                options: [
                    { value: 'one_sided', label: 'One-sided, throbbing with light sensitivity' },
                    { value: 'band', label: 'Dull, band-like tension around the entire head' },
                    { value: 'sinus', label: 'Behind eyes and nasal sinuses' }
                ]
            });
        }

        if (selected.has('fever')) {
            questions.push({
                id: 'fever_temp',
                title: 'What is your approximate body temperature?',
                options: [
                    { value: 'mild', label: 'Low grade (< 100.4°F / 38°C)' },
                    { value: 'moderate', label: '100.4°F – 102°F (38°C – 38.9°C)' },
                    { value: 'high', label: 'High fever (> 102°F / 39°C)' }
                ]
            });
        }

        if (selected.has('skin_rash') || selected.has('itching')) {
            questions.push({
                id: 'rash_character',
                title: 'What best describes the skin appearance?',
                options: [
                    { value: 'flaky', label: 'Dry, red, flaking patches' },
                    { value: 'wheals', label: 'Raised, itchy hives or welts' },
                    { value: 'pimples', label: 'Acne-like pustules or blackheads' }
                ]
            });
        }

        if (questions.length === 0) {
            elements.refineContainer.style.display = 'none';
            return;
        }

        elements.refineContainer.innerHTML = `
            <div class="card-custom p-4 mb-4 border-info">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h5 class="fw-bold mb-0 text-info">
                        <i class="bi bi-sliders me-2"></i> Refine Your Assessment
                    </h5>
                    <span class="badge bg-info bg-opacity-10 text-info border border-info border-opacity-25 small">
                        Personalized Clinical Questions
                    </span>
                </div>
                <p class="small text-muted mb-3">
                    Answering these targeted follow-up questions helps differentiate overlapping conditions:
                </p>
                <div class="row g-3">
                    ${questions.slice(0, 2).map((q) => `
                        <div class="col-md-6">
                            <div class="p-3 bg-card-subtle rounded-3 border h-100">
                                <h6 class="fw-bold small mb-2">${escapeHtml(q.title)}</h6>
                                <div class="d-flex flex-column gap-2">
                                    ${q.options.map((opt) => {
                                        const isChecked = state.followUpAnswers[q.id] === opt.value;
                                        return `
                                            <button type="button" class="btn btn-sm text-start py-2 px-3 refine-option-btn ${isChecked ? 'btn-info text-white fw-bold' : 'btn-outline-secondary'}" data-qid="${q.id}" data-val="${opt.value}">
                                                <i class="bi ${isChecked ? 'bi-check-circle-fill me-1' : 'bi-circle me-1'}"></i>
                                                ${escapeHtml(opt.label)}
                                            </button>
                                        `;
                                    }).join('')}
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;

        elements.refineContainer.querySelectorAll('.refine-option-btn').forEach((btn) => {
            btn.addEventListener('click', () => {
                const qid = btn.dataset.qid;
                const val = btn.dataset.val;
                state.followUpAnswers[qid] = val;

                // Re-run prediction with updated refinements
                const updatedConditions = runPrediction();
                state.currentAnalysis = updatedConditions;
                renderResults(updatedConditions);
                renderFollowUpQuestions();
            });
        });

        elements.refineContainer.style.display = 'block';
    }

    /**
     * Record Prediction to Backend Database
     */
    async function recordPredictionHistory(topCondition) {
        try {
            await fetch('api/record_prediction.php', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    symptoms: Array.from(state.selectedSymptoms),
                    top_condition: topCondition.name,
                    score: topCondition.score
                })
            });
        } catch (e) {
            // Silently bypass history logging errors
        }
    }

    function escapeHtml(str) {
        if (!str) return '';
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    // Auto-initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
