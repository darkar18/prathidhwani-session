document.addEventListener('DOMContentLoaded', () => {
    // --- Charts Logic ---
    let experienceChart, confidenceChart, domainChart;

    async function fetchAnalytics() {
        try {
            const response = await fetch('/api/analyze', { method: 'POST' });
            const data = await response.json();
            updateCharts(data.analytics);
        } catch (error) {
            console.error("Failed to fetch analytics:", error);
        }
    }

    function updateCharts(data) {
        if (!data || data.error) return;

        updatePieChart('experienceChart', data.experience_breakdown, 'Experience Levels');
        updatePieChart('confidenceChart', data.confidence_breakdown, 'Confidence Levels');
        updatePieChart('domainChart', data.top_domains, 'Top Domains');
    }

    function updatePieChart(canvasId, dataMap, label) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        const labels = Object.keys(dataMap);
        const values = Object.values(dataMap);

        // Destroy existing chart if it exists to avoid overlay
        const chartInstance = Chart.getChart(canvasId);
        if (chartInstance) {
            chartInstance.destroy();
        }

        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    label: label,
                    data: values,
                    backgroundColor: [
                        'rgba(59, 130, 246, 0.8)',
                        'rgba(139, 92, 246, 0.8)',
                        'rgba(16, 185, 129, 0.8)',
                        'rgba(245, 158, 11, 0.8)',
                        'rgba(239, 68, 68, 0.8)'
                    ],
                    borderColor: 'rgba(15, 23, 42, 1)',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: { color: '#94a3b8' }
                    }
                }
            }
        });
    }

    // Expose refresh function globally
    window.refreshData = fetchAnalytics;

    // Initial Load
    fetchAnalytics();

    // --- Chat Logic ---
    const chatWindow = document.getElementById('chat-window');
    const adminInput = document.getElementById('admin-input');
    const sendBtn = document.getElementById('admin-send-btn');

    function addMessage(text, sender) {
        const div = document.createElement('div');
        div.classList.add('message', sender === 'user' ? 'user-message' : 'bot-message');
        if (sender === 'bot') {
            div.innerHTML = marked.parse(text);
        } else {
            div.textContent = text;
        }
        chatWindow.appendChild(div);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    async function sendAdminMessage() {
        const text = adminInput.value.trim();
        if (!text) return;

        addMessage(text, 'user');
        adminInput.value = '';

        try {
            const response = await fetch('/api/admin/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: text })
            });

            const data = await response.json();
            addMessage(data.answer, 'bot');
        } catch (error) {
            console.error('Error:', error);
            addMessage("Error querying analytics agent.", 'bot');
        }
    }

    sendBtn.addEventListener('click', sendAdminMessage);
    adminInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendAdminMessage();
    });
});
