// src/App.js
import React, { useState } from 'react';
import './App.css';

function App() {
  const [topic, setTopic] = useState('');
  const [briefing, setBriefing] = useState(null);
  const [status, setStatus] = useState('Enter a topic to generate a live intelligence briefing.');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!topic || isLoading) return;

    setIsLoading(true);
    setBriefing(null);
    setStatus(`Generating live briefing for "${topic}"... This may take up to 30 seconds.`);

    try {
      const response = await fetch(`http://127.0.0.1:5000/api/analyze/${encodeURIComponent(topic)}`);
      const data = await response.json();

      // --- THIS IS THE FIX ---
      // We now check if the response was NOT ok, or if the data contains an error key.
      if (!response.ok || data.error) {
        throw new Error(data.error || 'An unknown error occurred during analysis.');
      }
      // -----------------------
      
      setBriefing(data);
      setStatus(`Briefing complete for "${topic}".`);

    } catch (error) {
      setStatus(`Error: ${error.message}`);
      console.error("Error fetching briefing:", error);
    } finally {
      setIsLoading(false);
    }
  };
  
  // The rest of the App.js component remains the same
  // ... (getTRLColor function, return() statement with JSX) ...
  return (
    <div className="container">
      <h1>🦅 AETOS Live Intelligence Briefing</h1>
      <div className="search-container">
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="Enter a technology topic..."
            disabled={isLoading}
          />
          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Generating...' : 'Generate Briefing'}
          </button>
        </form>
      </div>
      <div className="status-bar">{status}</div>
      
      {briefing && (
        <div className="briefing-card">
          <h2>Strategic Briefing: {topic}</h2>
          <div className="summary-section">
            <h3>Executive Summary</h3>
            <p>{briefing.strategic_summary}</p>
          </div>
          <div className="details-grid">
            <div>
              <h3>Aggregate TRL</h3>
              <div className="trl-display">TRL {briefing.aggregate_TRL}</div>
              <p className="trl-justification">{briefing.TRL_justification}</p>
            </div>
            <div>
              <h3>Key Technologies</h3>
              <ul className="tech-list">
                {briefing.key_technologies?.map((t, i) => <li key={i}>{t}</li>)}
              </ul>
            </div>
            <div>
              <h3>Emerging Convergences</h3>
              <ul className="relations-list">
                {briefing.emerging_convergences?.map((r, i) => (
                  <li key={i}><strong>{r.subject}</strong> {r.relationship} <strong>{r.object}</strong></li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;