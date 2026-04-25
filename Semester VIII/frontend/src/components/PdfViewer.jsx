import { useState, useEffect } from "react";
import "../styles/PdfViewer.css";

function PdfViewer({ pdf }) {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(false);

    useEffect(() => {
        setLoading(true);
        setError(false);
    }, [pdf]);

    const handleLoad = () => {
        setLoading(false);
    };

    const handleError = () => {
        setLoading(false);
        setError(true);
    };

    if (!pdf) {
        return (
            <div className="pdf-placeholder">
                <div className="placeholder-icon">
                    <svg viewBox="0 0 24 24">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z" />
                        <path d="M14 2v6h6" />
                    </svg>
                </div>
                <h3>Document Viewer</h3>
                <p>Select a cited source from the chat to view the PDF document</p>
            </div>
        );
    }

    return (
        <div className="pdf-viewer-container">

            <div className="pdf-content">
                {loading && (
                    <div className="pdf-loading">
                        <div className="loading-spinner">
                            <div className="spinner"></div>
                        </div>
                        <p>Loading document...</p>
                    </div>
                )}

                {error ? (
                    <div className="pdf-error">
                        <h4>Failed to load document</h4>
                        <p>The PDF could not be loaded. Please check the link or try again.</p>
                        <button
                            className="retry-btn"
                            onClick={() => window.location.reload()}
                        >
                            Retry
                        </button>
                    </div>
                ) : (
                    <iframe
                        key={pdf}
                        src={pdf}
                        title="PDF Viewer"
                        className="pdf-frame"
                        onLoad={handleLoad}
                        onError={handleError}
                    />
                )}
            </div>

            <div className="pdf-footer">
                <span className="pdf-status">
                    {loading ? 'Loading...' : 'Ready'}
                </span>
                <span className="pdf-hint">
                    Use scroll to navigate • Ctrl+ to zoom
                </span>
            </div>
        </div>
    );
}

export default PdfViewer;