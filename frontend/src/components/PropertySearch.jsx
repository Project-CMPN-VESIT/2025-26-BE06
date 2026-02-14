import { useState } from 'react';
import '../styles/PropertySearch.css';

function PropertySearch() {
    const [query, setQuery] = useState('');
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState(null);
    const [error, setError] = useState('');

    const handleSearch = async () => {
        if (!query.trim()) {
            setError('VALID QUERY REQUIRED');
            return;
        }

        setLoading(true);
        setError('');
        setResults(null);

        try {
            const response = await fetch('http://localhost:5000/api/properties/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: query, max_results: 12 })
            });

            const data = await response.json();
            if (data.success) {
                setResults(data);
            } else {
                setError(data.error || 'NO MATCHING ASSETS FOUND');
            }
        } catch (err) {
            setError('NETWORK COMMUNICATION FAILURE');
        } finally {
            setLoading(false);
        }
    };

    const handleKeyPress = (e) => { if (e.key === 'Enter') handleSearch(); };

    const formatPrice = (price) => {
        if (!price || price === 'N/A') return 'PRICE UPON REQUEST';
        return price.toUpperCase();
    };

    return (
        <div className="property-search">
            <div className="search-header">
                <h2 className="search-title">Property Intelligence Search</h2>
                <p className="search-subtitle">NATURAL LANGUAGE PROCESSING INTERFACE</p>
            </div>

            <div className="search-container">
                <div className="search-box">
                    <input
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="SEARCH PARAMETERS (E.G. '2 BHK ANDHERI UNDER 2 CR')"
                        className="search-input"
                        disabled={loading}
                    />
                    <button
                        onClick={handleSearch}
                        disabled={loading || !query.trim()}
                        className="search-button"
                    >
                        {loading ? 'PROCESSING...' : 'EXECUTE SEARCH'}
                    </button>
                </div>

                {error && <div className="error-message">SYSTEM ERROR: {error}</div>}

                <div className="query-examples">
                    <span className="examples-label">SEARCH SUGGESTIONS:</span>
                    <div className="examples-grid">
                        <button onClick={() => setQuery("2 BHK in Andheri under 2 crore")} className="example-chip">ANDHERI 2 BHK &lt; 2CR</button>
                        <button onClick={() => setQuery("RERA approved flats in Powai")} className="example-chip">POWAI RERA APPROVED</button>
                        <button onClick={() => setQuery("Ready to move 3 BHK")} className="example-chip">READY 3 BHK</button>
                        <button onClick={() => setQuery("3 BHK in Mulund under 3 crore")} className="example-chip">MULUND 3 BHK &lt; 3CR</button>
                    </div>
                </div>
            </div>

            {results && (
                <div className="results-container">
                    <div className="interpretation-card">
                        <h3 className="card-label-small">LOGIC INTERPRETATION</h3>
                        <p className="interpretation-text">{results.interpretation.toUpperCase()}</p>
                        <div className="results-summary">
                            <span className="matches-count">{results.matches_found} ASSETS LOCATED</span>
                            <span className="query-text">INPUT: "{results.query.toUpperCase()}"</span>
                        </div>
                    </div>

                    <div className="properties-grid">
                        {results.properties && results.properties.length > 0 ? (
                            results.properties.map((property, index) => (
                                <div key={index} className="property-card">
                                    <div className="property-card-header">
                                        <div className="property-source">
                                            <span className="source-tag">HOUSING.COM</span>
                                            <span className={`rera-tag ${property.rera_flag === 'Yes' ? 'approved' : 'pending'}`}>
                                                {property.rera_flag === 'Yes' ? 'RERA COMPLIANT' : 'RERA PENDING'}
                                            </span>
                                        </div>
                                        <span className="status-tag">
                                            {property.ready_to_move === 'Yes' ? 'READY TO MOVE' : 'UNDER CONSTRUCTION'}
                                        </span>
                                    </div>

                                    <div className="property-card-body">
                                        <h3 className="property-name">{property.project_name.toUpperCase()}</h3>
                                        <div className="property-location">
                                            <span className="location-label">LOCATION:</span>
                                            <span className="location-text">{property.locality.toUpperCase()}</span>
                                        </div>

                                        <div className="property-details-grid">
                                            <div className="detail-item">
                                                <span className="detail-label">CONFIG</span>
                                                <span className="detail-value">{property.configuration.toUpperCase()}</span>
                                            </div>
                                            <div className="detail-item">
                                                <span className="detail-label">AREA</span>
                                                <span className="detail-value">
                                                    {property.builtup_area !== 'N/A' ? property.builtup_area.toUpperCase() : 'TBA'}
                                                </span>
                                            </div>
                                            <div className="detail-item">
                                                <span className="detail-label">POSSESSION</span>
                                                <span className="detail-value">
                                                    {property.possession_date !== 'N/A' ? property.possession_date.toUpperCase() : 'TBA'}
                                                </span>
                                            </div>
                                            <div className="detail-item">
                                                <span className="detail-label">UPDATED</span>
                                                <span className="detail-value">
                                                    {property.updated_on !== 'N/A' ? property.updated_on.toUpperCase() : 'N/A'}
                                                </span>
                                            </div>
                                        </div>

                                        <div className="property-price">
                                            <span className="price-label">VALUATION</span>
                                            <span className="price-value">{formatPrice(property.price)}</span>
                                        </div>
                                    </div>
                                </div>
                            ))
                        ) : (
                            <div className="no-results">
                                <h3>NULL RESULT</h3>
                                <p>No assets match the current search parameters.</p>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}

export default PropertySearch;