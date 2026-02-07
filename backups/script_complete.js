// ============================================================================
// Dashboard BI - Frontend JavaScript Completo
// Implementa TODOS los requerimientos del examen
// ============================================================================

const API_BASE = window.location.origin;

// Estado global de filtros
let currentFilters = {
    startDate: null,
    endDate: null,
    city: null,
    channel: null
};

// ============================================================================
// INICIALIZACIÓN
// ============================================================================
document.addEventListener('DOMContentLoaded', async () => {
    await loadFilterOptions();
    loadExecutiveDashboard();
});

// ============================================================================
// FILTROS
// ============================================================================
async function loadFilterOptions() {
    try {
        const response = await fetch(`${API_BASE}/api/filters`);
        const filters = await response.json();
        
        // Poblar select de ciudades
        const citySelect = document.getElementById('filterCity');
        filters.cities.forEach(city => {
            const option = document.createElement('option');
            option.value = city;
            option.textContent = city;
            citySelect.appendChild(option);
        });
        
        // Poblar select de canales
        const channelSelect = document.getElementById('filterChannel');
        filters.channels.forEach(channel => {
            const option = document.createElement('option');
            option.value = channel;
            option.textContent = channel;
            channelSelect.appendChild(option);
        });
        
        // Configurar fechas
        const startDateInput = document.getElementById('filterStartDate');
        const endDateInput = document.getElementById('filterEndDate');
        startDateInput.value = filters.date_range.min;
        endDateInput.value = filters.date_range.max;
        startDateInput.min = filters.date_range.min;
        startDateInput.max = filters.date_range.max;
        endDateInput.min = filters.date_range.min;
        endDateInput.max = filters.date_range.max;
        
        console.log('Filtros cargados:', filters);
    } catch (error) {
        console.error('Error cargando filtros:', error);
    }
}

function applyFilters() {
    currentFilters.startDate = document.getElementById('filterStartDate').value;
    currentFilters.endDate = document.getElementById('filterEndDate').value;
    currentFilters.city = document.getElementById('filterCity').value;
    currentFilters.channel = document.getElementById('filterChannel').value;
    
    console.log('Aplicando filtros:', currentFilters);
    
    // Recargar dashboard activo
    const activePage = document.querySelector('.page:not([style*="display: none"])');
    if (activePage.id === 'executive') {
        loadExecutiveDashboard();
    } else if (activePage.id === 'drivers') {
        loadDriversDashboard();
    }
}

function clearFilters() {
    document.getElementById('filterStartDate').value = '';
    document.getElementById('filterEndDate').value = '';
    document.getElementById('filterCity').value = '';
    document.getElementById('filterChannel').value = '';
    currentFilters = { startDate: null, endDate: null, city: null, channel: null };
    applyFilters();
}

function buildQueryParams() {
    const params = new URLSearchParams();
    if (currentFilters.startDate) params.append('start_date', currentFilters.startDate);
    if (currentFilters.endDate) params.append('end_date', currentFilters.endDate);
    if (currentFilters.city) params.append('city', currentFilters.city);
    if (currentFilters.channel) params.append('channel', currentFilters.channel);
    return params.toString();
}

// ============================================================================
// NAVEGACIÓN
// ============================================================================
function showPage(pageId) {
    document.querySelectorAll('.page').forEach(page => {
        page.style.display = 'none';
    });
    document.getElementById(pageId).style.display = 'block';
    
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    event.target.classList.add('active');
    
    if (pageId === 'executive') {
        loadExecutiveDashboard();
    } else if (pageId === 'drivers') {
        loadDriversDashboard();
    }
}

// ============================================================================
// HELPERS
// ============================================================================
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value);
}

function formatNumber(value) {
    return new Intl.NumberFormat('en-US').format(value);
}

// ============================================================================
// EXECUTIVE DASHBOARD (PÁGINA 1)
// ============================================================================
async function loadExecutiveDashboard() {
    try {
        const queryParams = buildQueryParams();
        
        // KPIs
        const kpisResponse = await fetch(`${API_BASE}/api/kpis?${queryParams}`);
        const kpis = await kpisResponse.json();
        
        document.getElementById('netSalesMTD').textContent = formatCurrency(kpis.net_sales_mtd);
        document.getElementById('netSalesYTD').textContent = formatCurrency(kpis.net_sales_ytd);
        document.getElementById('grossMargin').textContent = formatCurrency(kpis.gross_margin);
        document.getElementById('grossMarginPct').textContent = `${kpis.gross_margin_pct.toFixed(1)}%`;
        document.getElementById('totalOrders').textContent = formatNumber(kpis.total_orders);
        document.getElementById('totalUnits').textContent = formatNumber(kpis.total_units);
        document.getElementById('aov').textContent = formatCurrency(kpis.aov);
        document.getElementById('returnRate').textContent = `${kpis.return_rate.toFixed(2)}%`;
        document.getElementById('totalReturns').textContent = formatCurrency(kpis.total_returns);
        
        // Tendencia Mensual
        const trendResponse = await fetch(`${API_BASE}/api/monthly-trend?${queryParams}`);
        const trend = await trendResponse.json();
        
        const months = trend.map(d => d.month);
        const netSales = trend.map(d => d.net_sales);
        const grossSales = trend.map(d => d.gross_sales);
        const pctChanges = trend.map(d => d.pct_change);
        
        // Trace 1: Gross Sales
        const trace1 = {
            x: months,
            y: grossSales,
            name: 'Gross Sales',
            type: 'scatter',
            mode: 'lines+markers',
            line: { color: '#60a5fa', width: 3 },
            marker: { size: 8 },
            hovertemplate: '%{y:$,.0f}<br>%{x}<extra></extra>'
        };
        
        // Trace 2: Net Sales
        const trace2 = {
            x: months,
            y: netSales,
            name: 'Net Sales',
            type: 'scatter',
            mode: 'lines+markers',
            line: { color: '#3b82f6', width: 3 },
            marker: { size: 8 },
            hovertemplate: '%{y:$,.0f}<br>%{x}<extra></extra>'
        };
        
        // Trace 3: % Change (barras)
        const trace3 = {
            x: months,
            y: pctChanges,
            name: '% Cambio vs Mes Anterior',
            type: 'bar',
            yaxis: 'y2',
            marker: { 
                color: pctChanges.map(v => v >= 0 ? '#10b981' : '#ef4444'),
                opacity: 0.6
            },
            hovertemplate: '%{y:.1f}%<br>%{x}<extra></extra>'
        };
        
        const layout = {
            title: 'Evolución Mensual de Ventas',
            xaxis: { title: 'Mes' },
            yaxis: { 
                title: 'Ventas ($)',
                tickformat: '$,.0f'
            },
            yaxis2: {
                title: '% Cambio',
                overlaying: 'y',
                side: 'right',
                tickformat: '.1f%',
                showgrid: false
            },
            showlegend: true,
            legend: { x: 0, y: 1.1, orientation: 'h' },
            margin: { t: 80, r: 80, b: 60, l: 80 },
            hovermode: 'x unified'
        };
        
        Plotly.newPlot('monthlyTrendChart', [trace1, trace2, trace3], layout, {responsive: true});
        
        console.log('Executive Dashboard cargado con éxito');
    } catch (error) {
        console.error('Error cargando Executive Dashboard:', error);
        alert('Error cargando datos: ' + error.message);
    }
}

// ============================================================================
// DRIVERS DASHBOARD (PÁGINA 2)
// ============================================================================
async function loadDriversDashboard() {
    try {
        const queryParams = buildQueryParams();
        
        // 1. Sales by City
        const cityResponse = await fetch(`${API_BASE}/api/sales-by-city?${queryParams}`);
        const cityData = await cityResponse.json();
        
        const cityTrace = {
            x: cityData.map(d => d.net_sales),
            y: cityData.map(d => d.city),
            type: 'bar',
            orientation: 'h',
            marker: { color: '#60a5fa' },
            hovertemplate: '%{y}: %{x:$,.0f}<extra></extra>'
        };
        
        Plotly.newPlot('salesByCityChart', [cityTrace], {
            xaxis: { title: 'Net Sales ($)', tickformat: '$,.0f' },
            yaxis: { title: '' },
            margin: { t: 30, r: 30, b: 50, l: 150 }
        }, {responsive: true});
        
        // 2. Sales by Channel
        const channelResponse = await fetch(`${API_BASE}/api/sales-by-channel?${queryParams}`);
        const channelData = await channelResponse.json();
        
        const channelTrace = {
            x: channelData.map(d => d.net_sales),
            y: channelData.map(d => d.channel),
            type: 'bar',
            orientation: 'h',
            marker: { color: '#3b82f6' },
            hovertemplate: '%{y}: %{x:$,.0f}<extra></extra>'
        };
        
        Plotly.newPlot('salesByChannelChart', [channelTrace], {
            xaxis: { title: 'Net Sales ($)', tickformat: '$,.0f' },
            yaxis: { title: '' },
            margin: { t: 30, r: 30, b: 50, l: 100 }
        }, {responsive: true});
        
        // 3. Top Products by Gross Margin
        const productsResponse = await fetch(`${API_BASE}/api/top-products?${queryParams}`);
        const products = await productsResponse.json();
        
        const productsTrace = {
            x: products.map(d => d.gross_margin),
            y: products.map(d => d.product_name),
            type: 'bar',
            orientation: 'h',
            marker: { color: '#8b5cf6' },
            text: products.map(d => `${d.gross_margin_pct.toFixed(1)}%`),
            textposition: 'auto',
            hovertemplate: '%{y}<br>Margen: %{x:$,.0f} (%{text})<extra></extra>'
        };
        
        Plotly.newPlot('topProductsChart', [productsTrace], {
            xaxis: { title: 'Gross Margin ($)', tickformat: '$,.0f' },
            yaxis: { title: '', automargin: true },
            margin: { t: 30, r: 30, b: 50, l: 150 }
        }, {responsive: true});
        
        // 4. Category Mix (Pie Chart)
        const categoryResponse = await fetch(`${API_BASE}/api/sales-by-category?${queryParams}`);
        const categoryData = await categoryResponse.json();
        
        const categoryTrace = {
            labels: categoryData.map(d => d.category),
            values: categoryData.map(d => d.net_sales),
            type: 'pie',
            textinfo: 'label+percent',
            textposition: 'inside',
            hovertemplate: '%{label}<br>Ventas: %{value:$,.0f}<br>%{percent}<extra></extra>',
            marker: {
                colors: ['#60a5fa', '#3b82f6', '#2563eb', '#1d4ed8', '#1e40af', '#1e3a8a']
            }
        };
        
        Plotly.newPlot('categoryMixChart', [categoryTrace], {
            margin: { t: 30, r: 30, b: 30, l: 30 }
        }, {responsive: true});
        
        // 5. New vs Returning Customers
        const nvReturningResponse = await fetch(`${API_BASE}/api/new-vs-returning?${queryParams}`);
        const nvReturningData = await nvReturningResponse.json();
        
        const newCustomersTrace = {
            x: nvReturningData.map(d => d.month),
            y: nvReturningData.map(d => d.new_customers),
            name: 'Nuevos Clientes',
            type: 'bar',
            marker: { color: '#10b981' },
            hovertemplate: '%{y} clientes nuevos<extra></extra>'
        };
        
        const returningCustomersTrace = {
            x: nvReturningData.map(d => d.month),
            y: nvReturningData.map(d => d.returning_customers),
            name: 'Clientes Recurrentes',
            type: 'bar',
            marker: { color: '#3b82f6' },
            hovertemplate: '%{y} clientes recurrentes<extra></extra>'
        };
        
        Plotly.newPlot('newVsReturningChart', [newCustomersTrace, returningCustomersTrace], {
            barmode: 'stack',
            xaxis: { title: 'Mes' },
            yaxis: { title: 'Número de Clientes' },
            showlegend: true,
            legend: { x: 0, y: 1.1, orientation: 'h' },
            margin: { t: 50, r: 30, b: 60, l: 60 }
        }, {responsive: true});
        
        console.log('Drivers Dashboard cargado con éxito');
    } catch (error) {
        console.error('Error cargando Drivers Dashboard:', error);
        alert('Error cargando datos: ' + error.message);
    }
}
