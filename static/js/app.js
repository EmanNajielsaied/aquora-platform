/**
 * PowerGuard Predictive Maintenance Web Dashboard Logic
 * Dynamically builds form, handles presets, invokes FastAPI prediction API, and animates results.
 */

document.addEventListener('DOMContentLoaded', () => {
    let schemaData = null;
    let currentActiveTab = 'group_infrastructure';

    // UI Element references
    const categoryTabsContainer = document.getElementById('category-tabs');
    const sectionsContainer = document.getElementById('sections-container');
    const predictionForm = document.getElementById('prediction-form');
    const btnSubmit = document.getElementById('btn-submit-prediction');
    
    // Result elements
    const resultsCard = document.getElementById('results-card');
    const resultProbability = document.getElementById('result-probability');
    const resultBanner = document.getElementById('result-banner');
    const statusTitle = document.getElementById('status-title');
    const statusIcon = document.getElementById('status-icon');
    const riskBadge = document.getElementById('risk-badge');
    const gaugeFill = document.getElementById('gauge-fill');
    const gaugeNeedle = document.getElementById('gauge-needle');
    
    // Indicators
    const indAge = document.getElementById('ind-age');
    const indPressureDev = document.getElementById('ind-pressure-dev');
    const indVibRms = document.getElementById('ind-vib-rms');
    const indRiskScore = document.getElementById('ind-risk-score');

    // Modal elements
    const btnArchitectureModal = document.getElementById('btn-architecture-modal');
    const btnCloseModal = document.getElementById('btn-close-modal');
    const architectureModal = document.getElementById('architecture-modal');

    // 1. Fetch Schema from API
    async function initApp() {
        try {
            const response = await fetch('/api/schema');
            if (!response.ok) {
                throw new Error(`Failed to load API schema: ${response.statusText}`);
            }
            schemaData = await response.json();
            
            // Build UI
            renderCategoryTabs(schemaData.feature_groups);
            renderFeatureSections(schemaData);
            
            // Load Normal Preset by default
            loadPreset('normal');

            setupEventListeners();
        } catch (error) {
            console.error('Initialization error:', error);
            alert(`Error initializing PowerGuard dashboard: ${error.message}`);
        }
    }

    // 2. Render Category Navigation Tabs
    function renderCategoryTabs(featureGroups) {
        categoryTabsContainer.innerHTML = '';
        featureGroups.forEach((group, index) => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = `tab-btn ${index === 0 ? 'active' : ''}`;
            btn.dataset.groupId = group.id;
            btn.innerHTML = `<i class="fa-solid fa-folder"></i> ${group.title}`;
            
            btn.addEventListener('click', () => switchTab(group.id));
            categoryTabsContainer.appendChild(btn);
        });
    }

    // Switch Active Tab
    function switchTab(groupId) {
        currentActiveTab = groupId;
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.groupId === groupId);
        });
        document.querySelectorAll('.section-card').forEach(sec => {
            sec.classList.toggle('active', sec.dataset.groupId === groupId);
        });
    }

    // 3. Render Form Sections & Input Fields
    function renderFeatureSections(schema) {
        sectionsContainer.innerHTML = '';
        
        schema.feature_groups.forEach((group, index) => {
            const secCard = document.createElement('div');
            secCard.className = `section-card ${index === 0 ? 'active' : ''}`;
            secCard.dataset.groupId = group.id;

            const headerBox = document.createElement('div');
            headerBox.className = 'section-header-box';
            headerBox.innerHTML = `
                <h3>${group.title}</h3>
                <p>${group.description}</p>
            `;
            secCard.appendChild(headerBox);

            const grid = document.createElement('div');
            grid.className = 'fields-grid';

            group.features.forEach(featName => {
                const fieldGroup = createInputField(featName, schema);
                grid.appendChild(fieldGroup);
            });

            secCard.appendChild(grid);
            sectionsContainer.appendChild(secCard);
        });
    }

    // Helper: Create single input control (select or number input)
    function createInputField(featName, schema) {
        const div = document.createElement('div');
        div.className = 'field-group';

        const label = document.createElement('label');
        label.className = 'field-label';
        label.htmlFor = `input_${featName}`;
        
        const cleanTitle = featName.replace(/_/g, ' ');
        const unitText = getUnitForFeature(featName);
        label.innerHTML = `<span>${cleanTitle}</span> ${unitText ? `<span class="field-unit">${unitText}</span>` : ''}`;

        div.appendChild(label);

        if (schema.categorical_features.includes(featName)) {
            // Dropdown select for categorical
            const select = document.createElement('select');
            select.id = `input_${featName}`;
            select.name = featName;
            select.className = 'form-select';
            
            const options = schema.categorical_values[featName] || [];
            options.forEach(opt => {
                const optionEl = document.createElement('option');
                optionEl.value = opt;
                optionEl.textContent = opt;
                select.appendChild(optionEl);
            });
            div.appendChild(select);
        } else {
            // Number input for numeric
            const input = document.createElement('input');
            input.type = 'number';
            input.id = `input_${featName}`;
            input.name = featName;
            input.className = 'form-input';
            input.step = getStepForFeature(featName);
            input.value = '0';
            div.appendChild(input);
        }

        return div;
    }

    // Helper: Step size for number inputs
    function getStepForFeature(feat) {
        if (feat.includes('Year') || feat.includes('Month') || feat.includes('Day') || feat.includes('Hour') || feat.includes('Failures') || feat.includes('Lined') || feat.includes('Undersized') || feat.includes('Shallow') || feat.includes('Oversized') || feat.includes('Cleaned') || feat.includes('Was_Missing')) {
            return '1';
        }
        if (feat.includes('Score') || feat.includes('Ratio') || feat.includes('RMS') || feat.includes('STD') || feat.includes('Energy') || feat.includes('Deviation')) {
            return '0.01';
        }
        return '0.1';
    }

    // Helper: Display units
    function getUnitForFeature(feat) {
        if (feat.endsWith('_cm')) return 'cm';
        if (feat.endsWith('_m')) return 'm';
        if (feat.endsWith('_Years')) return 'yrs';
        if (feat.endsWith('_C')) return '°C';
        if (feat.includes('RMS')) return 'RMS';
        if (feat.includes('Score')) return 'score';
        if (feat.includes('Pressure')) return 'bar';
        if (feat.includes('Flow')) return 'L/s';
        return '';
    }

    // 4. Preset Loader
    function loadPreset(presetKey) {
        if (!schemaData || !schemaData.presets || !schemaData.presets[presetKey]) return;
        
        const presetData = schemaData.presets[presetKey].data;
        schemaData.features.forEach(feat => {
            const input = document.getElementById(`input_${feat}`);
            if (input && presetData[feat] !== undefined) {
                input.value = presetData[feat];
            }
        });

        // Trigger prediction automatically on preset load
        submitPrediction();
    }

    // 5. Submit Form & Call Prediction API
    async function submitPrediction() {
        if (!schemaData) return;

        // Build feature dictionary from form
        const featuresPayload = {};
        let isValid = true;

        schemaData.features.forEach(feat => {
            const input = document.getElementById(`input_${feat}`);
            if (!input) return;

            if (schemaData.categorical_features.includes(feat)) {
                featuresPayload[feat] = input.value;
            } else {
                const numVal = parseFloat(input.value);
                if (isNaN(numVal)) {
                    isValid = false;
                    input.style.borderColor = '#ef4444';
                } else {
                    input.style.borderColor = '';
                    featuresPayload[feat] = numVal;
                }
            }
        });

        if (!isValid) {
            alert('Please ensure all numeric feature fields contain valid numbers.');
            return;
        }

        // Set Loading State
        btnSubmit.disabled = true;
        btnSubmit.querySelector('.btn-text').style.display = 'none';
        btnSubmit.querySelector('.spinner').style.display = 'inline-block';

        try {
            const response = await fetch('/api/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ features: featuresPayload })
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Prediction request failed');
            }

            const result = await response.json();
            updateResultsUI(result);

        } catch (error) {
            console.error('Prediction API Error:', error);
            alert(`Prediction failed: ${error.message}`);
        } finally {
            btnSubmit.disabled = false;
            btnSubmit.querySelector('.btn-text').style.display = 'inline-block';
            btnSubmit.querySelector('.spinner').style.display = 'none';
        }
    }

    // 6. Render Prediction Results & Gauge Animation
    function updateResultsUI(res) {
        const probPct = (res.failure_probability * 100).toFixed(1);
        resultProbability.textContent = `${probPct}%`;

        // Update Gauge Needle & Arc
        // Arc spans from -90 deg (0%) to +90 deg (100%)
        const needleAngle = -90 + (res.failure_probability * 180);
        gaugeNeedle.style.transform = `rotate(${needleAngle}deg)`;

        // Calculate SVG stroke dasharray for arc fill
        // Arc radius = 80, length = PI * 80 ≈ 251.3
        const totalArc = 251.3;
        const fillLength = totalArc * res.failure_probability;
        gaugeFill.style.strokeDasharray = `${fillLength} ${totalArc}`;

        // Gauge color
        if (res.risk_level === 'High') {
            gaugeFill.style.stroke = '#ef4444';
            resultProbability.style.color = '#ef4444';
        } else if (res.risk_level === 'Medium') {
            gaugeFill.style.stroke = '#f59e0b';
            resultProbability.style.color = '#f59e0b';
        } else {
            gaugeFill.style.stroke = '#10b981';
            resultProbability.style.color = '#10b981';
        }

        // Update Result Banner
        resultBanner.className = `result-banner ${res.prediction ? 'failure' : 'normal'}`;
        statusTitle.textContent = res.status;
        statusIcon.className = res.prediction ? 'fa-solid fa-triangle-exclamation' : 'fa-solid fa-shield-check';

        // Risk badge
        riskBadge.textContent = `${res.risk_level} Risk`;
        riskBadge.className = `risk-badge badge-${res.risk_level.toLowerCase()}`;

        // Update Indicators
        const inds = res.key_indicators || {};
        indAge.textContent = `${inds.pipe_age || 0} yrs`;
        indPressureDev.textContent = `${inds.pressure_deviation || 0}`;
        indVibRms.textContent = `${inds.vibration_rms || 0}`;
        indRiskScore.textContent = `${inds.asset_risk_score || 0}`;
    }

    // 7. Event Listeners
    function setupEventListeners() {
        // Form submit
        predictionForm.addEventListener('submit', (e) => {
            e.preventDefault();
            submitPrediction();
        });

        // Preset buttons
        document.querySelectorAll('.preset-btn[data-preset]').forEach(btn => {
            btn.addEventListener('click', () => {
                loadPreset(btn.dataset.preset);
            });
        });

        // Reset form button
        document.getElementById('btn-reset-form').addEventListener('click', () => {
            loadPreset('normal');
        });

        // Architecture modal
        btnArchitectureModal.addEventListener('click', () => {
            architectureModal.style.display = 'flex';
        });
        btnCloseModal.addEventListener('click', () => {
            architectureModal.style.display = 'none';
        });
        architectureModal.addEventListener('click', (e) => {
            if (e.target === architectureModal) {
                architectureModal.style.display = 'none';
            }
        });
    }

    // Initialize Application
    initApp();
});
