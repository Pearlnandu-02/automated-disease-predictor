<?php
// health_assistant.php - AI Health Assistant (Section 4)
require_once __DIR__ . '/includes/auth.php';
require_once __DIR__ . '/includes/functions.php';

$page_title = 'MediSense AI | AI Health Assistant';
require_once __DIR__ . '/includes/header.php';
?>

<div class="row justify-content-center py-3">
    <div class="col-lg-10 col-xl-9">
        <!-- Assistant Hero Card -->
        <div class="card-custom p-4 mb-3 hero-banner">
            <div class="d-flex justify-content-between align-items-center flex-wrap gap-2">
                <div class="d-flex align-items-center gap-3">
                    <div class="p-3 bg-info bg-opacity-20 text-info rounded-circle fs-3">
                        <i class="bi bi-chat-heart-fill"></i>
                    </div>
                    <div>
                        <span class="badge hero-badge px-3 py-1 mb-1 fw-bold">Educational Health Companion</span>
                        <h2 class="fw-bold hero-heading mb-0">MediSense AI Health Assistant</h2>
                        <p class="hero-lead mb-0 small">Ask questions about medical conditions, symptoms, wellness habits, and preventive health.</p>
                    </div>
                </div>
                <div class="d-flex align-items-center gap-2">
                    <span class="badge bg-success bg-opacity-20 text-success border border-success border-opacity-25 px-3 py-2 rounded-pill small">
                        <i class="bi bi-circle-fill me-1" style="font-size: 0.55rem;"></i> Active • Educational Mode
                    </span>
                    <button type="button" class="btn btn-outline-danger btn-sm rounded-pill px-3 py-1" id="btnClearChat" title="Clear conversation history">
                        <i class="bi bi-trash3 me-1"></i> Clear Chat
                    </button>
                </div>
            </div>
        </div>

        <!-- Chat Container Card -->
        <div class="card-custom p-0 mb-3 shadow-lg border overflow-hidden d-flex flex-column" style="height: 620px;">
            <!-- Chat Message Stream -->
            <div id="chatMessagesStream" class="flex-grow-1 p-4 overflow-y-auto" style="background: var(--bg-secondary, #0f172a);">
                <!-- Initial Welcome Message from Assistant -->
                <div class="chat-message-row d-flex gap-3 mb-4 assistant-row">
                    <div class="chat-avatar flex-shrink-0">
                        <div class="p-2 rounded-circle bg-info bg-opacity-20 text-info d-flex align-items-center justify-content-center" style="width: 42px; height: 42px;">
                            <i class="bi bi-robot fs-5"></i>
                        </div>
                    </div>
                    <div class="chat-bubble-content flex-grow-1">
                        <div class="p-3 rounded-4 border bg-card text-body shadow-sm" style="max-width: 85%;">
                            <div class="d-flex justify-content-between align-items-center mb-1">
                                <strong class="text-info small"><i class="bi bi-shield-check me-1"></i> MediSense Assistant</strong>
                                <span class="small text-muted" style="font-size: 0.7rem;">Just now</span>
                            </div>
                            <p class="mb-2">
                                Hello! I am your <strong>MediSense AI Health Assistant</strong>. I am trained to provide reliable educational insights on symptoms, common diseases, lifestyle choices, and preventive healthcare.
                            </p>
                            <p class="mb-2 text-muted small">
                                Feel free to type any health question or select from the suggested prompts below.
                            </p>
                            <div class="p-2 rounded-3 bg-secondary-subtle small border border-secondary border-opacity-10 text-muted" style="font-size: 0.78rem;">
                                <i class="bi bi-info-circle-fill text-info me-1"></i>
                                <em>Medical Notice: This assistant provides educational guidance and is not a substitute for professional medical diagnosis or personalized clinical consultation.</em>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Typing Indicator (Hidden by default) -->
            <div id="typingIndicator" class="px-4 py-2 border-top d-none" style="background: var(--bg-secondary);">
                <div class="d-flex align-items-center gap-2 text-muted small">
                    <div class="spinner-grow spinner-grow-sm text-info" role="status" style="width: 0.75rem; height: 0.75rem;"></div>
                    <span>MediSense Assistant is synthesizing educational response...</span>
                </div>
            </div>

            <!-- Suggested Quick Questions Chips (Section 4) -->
            <div class="px-3 pt-2 pb-1 border-top bg-card-subtle">
                <div class="d-flex align-items-center gap-2 overflow-x-auto py-1" style="white-space: nowrap;">
                    <span class="small text-muted flex-shrink-0" style="font-size: 0.75rem;"><i class="bi bi-stars text-warning me-1"></i>Suggested:</span>
                    <button type="button" class="btn btn-sm btn-outline-info rounded-pill py-1 px-3 quick-chip" data-prompt="What are common symptoms of diabetes?">
                        What are common symptoms of diabetes?
                    </button>
                    <button type="button" class="btn btn-sm btn-outline-info rounded-pill py-1 px-3 quick-chip" data-prompt="What are warning signs of high blood pressure?">
                        What are warning signs of high blood pressure?
                    </button>
                    <button type="button" class="btn btn-sm btn-outline-info rounded-pill py-1 px-3 quick-chip" data-prompt="How can I improve my sleep?">
                        How can I improve my sleep?
                    </button>
                    <button type="button" class="btn btn-sm btn-outline-info rounded-pill py-1 px-3 quick-chip" data-prompt="What are common causes of fever?">
                        What are common causes of fever?
                    </button>
                    <button type="button" class="btn btn-sm btn-outline-info rounded-pill py-1 px-3 quick-chip" data-prompt="When should I see a doctor?">
                        When should I see a doctor?
                    </button>
                </div>
            </div>

            <!-- Input Bar -->
            <div class="p-3 border-top bg-card">
                <form id="chatForm" class="d-flex gap-2 align-items-center">
                    <input type="text" id="chatInput" class="form-control rounded-pill px-4 py-2" placeholder="Ask a health question (e.g., 'How can I lower blood pressure naturally?')..." autocomplete="off" required>
                    <button type="submit" id="btnSendChat" class="btn btn-primary-custom rounded-pill px-4 py-2 flex-shrink-0 d-flex align-items-center gap-2">
                        <span>Send</span>
                        <i class="bi bi-send-fill"></i>
                    </button>
                </form>
            </div>
        </div>

        <!-- Strict Medical Disclaimer Banner -->
        <div class="alert alert-secondary py-2 px-3 small border rounded-3 text-muted text-center" style="font-size: 0.8rem;">
            <i class="bi bi-shield-exclamation text-warning me-1"></i>
            <strong>Important Medical Disclaimer:</strong> MediSense AI Assistant is designed exclusively for educational information and general health literacy. It <strong>does not diagnose diseases, prescribe pharmaceuticals, or dictate medical treatments</strong>. Symptoms alone cannot confirm medical certainty. If you are experiencing a life-threatening medical emergency (such as severe chest pain, stroke symptoms, or severe shortness of breath), immediately call your local emergency dispatch (911 / 112).
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const chatStream = document.getElementById('chatMessagesStream');
    const chatForm = document.getElementById('chatForm');
    const chatInput = document.getElementById('chatInput');
    const btnClearChat = document.getElementById('btnClearChat');
    const typingIndicator = document.getElementById('typingIndicator');
    const quickChips = document.querySelectorAll('.quick-chip');

    // Load session history from sessionStorage if available
    loadChatHistory();

    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const query = chatInput.value.trim();
        if (!query) return;

        appendUserMessage(query);
        chatInput.value = '';
        saveChatHistory();

        // Show typing indicator
        typingIndicator.classList.remove('d-none');
        chatStream.scrollTop = chatStream.scrollHeight;

        setTimeout(function() {
            typingIndicator.classList.add('d-none');
            const responseData = generateEducationalResponse(query);
            appendAssistantMessage(responseData);
            saveChatHistory();
        }, 650);
    });

    quickChips.forEach(chip => {
        chip.addEventListener('click', function() {
            const prompt = this.getAttribute('data-prompt');
            chatInput.value = prompt;
            chatForm.dispatchEvent(new Event('submit'));
        });
    });

    btnClearChat.addEventListener('click', function() {
        if (confirm('Clear the current conversation history?')) {
            sessionStorage.removeItem('medisense_chat_history');
            location.reload();
        }
    });

    function appendUserMessage(text) {
        const row = document.createElement('div');
        row.className = 'chat-message-row d-flex justify-content-end gap-3 mb-4 user-row';
        row.innerHTML = `
            <div class="chat-bubble-content" style="max-width: 80%;">
                <div class="p-3 rounded-4 bg-info text-white shadow-sm" style="border-bottom-right-radius: 4px;">
                    <div class="d-flex justify-content-between align-items-center mb-1">
                        <strong class="small text-white-50">You</strong>
                        <span class="small text-white-50" style="font-size: 0.7rem;">${formatTime(new Date())}</span>
                    </div>
                    <div class="mb-0 text-white">${escapeHtml(text)}</div>
                </div>
            </div>
            <div class="chat-avatar flex-shrink-0">
                <div class="p-2 rounded-circle bg-secondary bg-opacity-25 text-body d-flex align-items-center justify-content-center" style="width: 42px; height: 42px;">
                    <i class="bi bi-person-fill fs-5"></i>
                </div>
            </div>
        `;
        chatStream.appendChild(row);
        chatStream.scrollTop = chatStream.scrollHeight;
    }

    function appendAssistantMessage(data) {
        const row = document.createElement('div');
        row.className = 'chat-message-row d-flex gap-3 mb-4 assistant-row';
        row.innerHTML = `
            <div class="chat-avatar flex-shrink-0">
                <div class="p-2 rounded-circle bg-info bg-opacity-20 text-info d-flex align-items-center justify-content-center" style="width: 42px; height: 42px;">
                    <i class="bi bi-robot fs-5"></i>
                </div>
            </div>
            <div class="chat-bubble-content flex-grow-1" style="max-width: 85%;">
                <div class="p-3 rounded-4 border bg-card text-body shadow-sm" style="border-bottom-left-radius: 4px;">
                    <div class="d-flex justify-content-between align-items-center mb-1">
                        <strong class="text-info small"><i class="bi bi-shield-check me-1"></i> MediSense Assistant</strong>
                        <span class="small text-muted" style="font-size: 0.7rem;">${formatTime(new Date())}</span>
                    </div>
                    <div class="mb-2">${data.content}</div>
                    ${data.actionLink ? `
                    <div class="mt-2 pt-2 border-top">
                        <a href="${data.actionLink.url}" class="btn btn-sm btn-outline-info rounded-pill py-1 px-3">
                            ${data.actionLink.label} &rarr;
                        </a>
                    </div>
                    ` : ''}
                    <div class="mt-2 text-muted" style="font-size: 0.72rem;">
                        <i class="bi bi-info-circle me-1"></i> Educational guidance only • Not a medical diagnosis
                    </div>
                </div>
            </div>
        `;
        chatStream.appendChild(row);
        chatStream.scrollTop = chatStream.scrollHeight;
    }

    // Comprehensive Rule-Based Educational Knowledge Engine
    function generateEducationalResponse(query) {
        const q = query.toLowerCase();

        // 1. Diabetes
        if (q.includes('diabetes') || q.includes('blood sugar') || q.includes('glucose')) {
            return {
                content: `
                    <h6 class="fw-bold text-info mb-2"><i class="bi bi-droplet-half me-1"></i> Common Symptoms of Diabetes</h6>
                    <p class="mb-2">Type 2 Diabetes often develops gradually. Classic early indicators include:</p>
                    <ul class="small mb-2 ps-3">
                        <li><strong>Polyuria:</strong> Frequent urination, especially waking multiple times at night.</li>
                        <li><strong>Polydipsia:</strong> Excessive, unquenchable thirst despite regular fluid intake.</li>
                        <li><strong>Unexplained Fatigue:</strong> Cellular energy depletion due to impaired glucose uptake.</li>
                        <li><strong>Blurred Vision:</strong> Fluid shifts affecting the lens of the eye.</li>
                        <li><strong>Slow-Healing Wounds:</strong> Impaired peripheral microcirculation and immune response.</li>
                        <li><strong>Paresthesias:</strong> Numbness, tingling, or "pins and needles" in feet or hands.</li>
                    </ul>
                    <p class="small text-muted mb-0"><strong>Recommended action:</strong> Ask your healthcare provider for a fasting blood glucose test or HbA1c test if experiencing persistent symptoms.</p>
                `,
                actionLink: { url: 'disease_detail.php?id=1', label: 'View Full Diabetes Profile' }
            };
        }

        // 2. Hypertension / High Blood Pressure
        if (q.includes('blood pressure') || q.includes('hypertension') || q.includes('bp')) {
            return {
                content: `
                    <h6 class="fw-bold text-danger mb-2"><i class="bi bi-heart-pulse-fill me-1"></i> High Blood Pressure (Hypertension) Warning Signs</h6>
                    <p class="mb-2">Hypertension is often called a <em>"silent condition"</em> because mild or moderate elevations typically produce <strong>no noticeable symptoms</strong>. When blood pressure reaches dangerously high levels (Hypertensive Crisis, >180/120 mm Hg), warning signs include:</p>
                    <ul class="small mb-2 ps-3">
                        <li><strong>Severe Occipital Headache:</strong> Throbbing headache primarily located at the back of the head.</li>
                        <li><strong>Vision Disturbances:</strong> Blurred vision, double vision, or temporary loss of focus.</li>
                        <li><strong>Chest Tightness / Dyspnea:</strong> Heaviness across chest or shortness of breath on mild exertion.</li>
                        <li><strong>Dizziness / Lightheadedness:</strong> Feeling faint upon standing.</li>
                        <li><strong>Nosebleeds (Epistaxis):</strong> Unprovoked recurrent nasal bleeding.</li>
                    </ul>
                    <p class="small text-muted mb-0"><strong>Clinical Guideline:</strong> Normal resting blood pressure is under 120/80 mm Hg. Periodic monitoring is recommended.</p>
                `,
                actionLink: { url: 'disease_detail.php?id=2', label: 'View Hypertension Guide' }
            };
        }

        // 3. Sleep Improvement
        if (q.includes('sleep') || q.includes('insomnia') || q.includes('tired') || q.includes('rest')) {
            return {
                content: `
                    <h6 class="fw-bold text-primary mb-2"><i class="bi bi-moon-stars-fill me-1"></i> Evidence-Based Sleep Hygiene Protocol</h6>
                    <p class="mb-2">Restorative sleep (7–9 hours nightly) directly supports endocrine, cardiovascular, and immune health. Key clinical practices:</p>
                    <ul class="small mb-2 ps-3">
                        <li><strong>Consistent Sleep Schedule:</strong> Wake up and sleep at the exact same times every day (even on weekends) to anchor circadian rhythm.</li>
                        <li><strong>Cool Bedroom Environment:</strong> Maintain a bedroom temperature between 16°C and 19°C (60°F - 67°F) to support natural core body cooling.</li>
                        <li><strong>Digital Wind-Down:</strong> Eliminate blue-light emitting screens (phones, tablets, laptops) at least 60 minutes before bedtime.</li>
                        <li><strong>Caffeine Curfew:</strong> Avoid caffeinated beverages (coffee, energy drinks, teas) after 2:00 PM due to a 5-7 hour metabolic half-life.</li>
                        <li><strong>Natural Morning Light:</strong> Get 15–30 minutes of natural outdoor sunlight within an hour of waking to signal cortisol release and nighttime melatonin production.</li>
                    </ul>
                `,
                actionLink: { url: 'prevention.php#sleep', label: 'Explore Sleep Prevention Guide' }
            };
        }

        // 4. Fever Causes & Care
        if (q.includes('fever') || q.includes('temperature') || q.includes('chills') || q.includes('pyrexia')) {
            return {
                content: `
                    <h6 class="fw-bold text-warning mb-2"><i class="bi bi-thermometer-high me-1"></i> Causes and Care for Fever</h6>
                    <p class="mb-2">A fever (body temperature > 38°C or 100.4°F) is an adaptive physiological immune defense mechanism. Common causes:</p>
                    <ul class="small mb-2 ps-3">
                        <li><strong>Viral Infections:</strong> Upper respiratory tract viral infections (rhinovirus, influenza, COVID-19, RSV).</li>
                        <li><strong>Bacterial Infections:</strong> Streptococcal pharyngitis, urinary tract infections, pneumonia, or ear infections.</li>
                        <li><strong>Inflammatory Conditions:</strong> Autoimmune flares or heat-related illnesses.</li>
                    </ul>
                    <div class="alert alert-warning py-2 px-3 small border-0 rounded-3 mb-2">
                        <strong>Red Flags:</strong> Seek immediate medical care if fever exceeds 39.4°C (103°F), persists beyond 72 hours, or is accompanied by a stiff neck, confusion, breathing difficulty, or rash.
                    </div>
                `,
                actionLink: { url: 'diseases.php?search=Fever', label: 'Learn More in Disease Library' }
            };
        }

        // 5. When to see a doctor
        if (q.includes('doctor') || q.includes('hospital') || q.includes('emergency') || q.includes('when to see')) {
            return {
                content: `
                    <h6 class="fw-bold text-danger mb-2"><i class="bi bi-hospital me-1"></i> When to Seek Medical Attention</h6>
                    <div class="row g-2 mb-2">
                        <div class="col-12">
                            <div class="p-2 rounded border border-danger bg-danger bg-opacity-10 small">
                                <strong class="text-danger d-block mb-1">🚨 Immediate Emergency Care (Call 911 / 112):</strong>
                                <ul class="mb-0 ps-3">
                                    <li>Sudden crushing chest pain radiating to left arm, neck, or jaw.</li>
                                    <li>Signs of stroke (FAST: Face drooping, Arm weakness, Speech slurring).</li>
                                    <li>Severe difficulty breathing or blue/pale lips.</li>
                                    <li>Sudden loss of consciousness or severe head trauma.</li>
                                </ul>
                            </div>
                        </div>
                        <div class="col-12">
                            <div class="p-2 rounded border border-warning bg-warning bg-opacity-10 small">
                                <strong class="text-warning-emphasis d-block mb-1">⚠️ Urgent Same-Day Physician Consultation:</strong>
                                <ul class="mb-0 ps-3">
                                    <li>High fever lasting more than 3 consecutive days.</li>
                                    <li>Inability to keep liquids down due to vomiting (>24 hours).</li>
                                    <li>Unexplained rapid weight loss or persistent swollen lymph nodes.</li>
                                    <li>Skin lesions that are bleeding, growing, or changing color.</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                `,
                actionLink: { url: 'emergency.php', label: 'View Emergency Red-Flag Guide' }
            };
        }

        // 6. Injury / Wound / Skin
        if (q.includes('wound') || q.includes('cut') || q.includes('burn') || q.includes('skin') || q.includes('rash') || q.includes('lesion') || q.includes('mole')) {
            return {
                content: `
                    <h6 class="fw-bold text-info mb-2"><i class="bi bi-bandaid me-1"></i> Superficial Skin & Injury First Aid</h6>
                    <p class="mb-2">For minor superficial wounds and skin concerns:</p>
                    <ul class="small mb-2 ps-3">
                        <li><strong>Clean Gently:</strong> Rinse with cool or lukewarm potable water and mild soap. Avoid harsh alcohol or hydrogen peroxide on open tissue.</li>
                        <li><strong>Apply Pressure:</strong> Use a clean cloth or sterile gauze to control minor bleeding.</li>
                        <li><strong>Moisture Barrier:</strong> Apply a thin layer of sterile petroleum jelly or antibiotic ointment and cover with a breathable bandage.</li>
                        <li><strong>Concerning Skin Lesions:</strong> Inspect suspicious moles using the ABCDE criteria (Asymmetry, Border, Color, Diameter >6mm, Evolving). Never attempt to cut or scrape lesions at home.</li>
                    </ul>
                `,
                actionLink: { url: 'image_scanner.php', label: 'Open Injury Scanner' }
            };
        }

        // 7. General Fallback
        return {
            content: `
                <p class="mb-2">Thank you for your question. While I cannot diagnose specific symptoms or prescribe medication, here are general educational principles relevant to your inquiry:</p>
                <ul class="small mb-2 ps-3">
                    <li><strong>Symptom Timeline:</strong> Pay attention to when symptoms began, whether they are worsening, and what factors relieve or aggravate them.</li>
                    <li><strong>Vital Signs:</strong> Objective metrics like temperature, blood pressure, resting pulse, and oxygen saturation offer important clinical clues.</li>
                    <li><strong>Primary Care:</strong> For persistent, recurring, or distressing symptoms, scheduling an evaluation with a certified general practitioner or specialist is always the safest course of action.</li>
                </ul>
                <p class="small text-muted mb-0">Would you like to check specific symptoms using our AI Symptom Checker or explore a condition in the Disease Library?</p>
            `,
            actionLink: { url: 'prediction.php', label: 'Run AI Symptom Checker' }
        };
    }

    function formatTime(date) {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    function escapeHtml(str) {
        return String(str).replace(/[&<>"']/g, function(m) {
            return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m];
        });
    }

    function saveChatHistory() {
        try {
            sessionStorage.setItem('medisense_chat_history', chatStream.innerHTML);
        } catch(e) {}
    }

    function loadChatHistory() {
        try {
            const saved = sessionStorage.getItem('medisense_chat_history');
            if (saved && saved.trim().length > 50) {
                chatStream.innerHTML = saved;
                chatStream.scrollTop = chatStream.scrollHeight;
            }
        } catch(e) {}
    }
});
</script>

<?php require_once __DIR__ . '/includes/footer.php'; ?>
