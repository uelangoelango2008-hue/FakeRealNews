document.addEventListener('DOMContentLoaded', function () {
    const newsTextarea = document.getElementById('news');
    const wordCountSpan = document.getElementById('wordCount');
    const charCountSpan = document.getElementById('charCount');
    const btnRealSample = document.getElementById('btnRealSample');
    const btnFakeSample = document.getElementById('btnFakeSample');
    const btnClear = document.getElementById('btnClear');
    const predictionForm = document.getElementById('predictionForm');
    const btnSubmit = document.getElementById('btnSubmit');

    // Benchmark sample news from the PBL project report
    const REAL_SAMPLE_TEXT = "The Tamil Nadu government has approached the Supreme Court seeking directions against Karnataka for not fully complying with the Cauvery Water Management Authority's order to release water. The state has also requested compensation for the reported shortfall in water release.";

    const FAKE_SAMPLE_TEXT = "Tamil Nadu Chief Minister announced that actor Ajith Kumar will become the Minister for Sports and Motorsports from next week.";

    // Update word and character counts dynamically
    function updateCounts() {
        if (!newsTextarea) return;
        const text = newsTextarea.value.trim();
        const chars = newsTextarea.value.length;
        const words = text ? text.split(/\s+/).length : 0;

        if (wordCountSpan) {
            wordCountSpan.textContent = words + (words === 1 ? ' word' : ' words');
        }
        if (charCountSpan) {
            charCountSpan.textContent = chars + (chars === 1 ? ' character' : ' characters');
        }
    }

    if (newsTextarea) {
        newsTextarea.addEventListener('input', updateCounts);
        updateCounts();
    }

    // Load Real News Sample
    if (btnRealSample) {
        btnRealSample.addEventListener('click', function () {
            newsTextarea.value = REAL_SAMPLE_TEXT;
            updateCounts();
            newsTextarea.focus();
        });
    }

    // Load Fake News Sample
    if (btnFakeSample) {
        btnFakeSample.addEventListener('click', function () {
            newsTextarea.value = FAKE_SAMPLE_TEXT;
            updateCounts();
            newsTextarea.focus();
        });
    }

    // Clear form and results
    if (btnClear) {
        btnClear.addEventListener('click', function () {
            newsTextarea.value = '';
            updateCounts();

            // Clear any displayed results or alerts
            const resultSection = document.getElementById('resultSection');
            if (resultSection) {
                resultSection.remove();
            }
            const alertBox = document.querySelector('.alert');
            if (alertBox) {
                alertBox.remove();
            }

            newsTextarea.focus();
        });
    }

    // Button loading state on submit
    if (predictionForm && btnSubmit) {
        predictionForm.addEventListener('submit', function () {
            btnSubmit.innerHTML = '<span>Processing & Predicting...</span>';
            btnSubmit.style.opacity = '0.8';
        });
    }
});
