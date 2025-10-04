import React, { useState, useEffect, useCallback } from 'react';
import './App.css';

function App() {
  const [topic, setTopic] = useState('');
  const [documents, setDocuments] = useState([]);
  const [status, setStatus] = useState('Enter a topic to begin analysis.');
  const [isLoading, setIsLoading] = useState(false);

  const fetchDocuments = useCallback(async (currentTopic) => {
    if (!currentTopic) return;
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/documents/${encodeURIComponent(currentTopic)}`);
      const data = await response.json();
      setDocuments(data || []);
      if (data && data.length > 0) {
        setStatus(`Displaying ${data.length} results for "${currentTopic}".`);
      } else {
        setStatus(`No results found for "${currentTopic}".`);
      }
    } catch (error) {
      console.error("Error fetching documents:", error);
      setStatus("Error fetching documents. Is the API server running?");
    }
  }, []); // Removed status from dependencies to avoid loops

  const startAnalysis = async (currentTopic) => {
    setIsLoading(true);
    setDocuments([]); // Clear old documents
    setStatus(`Submitting new analysis job for "${currentTopic}"...`);
    try {
      const resp = await fetch(`http://127.0.0.1:5000/api/analyze/${encodeURIComponent(currentTopic)}`, {
        method: 'POST',
      });
      
      const payload = await resp.json();
      setStatus(`Server response: ${payload?.status || resp.statusText}`);

      if (resp.ok) {
        fetchDocuments(currentTopic);
      }

    } catch (error) {
      setStatus("Error: Could not start analysis. Is the API server running?");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
  }, []);

  const handleSubmit = (event) => {
    event.preventDefault();
    if (topic && !isLoading) {
      startAnalysis(topic);
    }
  };
  
  const getTRLColor = (trl) => {
    if (!trl && trl !== 0) return '#6c757d';
    if (trl >= 7) return '#198754';
    if (trl >= 4) return '#ffc107';
    return '#dc3545';
  };

  return (
    <div className="container">
      <h1>🦅 AETOS Intelligence Dashboard</h1>
      <div className="search-container">
        <form onSubmit={handleSubmit}>
          <input type="text" value={topic} onChange={(e) => setTopic(e.target.value)} placeholder="Enter a technology topic..." disabled={isLoading} />
          <button type="submit" disabled={isLoading}>{isLoading ? 'Analyzing...' : 'Analyze Topic'}</button>
        </form>
      </div>
      <div className="status-bar">{status}</div>
      <table>
        <thead>
          <tr>
            <th style={{width: "50%"}}>Strategic Analysis</th>
            <th>Key Technologies & Relationships</th>
            <th>Source & Funding</th> 
          </tr>
        </thead>
        <tbody>
          {documents && documents.length > 0 ? (
            documents.map((doc) => (
              <tr key={doc.id?.$oid || doc._id?.$oid || Math.random()}>
                <td>
                  <div className="doc-title"><a href={doc.id} target="_blank" rel="noopener noreferrer">{doc.title}</a></div>
                  <div>
                    <span className="trl-badge" style={{ backgroundColor: getTRLColor(doc.TRL) }}>TRL {doc.TRL ?? 'N/A'}</span>
                    <span className="trl-justification">{doc.TRL_justification || ''}</span>
                  </div>
                  <p className="strategic-summary">{doc.strategic_summary || 'Not available.'}</p>
                </td>
                <td>
                  <strong>Technologies:</strong>
                  <ul className="tech-list">{(doc.technologies || []).map((t, i) => <li key={i}>{t}</li>)}</ul>
                  <hr />
                  <strong>Key Relationships:</strong>
                  <ul className="relations-list">{(doc.key_relationships || []).map((r, i) => <li key={i}><strong>{r.subject}</strong> {r.relationship} <strong>{r.object}</strong></li>)}</ul>
                </td>
                <td>
                  <div className="source-details">
                    <p><strong>Country:</strong> {doc.country || 'N/A'}</p>
                    <p><strong>Provider/Company:</strong> {doc.provider_company || 'N/A'}</p>
                    <p><strong>Date:</strong> {doc.published ? new Date(doc.published).toLocaleDateString() : 'N/A'}</p>
                    <p><strong>Funding:</strong> {doc.funding_details || 'N/A'}</p>
                  </div>
                </td>
              </tr>
            ))
          ) : ( <tr><td colSpan="3" style={{ textAlign: 'center' }}>No documents to display.</td></tr> )}
        </tbody>
      </table>
    </div>
  );
}

export default App;