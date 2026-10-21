// C.A.R.E. - Customer Analytics & Retention Engine
// Frontend JavaScript Application

class CareApp {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000';
        this.currentData = null;
        this.currentAnalysis = null;
        this.connectionInterval = null;
        
        this.initializeElements();
        this.bindEvents();
        this.checkApiStatus();
        this.startAutoConnection();
    }
    
    // Initialize DOM elements
    initializeElements() {
        // Upload elements
        this.uploadArea = document.getElementById('upload-area');
        this.fileInput = document.getElementById('file-input');
        this.fileInfo = document.getElementById('file-info');
        this.fileName = document.getElementById('file-name');
        this.fileSize = document.getElementById('file-size');
        this.removeFileBtn = document.getElementById('remove-file');
        this.analyzeBtn = document.getElementById('analyze-btn');
        this.uploadLink = document.querySelector('.upload-link');
        
        // Section elements
        this.uploadSection = document.getElementById('upload-section');
        this.loadingSection = document.getElementById('loading-section');
        this.resultsSection = document.getElementById('results-section');
        this.errorSection = document.getElementById('error-section');
        
        // Loading elements
        this.progressFill = document.getElementById('progress-fill');
        this.progressText = document.getElementById('progress-text');
        
        // Results elements
        this.totalCustomers = document.getElementById('total-customers');
        this.churnRate = document.getElementById('churn-rate');
        this.highRisk = document.getElementById('high-risk');

        this.executiveSummary = document.getElementById('executive-summary-text');
        this.prioritiesGrid = document.getElementById('priorities-grid');
        this.actionTimeline = document.getElementById('action-timeline');
        this.predictionsTable = document.getElementById('predictions-tbody');
        this.metricsGrid = document.getElementById('metrics-grid');
        this.riskGrid = document.getElementById('risk-grid');
        
        // Controls
        this.riskFilter = document.getElementById('risk-filter');
        this.exportBtn = document.getElementById('export-csv');
        this.retryBtn = document.getElementById('retry-btn');
        
        // Status
        this.apiStatus = document.getElementById('api-status');
    }
    
    // Bind event listeners
    bindEvents() {
        // File upload events
        this.uploadArea.addEventListener('click', (e) => {
            // Don't trigger if clicking on the upload link or label
            if (e.target.classList.contains('upload-link') || e.target.tagName === 'LABEL') {
                return;
            }
            this.fileInput.click();
        });
        this.uploadArea.addEventListener('dragover', this.handleDragOver.bind(this));
        this.uploadArea.addEventListener('dragleave', this.handleDragLeave.bind(this));
        this.uploadArea.addEventListener('drop', this.handleFileDrop.bind(this));
        this.fileInput.addEventListener('change', this.handleFileSelect.bind(this));
        this.removeFileBtn.addEventListener('click', this.removeFile.bind(this));
        this.analyzeBtn.addEventListener('click', this.analyzeData.bind(this));
        
        // Add direct click handler for upload link if it exists
        if (this.uploadLink) {
            this.uploadLink.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.fileInput.click();
            });
        }
        
        // Results events
        this.riskFilter.addEventListener('change', this.filterPredictions.bind(this));
        this.exportBtn.addEventListener('click', this.exportPredictions.bind(this));
        this.retryBtn.addEventListener('click', this.resetToUpload.bind(this));
    }
    
    // Check API status
    async checkApiStatus() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/health`);
            const status = this.apiStatus.querySelector('.status-dot');
            const text = this.apiStatus;
            
            if (response.ok) {
                status.classList.add('connected');
                status.classList.remove('error');
                text.innerHTML = '<span class="status-dot connected"></span>Connected';
                
                // If we successfully connect, we can reduce the check frequency
                if (this.connectionInterval) {
                    clearInterval(this.connectionInterval);
                    this.connectionInterval = setInterval(() => this.checkApiStatus(), 10000); // Check every 10 seconds when connected
                }
            } else {
                status.classList.add('error');
                status.classList.remove('connected');
                text.innerHTML = '<span class="status-dot error"></span>Error';
            }
        } catch (error) {
            const status = this.apiStatus.querySelector('.status-dot');
            const text = this.apiStatus;
            status.classList.add('error');
            status.classList.remove('connected');
            text.innerHTML = '<span class="status-dot error"></span>Connecting...';
        }
    }
    
    // Start automatic connection checking
    startAutoConnection() {
        // Check every 3 seconds when not connected, 10 seconds when connected
        this.connectionInterval = setInterval(() => this.checkApiStatus(), 3000);
    }
    
    // File handling methods
    handleDragOver(e) {
        e.preventDefault();
        this.uploadArea.classList.add('dragover');
    }
    
    handleDragLeave(e) {
        e.preventDefault();
        this.uploadArea.classList.remove('dragover');
    }
    
    handleFileDrop(e) {
        e.preventDefault();
        this.uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.handleFile(files[0]);
        }
    }
    
    handleFileSelect(e) {
        const files = e.target.files;
        if (files.length > 0) {
            this.handleFile(files[0]);
        }
    }
    
    handleFile(file) {
        // Validate file type
        if (!file.name.toLowerCase().endsWith('.csv')) {
            this.showError('Please upload a CSV file.');
            return;
        }
        
        // Store file
        this.currentData = file;
        
        // Update UI
        this.fileName.textContent = file.name;
        this.fileSize.textContent = this.formatFileSize(file.size);
        this.uploadArea.style.display = 'none';
        this.fileInfo.style.display = 'flex';
        this.analyzeBtn.disabled = false;
    }
    
    removeFile() {
        this.currentData = null;
        this.fileInput.value = '';
        this.uploadArea.style.display = 'block';
        this.fileInfo.style.display = 'none';
        this.analyzeBtn.disabled = true;
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // Data analysis methods
    async analyzeData() {
        if (!this.currentData) return;
        
        // Show loading
        this.showLoading();
        
        // Create form data
        const formData = new FormData();
        formData.append('file', this.currentData);
        
        try {
            // Update progress
            this.updateProgress(20, 'Uploading file...');
            
            // Upload and analyze
            const response = await fetch(`${this.apiBaseUrl}/upload`, {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            this.updateProgress(60, 'Processing results...');
            
            const result = await response.json();
            
            this.updateProgress(90, 'Generating business plan...');
            
            // Store results
            this.currentAnalysis = result;
            
            // Show results
            setTimeout(() => {
                this.showResults(result);
            }, 500);
            
        } catch (error) {
            console.error('Analysis error:', error);
            this.showError('Failed to analyze data. Please check your file and try again.');
        }
    }
    
    showLoading() {
        this.uploadSection.style.display = 'none';
        this.errorSection.style.display = 'none';
        this.resultsSection.style.display = 'none';
        this.loadingSection.style.display = 'flex';
        
        // Reset progress
        this.updateProgress(0, 'Initializing...');
    }
    
    updateProgress(percentage, text) {
        this.progressFill.style.width = `${percentage}%`;
        this.progressText.textContent = text;
    }
    
    showResults(analysis) {
        this.loadingSection.style.display = 'none';
        this.resultsSection.style.display = 'block';
        this.resultsSection.classList.add('fade-in');
        
        // Populate summary
        this.populateSummary(analysis.summary);
        
        // Populate business plan
        this.populateBusinessPlan(analysis.business_plan);
        
        // Populate predictions
        this.populatePredictions(analysis.predictions);
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
    
    populateSummary(summary) {
        this.totalCustomers.textContent = summary.total_customers.toLocaleString();
        this.churnRate.textContent = `${summary.churn_rate}%`;
        this.highRisk.textContent = summary.high_risk_customers.toLocaleString();
        

    }
    
    populateBusinessPlan(businessPlan) {
        // Executive summary
        this.executiveSummary.textContent = businessPlan.executive_summary;
        

        
        // Strategic priorities
        this.prioritiesGrid.innerHTML = '';
        businessPlan.strategic_priorities.forEach(priority => {
            const priorityElement = this.createPriorityElement(priority);
            this.prioritiesGrid.appendChild(priorityElement);
        });
        
        // Action plan
        this.actionTimeline.innerHTML = '';
        const phases = {
            'Foundation': businessPlan.action_plan.filter(item => item.phase === 'Foundation'),
            'Implementation': businessPlan.action_plan.filter(item => item.phase === 'Implementation'),
            'Optimization': businessPlan.action_plan.filter(item => item.phase === 'Optimization')
        };
        
        Object.entries(phases).forEach(([phaseName, actions]) => {
            if (actions.length > 0) {
                const phaseElement = this.createPhaseElement(phaseName, actions);
                this.actionTimeline.appendChild(phaseElement);
            }
        });
        
        // Success metrics
        this.metricsGrid.innerHTML = '';
        businessPlan.success_metrics.forEach(metric => {
            const metricElement = this.createMetricElement(metric);
            this.metricsGrid.appendChild(metricElement);
        });
        
        // Risk mitigation
        this.riskGrid.innerHTML = '';
        businessPlan.risk_mitigation.forEach(risk => {
            const riskElement = this.createRiskElement(risk);
            this.riskGrid.appendChild(riskElement);
        });
    }
    
    createPriorityElement(priority) {
        const div = document.createElement('div');
        div.className = `priority-item ${priority.priority_level.toLowerCase()}`;
        
        div.innerHTML = `
            <div class="priority-header">
                <span class="priority-badge ${priority.priority_level.toLowerCase()}">${priority.priority_level}</span>
                <div class="priority-title">${priority.focus_area}</div>
            </div>
            <div class="priority-details">
                <strong>Target:</strong> ${priority.target_driver}<br>
                <strong>Impact:</strong> ${priority.target_impact}
            </div>
        `;
        
        return div;
    }
    
    createPhaseElement(phaseName, actions) {
        const div = document.createElement('div');
        div.className = 'action-phase';
        
        let phaseHtml = `<div class="phase-title">📅 ${phaseName} Phase</div>`;
        
        actions.forEach(action => {
            phaseHtml += `
                <div class="action-item">
                    <div class="action-header">
                        <div>
                            <div class="action-title">${action.initiative_name}</div>
                            <div class="action-timeline">⏱️ ${action.timeline}</div>
                        </div>
                    </div>
                    <div class="action-details">
                        <ul class="action-list">
                            ${action.specific_actions.map(actionItem => `<li>${actionItem}</li>`).join('')}
                        </ul>
                    </div>
                    <div class="action-impact">
                        <strong>Expected Impact:</strong> ${action.expected_impact}
                    </div>
                </div>
            `;
        });
        
        div.innerHTML = phaseHtml;
        return div;
    }
    
    createMetricElement(metric) {
        const div = document.createElement('div');
        div.className = 'metric-item';
        
        div.innerHTML = `
            <div class="metric-name">${metric.metric_name}</div>
            <div class="metric-current">Current: ${metric.current_value}</div>
            <div class="metric-target">Target: ${metric.target_value}</div>
            <div class="metric-method">Method: ${metric.measurement_method} (${metric.review_frequency})</div>
        `;
        
        return div;
    }
    
    createRiskElement(risk) {
        const div = document.createElement('div');
        div.className = 'risk-item';
        
        div.innerHTML = `
            <div class="risk-name">⚠️ ${risk.risk}</div>
            <div class="risk-details">
                <span class="risk-probability ${risk.probability.toLowerCase()}">${risk.probability} Probability</span>
                <span class="risk-impact ${risk.impact.toLowerCase()}">${risk.impact} Impact</span>
            </div>
            <div class="risk-mitigation">
                <strong>Mitigation:</strong> ${risk.mitigation_strategy}
            </div>
        `;
        
        return div;
    }
    
    populatePredictions(predictions) {
        this.predictionsTable.innerHTML = '';
        
        predictions.forEach((prediction, index) => {
            const row = this.createPredictionRow(prediction, index);
            this.predictionsTable.appendChild(row);
        });
    }
    
    createPredictionRow(prediction, index) {
        const tr = document.createElement('tr');
        tr.dataset.risk = prediction.risk_level.toLowerCase();
        
        const riskClass = prediction.risk_level.toLowerCase();
        const probClass = parseFloat(prediction.churn_probability) >= 0.7 ? 'high' : 
                         parseFloat(prediction.churn_probability) >= 0.4 ? 'medium' : 'low';
        
        tr.innerHTML = `
            <td>${prediction.customer_id}</td>
            <td><span class="churn-prob ${probClass}">${(prediction.churn_probability * 100).toFixed(1)}%</span></td>
            <td>${prediction.churn_prediction}</td>
            <td><span class="risk-badge ${riskClass}">${prediction.risk_level}</span></td>
        `;
        
        return tr;
    }
    
    filterPredictions() {
        const filter = this.riskFilter.value;
        const rows = this.predictionsTable.querySelectorAll('tr');
        
        rows.forEach(row => {
            if (filter === 'all') {
                row.style.display = '';
            } else {
                row.style.display = row.dataset.risk === filter ? '' : 'none';
            }
        });
    }
    
    exportPredictions() {
        if (!this.currentAnalysis || !this.currentAnalysis.predictions) return;
        
        // Create CSV content
        const headers = ['Customer ID', 'Churn Probability', 'Churn Prediction', 'Risk Level'];
        const rows = this.currentAnalysis.predictions.map(p => [
            p.customer_id,
            (p.churn_probability * 100).toFixed(1) + '%',
            p.churn_prediction,
            p.risk_level
        ]);
        
        const csvContent = [headers, ...rows]
            .map(row => row.map(cell => `"${cell}"`).join(','))
            .join('\\n');
        
        // Create download link
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `churn_predictions_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }
    
    showError(message) {
        this.uploadSection.style.display = 'none';
        this.loadingSection.style.display = 'none';
        this.resultsSection.style.display = 'none';
        this.errorSection.style.display = 'flex';
        this.errorSection.classList.add('fade-in');
        
        // Update error message
        const errorMessage = document.getElementById('error-message');
        if (errorMessage) {
            errorMessage.textContent = message;
        }
    }
    
    resetToUpload() {
        this.errorSection.style.display = 'none';
        this.resultsSection.style.display = 'none';
        this.loadingSection.style.display = 'none';
        this.uploadSection.style.display = 'block';
        this.uploadSection.classList.add('fade-in');
        
        // Clear file
        this.removeFile();
        
        // Reset data
        this.currentData = null;
        this.currentAnalysis = null;
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new CareApp();
});

// Utility functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function formatNumber(num) {
    return new Intl.NumberFormat('en-US').format(num);
}

function formatPercentage(value) {
    return `${(value * 100).toFixed(1)}%`;
}