import { Link } from "react-router-dom";
import "../styles/Home.css";

function Home() {
    return (
        <div className="home-container">
            {/* Hero Section */}
            <div className="hero-section">
                <div className="hero-content">
                    <h1 className="hero-title">INDREVA</h1>
                    <p className="hero-subtitle">
                        India Real Estate Valuation and Risk Assessment Framework
                    </p>
                </div>
            </div>

            {/* Features Grid */}
            <div className="features-section">
                <div className="section-header">
                    <h2 className="section-title">Regulatory & Market Intelligence</h2>
                    <p className="section-subtitle">
                        Built-in tools for risk assessment, legal clarity, and infrastructure scoring
                    </p>
                </div>
                
                <div className="features-grid">
                    <Link to="/rera-projects" className="feature-card">
                        <div className="feature-icon">
                            <div className="icon-building"></div>
                        </div>
                        <div className="feature-content">
                            <h3 className="feature-title">RERA Risk Dashboard</h3>
                            <p className="feature-description">
                                Monitor district-wide compliance scores, QPR filing status, and project risk levels across Maharashtra.
                            </p>
                            <div className="feature-cta">Analyze Compliance</div>
                        </div>
                    </Link>

                    <Link to="/assistant" className="feature-card">
                        <div className="feature-icon">
                            <div className="icon-chat"></div>
                        </div>
                        <div className="feature-content">
                            <h3 className="feature-title">Legal AI Assistant</h3>
                            <p className="feature-description">
                                RAG-powered chatbot providing cited legal answers from MahaRERA regulatory documents and circulars.
                            </p>
                            <div className="feature-cta">Ask Legal Query</div>
                        </div>
                    </Link>

                    <Link to="/amenities" className="feature-card">
                        <div className="feature-icon">
                            <div className="icon-map"></div>
                        </div>
                        <div className="feature-content">
                            <h3 className="feature-title">Infrastructure Scoring</h3>
                            <p className="feature-description">
                                Automated amenity weights and commute stress analysis using real-time OpenStreetMap data.
                            </p>
                            <div className="feature-cta">View Locality Score</div>
                        </div>
                    </Link>

                    <Link to="/analytics" className="feature-card">
                        <div className="feature-icon">
                            <div className="icon-analytics"></div>
                        </div>
                        <div className="feature-content">
                            <h3 className="feature-title">Market Intelligence</h3>
                            <p className="feature-description">
                                Price trends, RERA verification distributions, and BHK configuration analysis for major urban centers.
                            </p>
                            <div className="feature-cta">View Market Trends</div>
                        </div>
                    </Link>
                </div>
            </div>

            {/* Quick Actions */}
            <div className="quick-actions-section">
                <div className="section-header">
                    <h2 className="section-title">Direct Regulatory Links</h2>
                    <p className="section-subtitle">
                        Official MahaRERA resources and public verification portals
                    </p>
                </div>
                
                <div className="actions-grid">
                    <a href="https://maharera.maharashtra.gov.in" target="_blank" rel="noopener noreferrer" className="action-item">
                        <div className="action-content">
                            <h3 className="action-title">MahaRERA Portal</h3>
                            <p className="action-description">Official Government of Maharashtra regulatory website</p>
                        </div>
                    </a>
                    <a href="https://maharera.maharashtra.gov.in/project-search" target="_blank" rel="noopener noreferrer" className="action-item">
                        <div className="action-content">
                            <h3 className="action-title">Project Search</h3>
                            <p className="action-description">Verify registration and official project certificates</p>
                        </div>
                    </a>
                </div>
            </div>

            {/* Recent Updates */}
            <div className="updates-section">
                <div className="section-header">
                    <h2 className="section-title">Pipeline Status</h2>
                    <p className="section-subtitle">
                        Monitoring automated data acquisition and system health
                    </p>
                </div>
                
                <div className="status-grid">
                    <div className="status-card">
                        <div className="status-indicator active"></div>
                        <div className="status-content">
                            <h3 className="status-title">Data Pipeline</h3>
                            <p className="status-description">72-hour automated background scrape active</p>
                            <div className="status-time">Last Sync: Successful</div>
                        </div>
                    </div>

                    <div className="status-card">
                        <div className="status-indicator active"></div>
                        <div className="status-content">
                            <h3 className="status-title">AI Core Availability</h3>
                            <p className="status-description">Ollama LLM & FAISS Vector Engine operational</p>
                            <div className="status-time">99.9% Uptime</div>
                        </div>
                    </div>

                    <div className="status-card">
                        <div className="status-indicator active"></div>
                        <div className="status-content">
                            <h3 className="status-title">Analytical Lake</h3>
                            <p className="status-description">2.1M+ Regulatory & Property Records processed</p>
                            <div className="status-time">Total: 2,165,808 Records</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Home;