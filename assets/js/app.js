// Client-side Interactive Logic & Dynamics

document.addEventListener('DOMContentLoaded', function () {
    // Dynamic Form Switcher on Assessment Page
    const diseaseSelector = document.getElementById('disease_type');
    const diabetesFields = document.getElementById('diabetes_fields');
    const heartFields = document.getElementById('heart_fields');

    if (diseaseSelector && diabetesFields && heartFields) {
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
                if (enable) {
                    input.removeAttribute('disabled');
                } else {
                    input.setAttribute('disabled', 'disabled');
                }
            });
        }

        diseaseSelector.addEventListener('change', toggleFields);
        toggleFields(); // Initial state
    }

    // Dynamic Range Slider Output Synchronization
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
});
