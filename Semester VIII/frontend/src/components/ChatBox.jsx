import { useState, useEffect, useRef } from "react";
import { askQuestion } from "../api/api";
import "../styles/ChatBox.css";

function ChatBox({ setSources, setPdf }) {
    const [question, setQuestion] = useState("");
    const [messages, setMessages] = useState([]);
    const [loading, setLoading] = useState(false);
    const chatWindowRef = useRef(null);

    const scrollToBottom = () => {
        if (chatWindowRef.current) {
            chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight;
        }
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, loading]);

    const handleAsk = async () => {
        if (!question.trim()) return;
        
        const userMessage = { role: "user", content: question };
        setMessages(prev => [...prev, userMessage]);
        setQuestion("");
        setLoading(true);

        try {
            const data = await askQuestion(question, messages);
            
            const aiMessage = { 
                role: "assistant", 
                content: data.answer,
                sources: data.sources || []
            };
            setMessages(prev => [...prev, aiMessage]);
            setSources(data.sources || []);
        } catch (err) {
            setMessages(prev => [...prev, { 
                role: "assistant", 
                content: "Error fetching answer.",
                sources: []
            }]);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleAsk();
        }
    };

    const handleSourceClick = (src) => {
        if (setPdf && typeof setPdf === 'function') {
            setPdf(`http://localhost:5000${encodeURI(src.link)}`);
        } else {
            console.error("setPdf is not a function or not provided");
        }
    };

    return (
        <section className="chat-section">
            <div className="chat-window" ref={chatWindowRef}>
                <div className="chat-content">
                    {messages.map((msg, i) => (
                        <div key={i} className={`message-container ${msg.role}`}>
                            <div className={`message-bubble ${msg.role}`}>
                                <div className="message-content">
                                    {msg.content}
                                    
                                    {msg.role === "assistant" && msg.sources && msg.sources.length > 0 && (
                                        <div className="chat-source-list">
                                            <h4>Cited Sources</h4>
                                            <ul>
                                                {msg.sources.map((src, index) => (
                                                    <li
                                                        key={index}
                                                        onClick={() => handleSourceClick(src)}
                                                        style={{ cursor: "pointer" }}
                                                    >
                                                        <span className="file-name">
                                                            {src.pdf} (Page {src.page})
                                                        </span>
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}
                                </div>
                                <div className="message-time">
                                    {msg.role === "user" ? "You" : "Assistant"}
                                </div>
                            </div>
                        </div>
                    ))}
                    {loading && (
                        <div className="message-container assistant">
                            <div className="message-bubble assistant">
                                <div className="thinking-indicator">
                                    <span className="dot"></span>
                                    <span className="dot"></span>
                                    <span className="dot"></span>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            <div className="input-container">
                <div className="input-wrapper">
                    <textarea
                        value={question}
                        onChange={(e) => setQuestion(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Ask a legal question or follow-up..."
                        rows="3"
                    />
                    <button 
                        onClick={handleAsk} 
                        disabled={loading || !question.trim()}
                        className="send-button"
                    >
                        <svg className="send-icon" viewBox="0 0 24 24">
                            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                        </svg>
                    </button>
                </div>
                <div className="input-hint">
                    Press Enter to send • Shift+Enter for new line
                </div>
            </div>
        </section>
    );
}

export default ChatBox;