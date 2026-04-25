import { useState, useEffect } from 'react';
import PropertySearch from './PropertySearch';
import "../styles/ScraperDashboard.css";
import DataVisualizations from './DataVisualizations';
import "../styles/ScraperDashboard.css";

function ScraperDashboard() {
    const [versions, setVersions] = useState([]);
    const [scrapingStats, setScrapingStats] = useState({
        lastScrape: null,
    });

    const API_BASE = 'http://localhost:5000';

    const fetchVersions = async () => {
        try {
            const response = await fetch(`${API_BASE}/api/scrape/versions`);
            if (!response.ok) throw new Error('Failed to fetch');
            const data = await response.json();
            setVersions(data.versions || []);

            if (data.versions && data.versions.length > 0) {
                setScrapingStats({
                    lastScrape: data.versions[0]?.timestamp || null,
                });
            }
        } catch (error) {
            console.error('Error fetching versions:', error);
        }
    };

    useEffect(() => {
        fetchVersions();
    }, []);

    const getNextUpdateDate = () => {
        if (!scrapingStats.lastScrape) return "PENDING SYNC";
        const nextDate = new Date(scrapingStats.lastScrape);
        nextDate.setDate(nextDate.getDate() + 3);
        return nextDate.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' }).toUpperCase();
    };

    const formatDate = (timestamp) => {
        return timestamp ? new Date(timestamp).toLocaleString('en-GB', { hour12: false }).toUpperCase() : 'N/A';
    };

    return (
        <div className="scraper-page">
            <div className="scraper-dashboard">
                <div className="dashboard-header">
                    <h1 className="dashboard-title">DATA UPDATE DASHBOARD</h1>
                </div>

                <div className="stats-grid">
                    <div className="stat-card">
                        <h3 className="stat-title">System Status</h3>
                        <p className="stat-value status-text-active">ACTIVE</p>
                        <p className="stat-description">Background scheduler operational</p>
                    </div>
                    
                    <div className="stat-card">
                        <h3 className="stat-title">Last Database Sync</h3>
                        <p className="stat-value">
                            {scrapingStats.lastScrape ? new Date(scrapingStats.lastScrape).toLocaleDateString(undefined, {month: 'short', day: 'numeric'}).toUpperCase() : 'NONE'}
                        </p>
                        <p className="stat-description">Version head timestamp</p>
                    </div>
                    
                    <div className="stat-card">
                        <h3 className="stat-title">Next Scheduled Sync</h3>
                        <p className="stat-value accent-text">
                            {getNextUpdateDate()}
                        </p>
                        <p className="stat-description">Calculated recurring window</p>
                    </div>
                </div>

                <div className="version-history">
                    <div className="section-header">
                        <h2 className="section-title">Version Control History</h2>
                        <button onClick={fetchVersions} className="refresh-button">
                            REFRESH DATA
                        </button>
                    </div>
                    <div className="versions-table">
                        <table>
                            <thead>
                                <tr>
                                    <th>Reference ID</th>
                                    <th>Data Source</th>
                                    <th>Timestamp</th>
                                    <th>Record Count</th>
                                    <th>Execution Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {versions.map(v => (
                                    <tr key={v.id} className="version-row">
                                        <td className="version-id">REV_{v.id}</td>
                                        <td>
                                            <div className="source-cell">
                                                <div className={`source-indicator ${v.source === '99acres' ? 'indicator-primary' : 'indicator-secondary'}`}></div>
                                                <span className="source-label">{v.source.toUpperCase()}</span>
                                            </div>
                                        </td>
                                        <td>{formatDate(v.timestamp)}</td>
                                        <td>{v.records_count.toLocaleString()}</td>
                                        <td><span className={`status-badge status-${v.status}`}>{v.status.toUpperCase()}</span></td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                        
                        {versions.length === 0 && (
                            <div className="empty-state">
                                <h3>NO HISTORY AVAILABLE</h3>
                                <p>Initialize system scan to generate logs.</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            <DataVisualizations />

            <div className="search-container-wrapper">
                <PropertySearch />
            </div>
        </div>
    );
}

export default ScraperDashboard;