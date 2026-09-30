/**
 * Retail Sales Forecasting & Business Analytics - Frontend JavaScript
 * Author: Lakshana R, Kumaraguru College of Liberal Arts and Science, Coimbatore
 */

let currentCurrency = '₹'; // Default to Indian Rupee (or $ via toggle)
let dashboardData = null;
let actualVsPredictedChartInstance = null;
let monthlyTrendChartInstance = null;
let categoryChartInstance = null;

// Format Currency
function formatMoney(amount, currency = currentCurrency) {
  if (amount === null || amount === undefined || isNaN(amount)) return `${currency}0.00`;
  const num = Number(amount);
  return `${currency}${num.toLocaleString('en-IN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })}`;
}

// Currency Switcher
function setCurrency(curr) {
  currentCurrency = curr;
  document.getElementById('curr-inr').classList.toggle('active', curr === '₹');
  document.getElementById('curr-usd').classList.toggle('active', curr === '$');

  if (dashboardData) {
    updateKpisDisplay();
    onMonthSelected();
    if (actualVsPredictedChartInstance) actualVsPredictedChartInstance.update();
    if (monthlyTrendChartInstance) monthlyTrendChartInstance.update();
    if (categoryChartInstance) categoryChartInstance.update();
  }
}

// Update KPI cards with selected currency
function updateKpisDisplay() {
  if (!dashboardData || !dashboardData.kpis) return;
  const k = dashboardData.kpis;

  document.getElementById('kpi-total-sales').textContent = formatMoney(k.total_sales);
  document.getElementById('kpi-avg-sales').textContent = formatMoney(k.avg_monthly_sales);
  document.getElementById('kpi-high-month').textContent = k.highest_month.month_name;
  document.getElementById('kpi-high-val').textContent = `Sales: ${formatMoney(k.highest_month.sales)}`;
  document.getElementById('kpi-low-month').textContent = k.lowest_month.month_name;
  document.getElementById('kpi-low-val').textContent = `Sales: ${formatMoney(k.lowest_month.sales)}`;

  // Metric numbers
  document.getElementById('metric-r2').textContent = k.model_metrics.r2_score;
  document.getElementById('metric-mae').textContent = formatMoney(k.model_metrics.mae);
  document.getElementById('metric-mse').textContent = Number(k.model_metrics.mse).toLocaleString('en-IN', { maximumFractionDigits: 0 });
  document.getElementById('metric-rmse').textContent = formatMoney(k.model_metrics.rmse);
}

// Load initial dashboard data from Flask API
async function loadDashboardData() {
  try {
    const response = await fetch('/api/dashboard_data');
    if (!response.ok) throw new Error('Network error loading dashboard data');
    dashboardData = await response.json();

    updateKpisDisplay();
    initCharts();
    onMonthSelected();
  } catch (error) {
    console.error('Error fetching dashboard data:', error);
  }
}

// Handle Month Selection Change
async function onMonthSelected() {
  const selectEl = document.getElementById('month-select');
  if (!selectEl) return;
  const selectedMonth = selectEl.value;

  try {
    const response = await fetch(`/api/predict?month=${encodeURIComponent(selectedMonth)}`);
    if (!response.ok) throw new Error('Prediction API failed');
    const result = await response.json();

    if (result.status === 'success') {
      // Display Actual Sales
      document.getElementById('display-actual').textContent = formatMoney(result.actual_sales);
      document.getElementById('meta-actual').textContent = `Quantity: ${result.quantity} units • Avg Discount: ${result.discount_pct}%`;

      // Display Predicted Sales from Linear Regression
      document.getElementById('display-predicted').textContent = formatMoney(result.predicted_sales);
      document.getElementById('meta-predicted').textContent = `Linear Regression Model Output`;

      // Display Difference
      const diffVal = result.difference;
      const absDiff = result.abs_difference;
      const diffEl = document.getElementById('display-diff');
      const badgeEl = document.getElementById('diff-badge');

      if (diffVal >= 0) {
        diffEl.textContent = `+${formatMoney(absDiff)}`;
        diffEl.style.color = '#16A34A';
        badgeEl.textContent = 'Actual > Predicted';
        badgeEl.style.color = '#16A34A';
        badgeEl.style.backgroundColor = '#DCFCE7';
      } else {
        diffEl.textContent = `-${formatMoney(absDiff)}`;
        diffEl.style.color = '#EA580C';
        badgeEl.textContent = 'Actual < Predicted';
        badgeEl.style.color = '#EA580C';
        badgeEl.style.backgroundColor = '#FFEDD5';
      }

      document.getElementById('meta-diff').textContent = `Variance: ${Math.abs(result.difference_pct)}% (${formatMoney(absDiff)})`;

      // Highlight point on chart
      highlightMonthOnChart(selectedMonth);
    }
  } catch (err) {
    console.error('Prediction fetch error:', err);
  }
}

// Highlight selected month on the main comparison chart
function highlightMonthOnChart(selectedMonthName) {
  if (!actualVsPredictedChartInstance || !dashboardData) return;
  const labels = dashboardData.months_data.map(m => m.month_name);
  const targetIndex = labels.indexOf(selectedMonthName);

  if (targetIndex !== -1) {
    // Generate point radius array
    const pointRadii = labels.map((_, i) => (i === targetIndex ? 8 : 2.5));
    const pointBorderWidths = labels.map((_, i) => (i === targetIndex ? 3 : 1));
    const pointColors = labels.map((_, i) => (i === targetIndex ? '#F59E0B' : '#EA580C'));

    actualVsPredictedChartInstance.data.datasets[1].pointRadius = pointRadii;
    actualVsPredictedChartInstance.data.datasets[1].pointHoverRadius = 9;
    actualVsPredictedChartInstance.data.datasets[1].pointBorderWidth = pointBorderWidths;
    actualVsPredictedChartInstance.data.datasets[1].pointBackgroundColor = pointColors;
    actualVsPredictedChartInstance.update();
  }
}

// Initialize Visualizations using Chart.js
function initCharts() {
  if (!dashboardData || typeof Chart === 'undefined') return;

  const months = dashboardData.months_data;
  const labels = months.map(m => m.month_name);
  const actualSales = months.map(m => m.actual_sales);
  const predictedSales = months.map(m => m.predicted_sales);

  Chart.defaults.font.family = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";
  Chart.defaults.color = '#64748B';

  // 1. Main Comparison Line Chart: Actual vs Predicted Sales
  const ctxCompare = document.getElementById('actualVsPredictedChart');
  if (ctxCompare) {
    actualVsPredictedChartInstance = new Chart(ctxCompare, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Actual Sales',
            data: actualSales,
            borderColor: '#0F172A',
            backgroundColor: 'rgba(15, 23, 42, 0.04)',
            borderWidth: 2.2,
            tension: 0.25,
            fill: false,
            pointRadius: 2.5,
            pointBackgroundColor: '#0F172A'
          },
          {
            label: 'Predicted Sales (Linear Regression)',
            data: predictedSales,
            borderColor: '#EA580C',
            backgroundColor: 'rgba(234, 88, 12, 0.08)',
            borderWidth: 2.5,
            borderDash: [5, 4],
            tension: 0.25,
            fill: true,
            pointRadius: 2.5,
            pointBackgroundColor: '#EA580C'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: 'index',
          intersect: false
        },
        plugins: {
          legend: {
            display: false // Using custom HTML legend
          },
          tooltip: {
            backgroundColor: '#0F172A',
            titleColor: '#FFFFFF',
            bodyColor: '#F8FAFC',
            padding: 12,
            cornerRadius: 8,
            callbacks: {
              label: function(context) {
                return ` ${context.dataset.label}: ${formatMoney(context.raw)}`;
              }
            }
          }
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: {
              maxRotation: 45,
              minRotation: 45,
              autoSkip: true,
              maxTicksLimit: 14
            }
          },
          y: {
            grid: { color: '#F1F5F9' },
            ticks: {
              callback: function(val) {
                return `${currentCurrency}${(val / 1000).toFixed(0)}k`;
              }
            }
          }
        }
      }
    });
  }

  // 2. Monthly Sales Trend Bar / Area Chart
  const ctxTrend = document.getElementById('monthlyTrendChart');
  if (ctxTrend) {
    monthlyTrendChartInstance = new Chart(ctxTrend, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Monthly Revenue',
            data: actualSales,
            backgroundColor: 'rgba(234, 88, 12, 0.75)',
            hoverBackgroundColor: '#EA580C',
            borderRadius: 4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: function(ctx) {
                return ` Sales: ${formatMoney(ctx.raw)}`;
              }
            }
          }
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: {
              maxRotation: 45,
              minRotation: 45,
              autoSkip: true,
              maxTicksLimit: 8
            }
          },
          y: {
            grid: { color: '#F1F5F9' },
            ticks: {
              callback: function(val) {
                return `${currentCurrency}${(val / 1000).toFixed(0)}k`;
              }
            }
          }
        }
      }
    });
  }

  // 3. Category Sales Doughnut Chart
  const ctxCat = document.getElementById('categoryChart');
  if (ctxCat && dashboardData.category_sales) {
    const catLabels = Object.keys(dashboardData.category_sales);
    const catValues = Object.values(dashboardData.category_sales);

    categoryChartInstance = new Chart(ctxCat, {
      type: 'doughnut',
      data: {
        labels: catLabels,
        datasets: [
          {
            data: catValues,
            backgroundColor: [
              '#EA580C', // Vibrant Orange
              '#F97316', // Lighter Orange
              '#FB923C'  // Soft Amber
            ],
            borderColor: '#FFFFFF',
            borderWidth: 3
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              padding: 14,
              font: { size: 12, weight: '600' }
            }
          },
          tooltip: {
            callbacks: {
              label: function(ctx) {
                return ` ${ctx.label}: ${formatMoney(ctx.raw)}`;
              }
            }
          }
        },
        cutout: '62%'
      }
    });
  }
}

// Start application
window.addEventListener('DOMContentLoaded', () => {
  loadDashboardData();
});
