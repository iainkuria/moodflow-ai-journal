// MoodFlow JavaScript Application
class MoodFlowApp {
    constructor() {
        this.entries = [];
        this.moodChart = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupThemeToggle();
        this.loadEntries();
        this.initChart();
        this.checkPaymentStatus();
    }

    setupEventListeners() {
        // Journal form submission
        document.getElementById('journalForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitJournalEntry();
        });
    }

    setupThemeToggle() {
        const themeToggle = document.getElementById('themeToggle');
        const themeIcon = document.getElementById('themeIcon');
        const currentTheme = localStorage.getItem('theme') || 'light';
        
        document.documentElement.setAttribute('data-theme', currentTheme);
        themeIcon.className = currentTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';

        themeToggle.addEventListener('click', () => {
            const theme = document.documentElement.getAttribute('data-theme');
            const newTheme = theme === 'dark' ? 'light' : 'dark';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            themeIcon.className = newTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        });
    }

    async submitJournalEntry() {
        const form = document.getElementById('journalForm');
        const textarea = document.getElementById('journalText');
        const submitBtn = form.querySelector('button[type="submit"]');
        const spinner = document.getElementById('loadingSpinner');
        
        const text = textarea.value.trim();
        if (!text) return;

        // Show loading state
        submitBtn.disabled = true;
        spinner.classList.remove('d-none');

        try {
            const response = await fetch('/api/entry', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text })
            });

            if (response.ok) {
                const entry = await response.json();
                
                // Clear form
                textarea.value = '';
                
                // Show success modal
                const modal = new bootstrap.Modal(document.getElementById('successModal'));
                modal.show();
                
                // Reload entries
                await this.loadEntries();
                this.updateChart();
                
                // Add animation to new entry
                setTimeout(() => {
                    const newEntry = document.querySelector('.journal-entry:first-child');
                    if (newEntry) {
                        newEntry.classList.add('fade-in-up');
                    }
                }, 100);
            } else {
                throw new Error('Failed to save entry');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showToast('Error saving entry. Please try again.', 'error');
        } finally {
            // Hide loading state
            submitBtn.disabled = false;
            spinner.classList.add('d-none');
        }
    }

    async loadEntries() {
        try {
            const response = await fetch('/api/entries');
            this.entries = await response.json();
            this.renderEntries();
        } catch (error) {
            console.error('Error loading entries:', error);
            this.showToast('Error loading entries', 'error');
        }
    }

    renderEntries() {
        const container = document.getElementById('entriesContainer');
        
        if (this.entries.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-book-open fa-3x"></i>
                    <h5>No entries yet</h5>
                    <p>Start writing your first journal entry above! ✍️</p>
                </div>
            `;
            return;
        }

        const entriesHTML = this.entries.map(entry => {
            const date = new Date(entry.date_created).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });

            const sentimentClass = this.getSentimentClass(entry.sentiment_label);
            const sentimentEmoji = this.getSentimentEmoji(entry.sentiment_label);
            const scorePercentage = Math.round(entry.sentiment_score * 100);

            return `
                <div class="journal-entry" data-entry-id="${entry.id}">
                    <div class="entry-header">
                        <div class="d-flex align-items-center">
                            <span class="sentiment-badge ${sentimentClass} me-2">
                                ${sentimentEmoji} ${entry.sentiment_label}
                            </span>
                            <small class="sentiment-score">
                                ${scorePercentage}% confidence
                            </small>
                        </div>
                        <small class="entry-date">
                            <i class="far fa-clock me-1"></i>${date}
                        </small>
                    </div>
                    <div class="entry-content">
                        <p class="entry-text mb-0">${this.escapeHtml(entry.content)}</p>
                        ${this.renderPremiumSection(entry)}
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = entriesHTML;
    }

    renderPremiumSection(entry) {
        if (entry.premium_analysis) {
            return `
                <div class="premium-analysis">
                    <h6><i class="fas fa-sparkles me-2"></i>AI Insight</h6>
                    <p class="mb-0">${this.escapeHtml(entry.premium_analysis)}</p>
                </div>
            `;
        } else if (entry.premium_unlocked) {
            return `
                <div class="entry-actions">
                    <button class="btn insight-btn btn-sm" onclick="app.generateInsight(${entry.id})">
                        <i class="fas fa-lightbulb me-1"></i>View AI Insight
                    </button>
                </div>
            `;
        } else {
            return `
                <div class="premium-section">
                    <h6><i class="fas fa-crown me-2"></i>Unlock AI-Powered Insight</h6>
                    <p class="mb-3">Get personalized, supportive guidance based on your journal entry</p>
                    <button class="btn payment-btn btn-sm" onclick="app.createPayment(${entry.id})">
                        <i class="fas fa-unlock me-1"></i>Unlock for KES 50
                    </button>
                </div>
            `;
        }
    }

    getSentimentClass(sentiment) {
        const sentimentLower = sentiment.toLowerCase();
        if (sentimentLower.includes('positive')) return 'sentiment-positive';
        if (sentimentLower.includes('negative')) return 'sentiment-negative';
        return 'sentiment-neutral';
    }

    getSentimentEmoji(sentiment) {
        const sentimentLower = sentiment.toLowerCase();
        if (sentimentLower.includes('positive')) return '😊';
        if (sentimentLower.includes('negative')) return '😔';
        return '😐';
    }

    async createPayment(entryId) {
        try {
            const response = await fetch('/api/create-payment-link', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ entry_id: entryId })
            });

            if (response.ok) {
                const data = await response.json();
                // Redirect to payment page
                window.location.href = data.payment_url;
            } else {
                throw new Error('Failed to create payment link');
            }
        } catch (error) {
            console.error('Payment error:', error);
            this.showToast('Payment service unavailable. Please try again.', 'error');
        }
    }

    async generateInsight(entryId) {
        try {
            const button = document.querySelector(`[onclick="app.generateInsight(${entryId})"]`);
            const originalText = button.innerHTML;
            button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Generating...';
            button.disabled = true;

            const response = await fetch('/api/generate-insight', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ entry_id: entryId })
            });

            if (response.ok) {
                const data = await response.json();
                await this.loadEntries(); // Reload to show the insight
                this.showToast('AI Insight generated successfully! 🎉', 'success');
            } else if (response.status === 402) {
                this.showToast('Premium not unlocked for this entry', 'warning');
            } else {
                throw new Error('Failed to generate insight');
            }
        } catch (error) {
            console.error('Insight error:', error);
            this.showToast('Failed to generate insight. Please try again.', 'error');
        }
    }

    initChart() {
        const ctx = document.getElementById('moodChart').getContext('2d');
        
        this.moodChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Mood Score',
                    data: [],
                    borderColor: 'rgb(102, 126, 234)',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: 'rgb(102, 126, 234)',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 3,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: 'white',
                        bodyColor: 'white',
                        cornerRadius: 8,
                        displayColors: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 1,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)',
                        },
                        ticks: {
                            callback: function(value) {
                                return (value * 100).toFixed(0) + '%';
                            }
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)',
                        }
                    }
                },
                elements: {
                    point: {
                        hoverBackgroundColor: 'rgb(102, 126, 234)',
                    }
                }
            }
        });
    }

    updateChart() {
        if (!this.moodChart || this.entries.length === 0) return;

        const chartData = this.entries
            .slice(-10) // Last 10 entries
            .reverse()
            .map(entry => ({
                date: new Date(entry.date_created).toLocaleDateString('en-US', {
                    month: 'short',
                    day: 'numeric'
                }),
                score: entry.sentiment_score
            }));

        this.moodChart.data.labels = chartData.map(d => d.date);
        this.moodChart.data.datasets[0].data = chartData.map(d => d.score);
        this.moodChart.update('active');
    }

    checkPaymentStatus() {
        // Check URL parameters for payment success
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('payment') === 'success') {
            this.showToast('Payment successful! Premium features unlocked! 🎉', 'success');
            // Reload entries to reflect unlocked status
            setTimeout(() => {
                this.loadEntries();
            }, 1000);
            
            // Clean up URL
            window.history.replaceState({}, document.title, window.location.pathname);
        }
    }

    showToast(message, type = 'info') {
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
        toast.style.cssText = 'top: 100px; right: 20px; z-index: 1050; min-width: 300px;';
        
        const icon = type === 'success' ? 'check-circle' : 
                    type === 'error' ? 'exclamation-circle' : 
                    type === 'warning' ? 'exclamation-triangle' : 'info-circle';
        
        toast.innerHTML = `
            <i class="fas fa-${icon} me-2"></i>${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(toast);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 5000);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Utility functions
function scrollToJournal() {
    document.getElementById('journalSection').scrollIntoView({
        behavior: 'smooth'
    });
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.app = new MoodFlowApp();
});

// Add some interactive effects
document.addEventListener('DOMContentLoaded', function() {
    // Add floating animation to cards on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
            }
        });
    }, observerOptions);

    // Observe all cards
    document.querySelectorAll('.card').forEach(card => {
        observer.observe(card);
    });

    // Add smooth hover effects to buttons
    document.addEventListener('mouseover', function(e) {
        if (e.target.classList.contains('btn')) {
            e.target.style.transform = 'translateY(-2px)';
        }
    });

    document.addEventListener('mouseout', function(e) {
        if (e.target.classList.contains('btn')) {
            e.target.style.transform = 'translateY(0)';
        }
    });
});