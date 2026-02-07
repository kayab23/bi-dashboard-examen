// ============================================================================
// Dashboard BI - Frontend JavaScript
// ============================================================================

const API_BASE = window.location.origin;

// Navegación entre páginas
function showPage(pageId) {
    document.querySelectorAll('.page').forEach(page => {
        page.style.display = 'none';
    });
    document.getElementById(pageId).style.display = 'block';
    
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Cargar datos según la página
    if (pageId === 'executive') {
        loadExecutiveDashboard();
    } else if (pageId === 'drivers') {
        loadDriversDashboard();
    }
}

// Formatear moneda
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value);
}

// Formatear número
function formatNumber(value) {
    return new Intl.NumberFormat('en-US').format(value);
}

// ============================================================================
// Executive Dashboard
// ============================================================================
async function loadExecutiveDashboard() {
    try {
        // Cargar KPIs
        const kpisResponse = await fetch(`${API_BASE}/api/kpis`);
        const kpis = await kpisResponse.json();
        
        document.getElementById('netSalesMTD').textContent = formatCurrency(kpis.net_sales_mtd);
        document.getElementById('netSalesYTD').textContent = formatCurrency(kpis.net_sales_ytd);
        document.getElementById('grossMargin').textContent = formatCurrency(kpis.gross_margin);
        document.getElementById('grossMarginPct').textContent = `${kpis.gross_margin_pct}%`;
        document.getElementById('totalOrders').textContent = formatNumber(kpis.total_orders);
        document.getElementById('aov').textContent = formatCurrency(kpis.aov);
        document.getElementById('returnRate').textContent = `${kpis.return_rate}%`;
        document.getElementById('totalReturns').textContent = formatCurrency(kpis.total_returns);
        
        // Cargar tendencia mensual
        const trendResponse = await fetch(`${API_BASE}/api/monthly-trend`);
        const trend = await trendResponse.json();
        
        const months = trend.map(d => d.month);
        const netSales = trend.map(d => d.net_sales);
        const grossSales = trend.map(d => d.gross_sales);
        
        const trendTrace1 = {
            x: months,
            y: grossSales,
            name: 'Gross Sales',
            type: 'scatter',
            mode: 'lines+markers',
            line: { color: '#667eea', width: 3 },
            marker: { size: 8 }
        };
        
        const trendTrace2 = {
            x: months,
            y: netSales,
            name: 'Net Sales',
            type: 'scatter',
            mode: 'lines+markers',
            line: { color: '#764ba2', width: 3 },
            marker: { size: 8 }
        };
        
        const layout = {
            title: '',
            xaxis: { title: 'Mes' },
            yaxis: { title: 'Ventas ($)' },
            showlegend: true,
            legend: { x: 0, y: 1.1, orientation: 'h' },
            margin: { t: 30, r: 30, b: 50, l: 80 }
        };
        
        Plotly.newPlot('monthlyTrendChart', [trendTrace1, trendTrace2], layout, {responsive: true});
        
    } catch (error) {
        console.error('Error cargando Executive Dashboard:', error);
    }
}

// ============================================================================
// Drivers Dashboard
// ============================================================================
async function loadDriversDashboard() {
    try {
        // Sales by City
        const cityResponse = await fetch(`${API_BASE}/api/sales-by-city`);
        const cityData = await cityResponse.json();
        
        const cityTrace = {
            x: cityData.map(d => d.net_sales),
            y: cityData.map(d => d.city),
            type: 'bar',
            orientation: 'h',
            marker: { color: '#667eea' }
        };
        
        const cityLayout = {
            title: '',
            xaxis: { title: 'Net Sales ($)' },
            yaxis: { title: '' },
            margin: { t: 30, r: 30, b: 50, l: 100 }
        };
        
        Plotly.newPlot('salesByCityChart', [cityTrace], cityLayout, {responsive: true});
        
        // Top Products
        const productsResponse = await fetch(`${API_BASE}/api/top-products`);
        const products = await productsResponse.json();
        
        const productsTrace = {
            x: products.map(d => d.gross_margin),
            y: products.map(d => d.product_name),
            type: 'bar',
            orientation: 'h',
            marker: { color: '#764ba2' },
            text: products.map(d => `${d.gross_margin_pct}%`),
            textposition: 'auto'
        };
        
        const productsLayout = {
            title: '',
            xaxis: { title: 'Gross Margin ($)' },
            yaxis: { title: '' },
            margin: { t: 30, r: 30, b: 50, l: 150 }
        };
        
        Plotly.newPlot('topProductsChart', [productsTrace], productsLayout, {responsive: true});
        
    } catch (error) {
        console.error('Error cargando Drivers Dashboard:', error);
    }
}

// Cargar dashboard inicial
document.addEventListener('DOMContentLoaded', () => {
    loadExecutiveDashboard();
});
