        // Utility to toggle modal visibility
        function toggleModal(modalId, displayState) {
            document.getElementById(modalId).style.display = displayState;
        }
    
        // Function to update real-time date and time
        function updateDateTime() {
            const now = new Date();
            const hours = now.getHours().toString().padStart(2, '0');
            const minutes = now.getMinutes().toString().padStart(2, '0');
            const seconds = now.getSeconds().toString().padStart(2, '0');
            const day = now.getDate().toString().padStart(2, '0');
            const month = (now.getMonth() + 1).toString().padStart(2, '0'); // Months are 0-based
            const year = now.getFullYear();
    
            const timeString = `${hours}:${minutes}:${seconds}`;
            const dateString = `${day}/${month}/${year}`;
            document.getElementById("date-time").textContent = `${dateString} | ${timeString}`;
        }
    
        // Initialize date and time
        updateDateTime();
        setInterval(updateDateTime, 1000);
    
        // Toggle sidebar visibility
        function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            sidebar.classList.toggle('active');
        }
            // Fetch sales data from the server
            async function fetchSalesData() {
                const response = await fetch("{% url 'sales_data' %}");
                const data = await response.json();
                return data;
            }
    
            // Generate bright and distinct colors for stalls
            function generateBrightColor() {
                const hue = Math.floor(Math.random() * 360);  // Random hue for vibrant colors
                const saturation = 70 + Math.floor(Math.random() * 30);  // Ensure it's vibrant
                const lightness = 50 + Math.floor(Math.random() * 20);  // Keep it bright
                return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
            }
    
            function assignColorsToStalls(stalls) {
                const colors = {};
                stalls.forEach(stall => {
                    colors[stall] = generateBrightColor();
                });
                return colors;
            }
    
           // Render a Combo Chart (Line + Bar)
    function renderSalesChart(ctx, datasets, labels, title) {
        new Chart(ctx, {
            type: 'bar',  // Default to 'bar', but individual datasets can be set to 'line' or 'bar'
            data: {
                labels: labels,
                datasets: datasets.map(dataset => ({
                    ...dataset,
                    tension: 0.4, // For lines
                    type: dataset.type || 'bar' // Default to 'bar', can be overridden by dataset type
                }))
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#fff' }
                    },
                    title: {
                        display: true,
                        text: title,
                        color: '#fff',
                        font: { size: 20 }
                    }
                },
                scales: {
                    x: {
                        title: { display: true, text: 'Time', color: '#fff' },
                        ticks: { color: '#fff' },
                        grid: { color: 'rgba(255, 255, 255, 0.2)' }
                    },
                    y: {
                        title: { display: true, text: 'Sales Amount', color: '#fff' },
                        ticks: { color: '#fff', beginAtZero: true, stepSize: 1000 },
                        grid: { color: 'rgba(255, 255, 255, 0.2)' }
                    }
                }
            }
        });
    }
    
    // Main function to render all charts
    async function renderCharts() {
        const salesData = await fetchSalesData();
    
        // Extract all stall names and generate colors
        const allStalls = Object.keys({ ...salesData.weekly, ...salesData.monthly, ...salesData.annual });
        const stallColors = assignColorsToStalls(allStalls);
    
        // Generate datasets and labels for each chart
        const weeklyDatasets = Object.keys(salesData.weekly).map(stall => ({
            label: stall,
            data: salesData.weekly[stall].sales,
            borderColor: stallColors[stall],
            backgroundColor: stallColors[stall],
            borderWidth: 2,
            fill: false,
            tension: 0.1,
            type: 'line'  // Specify this dataset as a line chart
        }));
        const weeklyLabels = salesData.weekly[Object.keys(salesData.weekly)[0]].labels;
    
        const monthlyDatasets = Object.keys(salesData.monthly).map(stall => ({
            label: stall,
            data: salesData.monthly[stall].sales,
            borderColor: stallColors[stall],
            backgroundColor: stallColors[stall],
            borderWidth: 2,
            fill: false,
            tension: 0.1,
            type: 'bar'  // Specify this dataset as a bar chart
        }));
        const monthlyLabels = salesData.monthly[Object.keys(salesData.monthly)[0]].labels;
    
        const annualDatasets = Object.keys(salesData.annual).map(stall => ({
            label: stall,
            data: salesData.annual[stall].sales,
            borderColor: stallColors[stall],
            backgroundColor: stallColors[stall],
            borderWidth: 2,
            fill: false,
            tension: 0.1,
            type: 'line'  // Specify this dataset as a line chart
        }));
        const annualLabels = salesData.annual[Object.keys(salesData.annual)[0]].labels;
    
        // Render combo charts
        renderSalesChart(document.getElementById('weeklySalesChart').getContext('2d'), weeklyDatasets, weeklyLabels, 'Weekly Sales of Different Stalls');
        renderSalesChart(document.getElementById('monthlySalesChart').getContext('2d'), monthlyDatasets, monthlyLabels, 'Monthly Sales of Different Stalls');
        renderSalesChart(document.getElementById('annualSalesChart').getContext('2d'), annualDatasets, annualLabels, 'Annual Sales of Different Stalls');
    }
    
    document.addEventListener('DOMContentLoaded', renderCharts);