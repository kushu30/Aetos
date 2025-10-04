import React, { useState, useEffect } from 'react';
import { Line, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top',
      labels: {
        color: '#e0e0e0'
      }
    },
  },
  scales: {
    x: {
      ticks: { color: '#e0e0e0' },
      grid: { color: 'rgba(255, 255, 255, 0.1)' }
    },
    y: {
      ticks: { color: '#e0e0e0' },
      grid: { color: 'rgba(255, 255, 255, 0.1)' }
    }
  }
};

const AnalyticsDashboard = ({ topic }) => {
  const [synthesis, setSynthesis] = useState(null);
  const [sCurveData, setSCurveData] = useState(null);
  const [convergenceData, setConvergenceData] = useState(null);
  const [trlData, setTrlData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!topic) return;

    const fetchAnalytics = async () => {
      setLoading(true);
      try {
        const [synthesisRes, sCurveRes, convergenceRes, trlRes] = await Promise.all([
          fetch(`http://127.0.0.1:5000/api/analytics/synthesis/${encodeURIComponent(topic)}`),
          fetch(`http://127.0.0.1:5000/api/analytics/scurve/${encodeURIComponent(topic)}`),
          fetch(`http://127.0.0.1:5000/api/analytics/convergence/${encodeURIComponent(topic)}`),
          fetch(`http://127.0.0.1:5000/api/analytics/trl_progression/${encodeURIComponent(topic)}`),
        ]);

        if (synthesisRes.ok) setSynthesis(await synthesisRes.json());
        if (sCurveRes.ok) {
            const data = await sCurveRes.json();
            setSCurveData({
                labels: data.map(d => d.year),
                datasets: [{
                    label: 'Cumulative Publications (S-Curve)',
                    data: data.map(d => d.cumulative_count),
                    borderColor: '#4a9eff',
                    backgroundColor: 'rgba(74, 158, 255, 0.2)',
                    fill: true,
                }]
            });
        }
        if (convergenceRes.ok) setConvergenceData(await convergenceRes.json());
        if (trlRes.ok) {
            const data = await trlRes.json();
            const allData = [...data.history, ...data.forecast];
            setTrlData({
                labels: allData.map(d => d.year),
                datasets: [{
                    label: 'Average TRL (History + Forecast)',
                    data: allData.map(d => d.avg_trl),
                    borderColor: '#198754',
                    backgroundColor: 'rgba(25, 135, 84, 0.2)',
                    // Dashed line for forecast part
                    borderDash: [5, 5],
                }]
            });
        }
      } catch (error) {
        console.error("Failed to fetch analytics data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [topic]);
  
  if (!topic || loading) {
    return null; // Don't show anything if no topic or still loading
  }

  return (
    <div className="analytics-container">
      <h2>Analytics Dashboard for "{topic}"</h2>
      <div className="grid">
        <div className="card">
          <h3>Signal Analysis</h3>
          {synthesis && !synthesis.error ? (
            <div>
              <p><strong>Summary:</strong> {synthesis.overall_summary}</p>
              <h5>Emerging Signals:</h5>
              <ul>{synthesis.emerging_signals?.map((signal, i) => <li key={i}>{signal}</li>)}</ul>
              <h5>Key Players:</h5>
              <ul>{synthesis.key_players?.map((player, i) => <li key={i}>{player}</li>)}</ul>
            </div>
          ) : <p>Not enough data for synthesis.</p>}
        </div>
        <div className="card">
          <h3>Technology Convergence</h3>
          {convergenceData && convergenceData.length > 0 ? (
            <ul>
              {convergenceData.map((item, i) => (
                <li key={i}>{item.tech_1} &harr; {item.tech_2} (Strength: {item.strength})</li>
              ))}
            </ul>
          ) : <p>Not enough data for convergence analysis.</p>}
        </div>
        <div className="card chart-card">
          <h3>S-Curve (Adoption Rate)</h3>
          <div className="chart-wrapper">
            {sCurveData ? <Line options={chartOptions} data={sCurveData} /> : <p>Loading chart...</p>}
          </div>
        </div>
        <div className="card chart-card">
          <h3>TRL Progression & Forecast</h3>
          <div className="chart-wrapper">
            {trlData ? <Line options={chartOptions} data={trlData} /> : <p>Loading chart...</p>}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;