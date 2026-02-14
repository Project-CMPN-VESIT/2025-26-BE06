import { useState, useEffect } from 'react';
import {
    BarChart, Bar, PieChart, Pie, XAxis, YAxis, CartesianGrid, 
    Tooltip, Legend, ResponsiveContainer, Cell
} from 'recharts';
import "../styles/DataVisualizations.css";

const COLORS = {
    primary: '#0f172a',
    accent: '#334155',
    green: '#166534',
    blue: '#1e40af',
    amber: '#d97706',
    slate: '#64748b',
    red: '#991b1b',
    lightGray: '#f8fafc',
    borderGray: '#e2e8f0'
};

const CHART_COLORS = ['#0f172a', '#334155', '#475569', '#64748b', '#94a3b8', '#1e40af', '#166534', '#d97706', '#991b1b'];

function DataVisualizations() {
    const [analytics, setAnalytics] = useState(null);
    const [loading, setLoading] = useState(true);

    const API_BASE = 'http://localhost:5000';

    useEffect(() => { fetchAnalytics(); }, []);

    const fetchAnalytics = async () => {
        try {
            const response = await fetch(`${API_BASE}/api/analytics/dashboard`);
            const data = await response.json();
            setAnalytics(data);
        } catch (error) {
            console.error('Error fetching analytics:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div className="loading-state"><div className="loading-spinner"></div></div>;
    if (!analytics) return <div className="empty-state">Data Unavailable</div>;

    const CustomTooltip = ({ active, payload, label }) => {
        if (active && payload && payload.length) {
            return (
                <div className="custom-tooltip">
                    <div className="tooltip-header"><span className="tooltip-category">{payload[0].name}</span></div>
                    <div className="tooltip-body">
                        <p className="tooltip-label">{label}</p>
                        <p className="tooltip-value">{payload[0].value.toLocaleString()}</p>
                    </div>
                </div>
            );
        }
        return null;
    };

    return (
        <div className="visualizations-container">
            <div className="dashboard-header">
                <div className="header-content">
                    <h1 className="dashboard-title">Market Intelligence Dashboard</h1>
                </div>
            </div>

            <div className="metrics-section">
                <div className="section-header">
                    <h2 className="section-title">Market Overview</h2>
                    <p className="section-subtitle">Key performance indicators across all listings</p>
                </div>
                <div className="metrics-grid">
                    <div className="metric-card">
                        <p className="metric-label">Total Listings</p>
                        <h3 className="metric-value">{analytics.total_properties?.toLocaleString()}</h3>
                    </div>
                    <div className="metric-card">
                        <p className="metric-label">RERA Verified</p>
                        <h3 className="metric-value">{analytics.rera_percentage}%</h3>
                    </div>
                    <div className="metric-card">
                        <p className="metric-label">Under Construction</p>
                        <h3 className="metric-value">{analytics.under_construction_percentage}%</h3>
                    </div>
                    <div className="metric-card">
                        <p className="metric-label">Average Price</p>
                        <h3 className="metric-value">₹{analytics.average_price} Cr</h3>
                    </div>
                </div>
            </div>

            <div className="charts-section">
                <div className="section-header">
                    <h2 className="section-title">Distribution Analysis</h2>
                    <p className="section-subtitle">Detailed breakdown of market segments</p>
                </div>

                <div className="charts-grid">
                    {/* Property Type */}
                    <div className="chart-card">
                        <div className="chart-header">
                            <h3 className="chart-title">Property Type</h3>
                            <p className="chart-description">BHK configuration breakdown</p>
                        </div>
                        <ResponsiveContainer width="100%" height={250}>
                            <PieChart>
                                <Pie
                                    data={analytics.bhk_distribution}
                                    cx="50%" cy="50%" outerRadius={70}
                                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                                    dataKey="count"
                                >
                                    {analytics.bhk_distribution.map((entry, index) => (
                                        <Cell key={index} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip content={<CustomTooltip />} />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>

                    {/* Top Localities */}
                    <div className="chart-card">
                        <div className="chart-header">
                            <h3 className="chart-title">Top Localities</h3>
                            <p className="chart-description">Highest inventory concentration</p>
                        </div>
                        <ResponsiveContainer width="100%" height={250}>
                            <BarChart data={analytics.top_localities} layout="vertical" margin={{ left: 40, right: 20 }}>
                                <XAxis type="number" hide />
                                <YAxis dataKey="locality" type="category" fontSize={10} width={70} />
                                <Tooltip content={<CustomTooltip />} />
                                <Bar dataKey="count" fill={COLORS.primary} radius={[0, 4, 4, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>

                    {/* Price Range */}
                    <div className="chart-card">
                        <div className="chart-header">
                            <h3 className="chart-title">Price Range</h3>
                            <p className="chart-description">Market segment distribution</p>
                        </div>
                        <ResponsiveContainer width="100%" height={250}>
                            <BarChart data={analytics.price_distribution}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={COLORS.borderGray} />
                                <XAxis dataKey="range" fontSize={10} interval={0} />
                                <YAxis fontSize={10} />
                                <Tooltip content={<CustomTooltip />} />
                                <Bar dataKey="count" fill={COLORS.blue} radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>

                    {/* Construction Status */}
                    <div className="chart-card">
                        <div className="chart-header">
                            <h3 className="chart-title">Construction Status</h3>
                            <p className="chart-description">Ready vs Under construction</p>
                        </div>
                        <ResponsiveContainer width="100%" height={250}>
                            <PieChart>
                                <Pie
                                    data={analytics.status_distribution}
                                    innerRadius={50} outerRadius={70} paddingAngle={5}
                                    label={({ name, percent }) => `${(percent * 100).toFixed(0)}%`}
                                    dataKey="count"
                                >
                                    {analytics.status_distribution.map((entry, index) => (
                                        <Cell key={index} fill={entry.name === 'Ready To Move' ? COLORS.green : COLORS.amber} />
                                    ))}
                                </Pie>
                                <Tooltip content={<CustomTooltip />} />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>

                    {/* Furnishing */}
                    <div className="chart-card">
                        <div className="chart-header">
                            <h3 className="chart-title">Furnishing</h3>
                            <p className="chart-description">Available options breakdown</p>
                        </div>
                        <ResponsiveContainer width="100%" height={250}>
                            <BarChart data={analytics.furnishing_distribution}>
                                <XAxis dataKey="type" fontSize={10} />
                                <YAxis fontSize={10} />
                                <Tooltip content={<CustomTooltip />} />
                                <Bar dataKey="count" fill={COLORS.accent} radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>

                    {/* RERA Compliance */}
                    <div className="chart-card">
                        <div className="chart-header">
                            <h3 className="chart-title">RERA Compliance</h3>
                            <p className="chart-description">Regulatory status overview</p>
                        </div>
                        <ResponsiveContainer width="100%" height={250}>
                            <PieChart>
                                <Pie
                                    data={analytics.rera_distribution}
                                    innerRadius={50} outerRadius={70}
                                    label={({ name, percent }) => `${(percent * 100).toFixed(0)}%`}
                                    dataKey="count"
                                >
                                    {analytics.rera_distribution.map((entry, index) => (
                                        <Cell key={index} fill={entry.name === 'RERA Verified' ? COLORS.green : COLORS.red} />
                                    ))}
                                </Pie>
                                <Tooltip content={<CustomTooltip />} />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default DataVisualizations;