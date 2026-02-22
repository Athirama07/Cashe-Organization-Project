// Global state
let currentConfig = {
    cacheSize: 16384,
    blockSize: 32,
    associativity: 2,
    writePolicy: 'WRITE_BACK',
    replacementPolicy: 'LRU',
    benchmark: 'matrix_multiplication',
    enableAdaptive: false,
    matrixSize: 32
};

let simulationResults = null;
let charts = {};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function () {
    initializeEventListeners();
    initializeCharts();
    loadSampleData();
    initializeCacheVisualizer();
});

// Event Listeners
function initializeEventListeners() {
    // Cache size slider
    const cacheSizeSlider = document.getElementById('cacheSize');
    const cacheSizeValue = document.getElementById('cacheSizeValue');

    cacheSizeSlider.addEventListener('input', function (e) {
        const kb = e.target.value / 1024;
        cacheSizeValue.textContent = kb + ' KB';
        currentConfig.cacheSize = parseInt(e.target.value);
    });

    // Block size change
    document.getElementById('blockSize').addEventListener('change', function (e) {
        currentConfig.blockSize = parseInt(e.target.value);
    });

    // Associativity change
    document.getElementById('associativity').addEventListener('change', function (e) {
        currentConfig.associativity = parseInt(e.target.value);
    });

    // Write policy change
    document.getElementById('writePolicy').addEventListener('change', function (e) {
        currentConfig.writePolicy = e.target.value;
    });

    // Replacement policy change
    document.getElementById('replacementPolicy').addEventListener('change', function (e) {
        currentConfig.replacementPolicy = e.target.value;
    });

    // Benchmark change
    document.getElementById('benchmark').addEventListener('change', function (e) {
        currentConfig.benchmark = e.target.value;
        const matrixSizeDiv = document.getElementById('matrixSizeDiv');
        matrixSizeDiv.style.display =
            e.target.value === 'matrix_multiplication' ? 'block' : 'none';
    });

    // Adaptive checkbox
    document.getElementById('enableAdaptive').addEventListener('change', function (e) {
        currentConfig.enableAdaptive = e.target.checked;
    });

    // Matrix size change
    document.getElementById('matrixSize').addEventListener('input', function (e) {
        currentConfig.matrixSize = parseInt(e.target.value);
    });

    // Run simulation button
    document.getElementById('runSimulationBtn').addEventListener('click', runSimulation);

    // Save config button
    document.getElementById('saveConfigBtn').addEventListener('click', saveConfiguration);

    // Reset config button
    document.getElementById('resetConfigBtn').addEventListener('click', resetConfiguration);

    // Address lookup
    document.getElementById('lookupAddress').addEventListener('click', lookupAddress);

    // Enter key for address input
    document.getElementById('addressInput').addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            lookupAddress();
        }
    });

    // Navigation links
    document.getElementById('docsLink').addEventListener('click', showDocumentation);
    document.getElementById('aboutLink').addEventListener('click', showAbout);
}

// Initialize Charts
function initializeCharts() {
    // Performance Timeline Chart
    const perfCtx = document.getElementById('performanceChart').getContext('2d');
    charts.performance = new Chart(perfCtx, {
        type: 'line',
        data: {
            labels: ['0', '500', '1000', '1500', '2000', '2500', '3000'],
            datasets: [{
                label: 'Hit Rate (%)',
                data: [92, 93, 94, 94, 95, 94, 94],
                borderColor: '#198754',
                backgroundColor: 'rgba(25, 135, 84, 0.1)',
                tension: 0.4,
                fill: true
            }, {
                label: 'Miss Rate (%)',
                data: [8, 7, 6, 6, 5, 6, 6],
                borderColor: '#dc3545',
                backgroundColor: 'rgba(220, 53, 69, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Number of Misses'
                    }
                }
            }
        }
    });

    // Adaptive Chart
    const adaptiveCtx = document.getElementById('adaptiveChart').getContext('2d');
    charts.adaptive = new Chart(adaptiveCtx, {
        type: 'line',
        data: {
            labels: ['500', '1000', '1500', '2000', '2500', '3000', '3500', '4000'],
            datasets: [{
                label: 'Miss Rate with Adaptive Policy',
                data: [8, 7, 6, 5, 5, 4, 4, 3.5],
                borderColor: '#ffc107',
                backgroundColor: 'rgba(255, 193, 7, 0.1)',
                tension: 0.4,
                fill: true
            }, {
                label: 'Standard LRU',
                data: [8, 7, 6, 6, 6, 6, 5.8, 5.8],
                borderColor: '#6c757d',
                borderDash: [5, 5],
                tension: 0.4,
                fill: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });


    // Hit/Miss Distribution Doughnut Chart
    const hitMissCtx = document.getElementById('hitMissChart').getContext('2d');
    charts.hitMiss = new Chart(hitMissCtx, {
        type: 'doughnut',
        data: {
            labels: ['Hits', 'Misses'],
            datasets: [{
                data: [94.2, 5.8],
                backgroundColor: [chartConfigs.colors.success, chartConfigs.colors.danger],
                borderColor: 'white',
                borderWidth: 3,
                hoverBackgroundColor: [
                    adjustColor(chartConfigs.colors.success, -20),
                    adjustColor(chartConfigs.colors.danger, -20)
                ]
            }]
        },
        options: {
            ...chartConfigs.commonOptions,
            cutout: '75%',
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        usePointStyle: true,
                        padding: 20,
                        font: {
                            size: 13
                        }
                    }
                },
                title: {
                    display: true,
                    text: 'Cache Hit/Miss Distribution',
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    padding: {
                        bottom: 20
                    }
                }
            }
        }
    });

    // Helper function to adjust color brightness
    function adjustColor(color, percent) {
        // This is a simple implementation - you might want to use a proper color library
        if (color.startsWith('#')) {
            // Handle hex colors or use your existing color manipulation logic
            return color;
        }
        return color;
    }
    // Miss Classification Bar Chart
    const missCtx = document.getElementById('missChart').getContext('2d');
    charts.miss = new Chart(missCtx, {
        type: 'bar',
        data: {
            labels: ['Compulsory', 'Capacity', 'Conflict'],
            datasets: [{
                label: 'Misses',
                data: [100, 200, 150],
                backgroundColor: [
                    chartConfigs.colors.primary,
                    chartConfigs.colors.warning,
                    chartConfigs.colors.danger
                ]
            }]
        },
        options: chartConfigs.commonOptions
    });
}

// Initialize Cache Visualizer
function initializeCacheVisualizer() {
    const cacheGrid = document.getElementById('cacheGrid');
    let html = '';

    for (let set = 0; set < 8; set++) {
        html += `<div class="cache-row" data-set="${set}" onclick="selectSet(${set})">`;
        html += `<div class="cache-set-label">Set ${set}</div>`;

        for (let way = 0; way < 4; way++) {
            const valid = Math.random() > 0.3;
            const tag = `0x${Math.floor(Math.random() * 1000).toString(16)}`;
            const age = Math.floor(Math.random() * 100);

            html += `<div class="cache-line ${valid ? 'valid' : 'invalid'}" 
                          data-set="${set}" data-way="${way}" data-tag="${tag}">`;
            if (valid) {
                html += `<div class="tag">${tag}</div>`;
                html += `<div class="age">age: ${age}</div>`;
            } else {
                html += `<span>Empty</span>`;
            }
            html += `</div>`;
        }
        html += `</div>`;
    }

    cacheGrid.innerHTML = html;
}

// Select Set in Cache Visualizer
function selectSet(set) {
    // Remove selected class from all rows
    document.querySelectorAll('.cache-row').forEach(row => {
        row.classList.remove('selected');
    });

    // Add selected class to clicked row
    document.querySelector(`.cache-row[data-set="${set}"]`).classList.add('selected');

    // Update badge
    document.getElementById('selectedSetBadge').textContent = `Set ${set} Selected`;

    // Update set details
    updateSetDetails(set);
}

// Update Set Details
function updateSetDetails(set) {
    const setDetails = document.getElementById('setDetails');
    const setRow = document.querySelector(`.cache-row[data-set="${set}"]`);
    const lines = setRow.querySelectorAll('.cache-line');

    let html = '<table class="table table-sm">';
    html += '<tr><th>Way</th><th>Valid</th><th>Tag</th><th>Age</th></tr>';

    lines.forEach((line, index) => {
        const valid = line.classList.contains('valid');
        const tag = line.querySelector('.tag')?.textContent || '-';
        const age = line.querySelector('.age')?.textContent?.replace('age: ', '') || '-';

        html += `<tr>
            <td>${index}</td>
            <td>${valid ? '<span class="badge bg-success">Yes</span>' : '<span class="badge bg-secondary">No</span>'}</td>
            <td><code>${tag}</code></td>
            <td>${age}</td>
        </tr>`;
    });

    html += '</table>';
    setDetails.innerHTML = html;
}
// Lookup Address
function lookupAddress() {
    const address = document.getElementById('addressInput').value;
    const resultDiv = document.getElementById('lookupResult');
    const resultText = document.getElementById('lookupText');

    if (!address) {
        resultDiv.style.display = 'none';
        return;
    }

    // Simulate address lookup
    const set = Math.floor(parseInt(address, 16) / 32) % 8;
    const tag = `0x${Math.floor(parseInt(address, 16) / (32 * 8)).toString(16)}`;

    // Highlight the line if found
    const lines = document.querySelectorAll('.cache-line');
    lines.forEach(line => line.classList.remove('highlighted'));

    let found = false;
    lines.forEach(line => {
        if (line.querySelector('.tag')?.textContent === tag) {
            line.classList.add('highlighted');
            found = true;
        }
    });

    if (found) {
        resultText.textContent = `Address maps to Set ${set} with tag ${tag} - Found in cache!`;
        resultDiv.className = 'alert alert-success';
    } else {
        resultText.textContent = `Address maps to Set ${set} with tag ${tag} - Not found in cache (miss)`;
        resultDiv.className = 'alert alert-warning';
    }

    resultDiv.style.display = 'block';
}

// Run Simulation (Main entry point)

// Update Results UI
function updateResults(results) {
    document.getElementById('hitRateValue').textContent = results.hitRate;
    document.getElementById('missRateValue').textContent = results.missRate;
    document.getElementById('amatValue').textContent = results.amat;
    document.getElementById('trafficValue').textContent = results.memoryTraffic;

    document.getElementById('hitRateChange').textContent = results.hitRateChange;
    document.getElementById('missRateChange').textContent = results.missRateChange;
    document.getElementById('amatChange').textContent = results.amatChange;
    document.getElementById('trafficChange').textContent = results.trafficChange;

    // Update charts with new data
    updateCharts(results);
}

// Update Charts
function updateCharts(results) {
    // Update performance chart
    if (charts.performance) {
        charts.performance.data.datasets[0].data = results.timelineData.map(d => d.hitRate);
        charts.performance.data.datasets[1].data = results.timelineData.map(d => d.missRate);
        charts.performance.update();
    }

    // Update pie chart
    if (charts.hitMiss) {
        const hit = parseFloat(results.hitRate);
        const miss = parseFloat(results.missRate);
        charts.hitMiss.data.datasets[0].data = [hit, miss];
        charts.hitMiss.update();

        // Update labels below chart
        document.getElementById('hitCountLabel').textContent = `Hits: ${results.hitRate}`;
        document.getElementById('missCountLabel').textContent = `Misses: ${results.missRate}`;
    }

    // Update miss chart
    if (charts.miss && results.missClassification) {
        charts.miss.data.datasets[0].data = [
            results.missClassification.compulsory,
            results.missClassification.capacity,
            results.missClassification.conflict
        ];
        charts.miss.update();
    }
}

// Save Configuration
function saveConfiguration() {
    localStorage.setItem('cacheConfig', JSON.stringify(currentConfig));
    showToast('Configuration saved successfully!', 'success');
}

// Reset Configuration
function resetConfiguration() {
    currentConfig = {
        cacheSize: 16384,
        blockSize: 32,
        associativity: 2,
        writePolicy: 'WRITE_BACK',
        replacementPolicy: 'LRU',
        benchmark: 'matrix_multiplication',
        enableAdaptive: false,
        matrixSize: 32
    };

    // Update UI
    document.getElementById('cacheSize').value = currentConfig.cacheSize;
    document.getElementById('cacheSizeValue').textContent = '16 KB';
    document.getElementById('blockSize').value = currentConfig.blockSize;
    document.getElementById('associativity').value = currentConfig.associativity;
    document.getElementById('writePolicy').value = currentConfig.writePolicy;
    document.getElementById('replacementPolicy').value = currentConfig.replacementPolicy;
    document.getElementById('benchmark').value = currentConfig.benchmark;
    document.getElementById('enableAdaptive').checked = currentConfig.enableAdaptive;
    document.getElementById('matrixSize').value = currentConfig.matrixSize;

    showToast('Configuration reset to defaults', 'info');
}

// Show Toast Message
function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }

    // Create toast
    const toastId = 'toast-' + Date.now();
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.id = toastId;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');

    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="fas ${type === 'success' ? 'fa-check-circle' :
            type === 'error' ? 'fa-exclamation-circle' :
                'fa-info-circle'} me-2"></i>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;

    toastContainer.appendChild(toast);

    // Initialize and show toast
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();

    // Remove toast after it's hidden
    toast.addEventListener('hidden.bs.toast', function () {
        toast.remove();
    });
}

// Show Documentation
function showDocumentation(e) {
    e.preventDefault();
    showToast('Documentation feature coming soon!', 'info');
}

// Show About
function showAbout(e) {
    e.preventDefault();
    alert(`
CacheSim Pro - Version 1.0
Advanced Cache Organization Analyzer

Created for Computer Architecture and Organization Project


Features:
• Multiple cache configurations
• Real-time visualization
• Adaptive cache policy
• Performance analysis
• Miss classification
• AMAT calculation
    `);
}

// Load Sample Data
function loadSampleData() {
    // This will populate with initial sample data
    const sampleResults = {
        hitRate: '94.2%',
        missRate: '5.8%',
        amat: '2.4 cycles',
        memoryTraffic: '1,234 blocks',
        hitRateChange: '+2.3%',
        missRateChange: '-1.2%',
        amatChange: '-0.3',
        trafficChange: '+124',
        timelineData: generateTimelineData(),
        missClassification: generateMissData()
    };

    updateResults(sampleResults);
}
// Update the runSimulation function in script.js
async function runSimulation() {
    // Show loading spinner
    document.getElementById('loadingSpinner').style.display = 'block';
    document.getElementById('resultsDashboard').style.opacity = '0.5';

    // Disable run button
    const runBtn = document.getElementById('runSimulationBtn');
    runBtn.disabled = true;
    runBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Running...';

    try {
        // Get current configuration
        const config = {
            cacheSize: parseInt(document.getElementById('cacheSize').value),
            blockSize: parseInt(document.getElementById('blockSize').value),
            associativity: parseInt(document.getElementById('associativity').value),
            writePolicy: document.getElementById('writePolicy').value,
            replacementPolicy: document.getElementById('replacementPolicy').value,
            benchmark: document.getElementById('benchmark').value,
            enableAdaptive: document.getElementById('enableAdaptive').checked,
            matrixSize: parseInt(document.getElementById('matrixSize').value || 32)
        };

        console.log('Sending config:', config); // Debug log

        // Make API call to backend (relative path so frontend and backend can run together)
        const response = await fetch('/api/simulate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(config)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const results = await response.json();
        console.log('Received results:', results); // Debug log

        // Update UI with results
        updateResults(results);

        // Show success message
        showToast('Simulation completed successfully!', 'success');

    } catch (error) {
        console.error('Simulation error:', error);
        showToast('Simulation failed: ' + error.message, 'error');

        // Fallback to sample data if backend not available
        console.log('Using fallback sample data');
        const sampleResults = {
            hitRate: '94.2%',
            missRate: '5.8%',
            amat: '2.4 cycles',
            memoryTraffic: '1,234 blocks',
            hitRateChange: '+2.3%',
            missRateChange: '-1.2%',
            amatChange: '-0.3',
            trafficChange: '+124',
            timelineData: generateTimelineData(),
            missClassification: generateMissData()
        };
        updateResults(sampleResults);
        showToast('Using sample data (backend not connected)', 'warning');

    } finally {
        // Hide loading spinner
        document.getElementById('loadingSpinner').style.display = 'none';
        document.getElementById('resultsDashboard').style.opacity = '1';

        // Re-enable run button
        runBtn.disabled = false;
        runBtn.innerHTML = '<i class="fas fa-play me-2"></i>Run Simulation';
    }
}

// Helper functions for fallback data
function generateTimelineData() {
    const data = [];
    for (let i = 0; i < 20; i++) {
        data.push({
            time: i * 100,
            hitRate: 90 + Math.random() * 8,
            missRate: 10 - Math.random() * 8
        });
    }
    return data;
}

function generateMissData() {
    return {
        compulsory: Math.floor(100 + Math.random() * 50),
        capacity: Math.floor(200 + Math.random() * 100),
        conflict: Math.floor(150 + Math.random() * 100)
    };
}