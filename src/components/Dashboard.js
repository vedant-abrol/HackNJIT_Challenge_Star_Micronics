import React, { useState, useEffect } from 'react';

function Dashboard() {
  const [stats, setStats] = useState({
    totalReceipts: 7688,
    totalCafes: 0,
    totalRevenue: 0,
    avgOrderValue: 0
  });

  // Simulate loading stats (in real app, this would fetch from API)
  useEffect(() => {
    // Calculate cafes from the data structure
    // This is a placeholder - in production, fetch from your API
    const timer = setTimeout(() => {
      setStats(prev => ({
        ...prev,
        totalCafes: 12, // Example value
        totalRevenue: 245678.90,
        avgOrderValue: 31.95
      }));
    }, 500);

    return () => clearTimeout(timer);
  }, []);

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(value);
  };

  const formatNumber = (value) => {
    return new Intl.NumberFormat('en-US').format(value);
  };

  return (
    <div className="Dashboard">
      <div className="dashboard-header">
        <h2 className="dashboard-title">Analytics Dashboard</h2>
        <p className="dashboard-subtitle">
          Real-time insights from POS receipt data analysis
        </p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total Receipts</div>
          <div className="stat-value">{formatNumber(stats.totalReceipts)}</div>
          <div className="stat-change">Processed and analyzed</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Active Cafes</div>
          <div className="stat-value">{stats.totalCafes || '—'}</div>
          <div className="stat-change">Locations tracked</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Total Revenue</div>
          <div className="stat-value">
            {stats.totalRevenue ? formatCurrency(stats.totalRevenue) : '—'}
          </div>
          <div className="stat-change">Across all locations</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Avg Order Value</div>
          <div className="stat-value">
            {stats.avgOrderValue ? formatCurrency(stats.avgOrderValue) : '—'}
          </div>
          <div className="stat-change">Per transaction</div>
        </div>
      </div>

      <div className="dashboard-placeholder">
        <svg
          className="placeholder-icon"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M3 3V21H21V3H3ZM19 19H5V5H19V19ZM7 7H17V9H7V7ZM7 11H17V13H7V11ZM7 15H13V17H7V15Z"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
        <div className="placeholder-text">Power BI Dashboard</div>
        <div className="placeholder-subtext">
          Connect your Power BI dashboard here to visualize sales trends, 
          top-selling items, revenue by cafe, and detailed analytics.
        </div>
      </div>

      <div className="powerbi-container" style={{ display: 'none' }}>
        {/* Power BI embedded dashboard will be rendered here */}
        {/* Example integration:
          <PowerBIEmbed
            embedConfig={{
              type: 'report',
              id: 'your-report-id',
              embedUrl: 'your-embed-url',
              accessToken: 'your-access-token',
              tokenType: models.TokenType.Embed,
              settings: {
                panes: { filters: { expanded: false, visible: false } },
                background: models.BackgroundType.Transparent,
              }
            }}
          />
        */}
      </div>
    </div>
  );
}

export default Dashboard;
