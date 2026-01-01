const form = document.getElementById('diabetesForm');
const loading = document.getElementById('loading');
const resultDiv = document.getElementById('result');
const analyzeBtn = document.getElementById('analyzeBtn');

form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const features = {
        pregnancies: parseInt(document.getElementById('pregnancies').value),
        glucose: parseInt(document.getElementById('glucose').value),
        blood_pressure: parseInt(document.getElementById('blood_pressure').value),
        skin_thickness: parseInt(document.getElementById('skin_thickness').value),
        insulin: parseInt(document.getElementById('insulin').value),
        bmi: parseFloat(document.getElementById('bmi').value),
        diabetes_pedigree: parseFloat(document.getElementById('diabetes_pedigree').value),
        age: parseInt(document.getElementById('age').value)
    };

    analyzeBtn.disabled = true;
    loading.style.display = 'flex';
    resultDiv.style.display = 'none';

    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ features: features })
        });

        const data = await response.json();

        if (data.success) {
            displayResult(data.result);
        } else {
            displayError(data.error || 'Unknown error');
        }
    } catch (error) {
        displayError(error.message);
    } finally {
        analyzeBtn.disabled = false;
        loading.style.display = 'none';
    }
});

function displayResult(result) {
    const isDiabetic = result.result === 'DIABETES DETECTED';
    const isError = result.result === 'ERROR';

    if (isError) {
        displayError(result.error || 'Analysis failed');
        return;
    }

    const iconClass = isDiabetic ? 'error' : 'success';
    const titleClass = isDiabetic ? 'error' : 'success';
    const icon = isDiabetic ? '⚠️' : '✓';

    resultDiv.innerHTML = `
        <div class="result-container">
            <div class="result-icon ${iconClass}">${icon}</div>
            <div class="result-title ${titleClass}">${result.result}</div>
            <div class="risk-badge">${result.risk_level}</div>

            <div class="stats-grid">
                <div class="stat-box">
                    <div class="stat-label">CONFIDENCE</div>
                    <div class="stat-value">${Math.round(result.confidence)}%</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">DIABETES RISK</div>
                    <div class="stat-value red">${Math.round(result.diabetes_probability)}%</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">HEALTHY</div>
                    <div class="stat-value green">${Math.round(result.no_diabetes_probability)}%</div>
                </div>
            </div>

            <div class="info-box">
                <div class="info-box-title">ℹ️ Important Information</div>
                <div class="info-box-text">
                    This AI analysis is for screening purposes only. For accurate diagnosis, please consult with a healthcare professional and undergo proper medical testing.
                </div>
            </div>
        </div>
    `;

    resultDiv.style.display = 'flex';
}

function displayError(errorMessage) {
    resultDiv.innerHTML = `
        <div class="result-container">
            <div class="result-icon error">⚠️</div>
            <div class="result-title error">ERROR</div>
            <div class="risk-badge">UNKNOWN</div>

            <div class="stats-grid">
                <div class="stat-box">
                    <div class="stat-label">CONFIDENCE</div>
                    <div class="stat-value">0%</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">DIABETES RISK</div>
                    <div class="stat-value red">0%</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">HEALTHY</div>
                    <div class="stat-value green">0%</div>
                </div>
            </div>

            <div class="info-box">
                <div class="info-box-title">⚠️ Error Details</div>
                <div class="info-box-text">
                    ${errorMessage}
                </div>
            </div>
        </div>
    `;

    resultDiv.style.display = 'flex';
}
