import { useState } from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import ChatBox from "./components/ChatBox";
import PdfViewer from "./components/PdfViewer";
import ReraProjects from "./components/ReraProjects";
import Home from "./components/Home";
import ScraperDashboard from './components/ScraperDashboard';
import "./styles/App.css";

function App() {
    const [answer, setAnswer] = useState("");
    const [sources, setSources] = useState([]);
    const [pdf, setPdf] = useState(null);

    return (
        <Router>
            <nav className="navbar">
                <Link to="/">Home</Link>
                <Link to="/assistant">Legal Assistant</Link>
                <Link to="/projects">Rera Dashboard</Link>
                <Link to="/scraper">Property Dashboard</Link>
            </nav>

            <Routes>
                <Route path="/" element={<Home />} />

                <Route path="/assistant" element={
                    <div className="app-container">
                        <aside className="sidebar">
                            <ChatBox
                                answer={answer}
                                setAnswer={setAnswer}
                                setSources={setSources}
                                setPdf={setPdf}
                            />
                            {/* <SourceList
                                sources={sources}
                                setPdf={setPdf}
                            /> */}
                        </aside>
                        <main className="viewer-panel">
                            <PdfViewer pdf={pdf} />
                        </main>
                    </div>
                } />

                <Route path="/projects" element={
                    <div style={{ padding: "0" }}>
                        <ReraProjects />
                    </div>
                } />

                <Route path="/scraper" element={
                    <div style={{ padding: "20px", maxWidth: "1200px", margin: "0 auto" }}>
                        <ScraperDashboard />
                    </div>
                } />
            </Routes>
        </Router>
    );
}

export default App;