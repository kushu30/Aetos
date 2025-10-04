import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
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
  Title,
  Tooltip,
  Legend,
  Filler
);

// --- MOCK DATA FOR S-CURVE ---
const mockSCurveData = {
  labels: ['2018', '2019', '2020', '2021', '2022', '2023', '2024'],
  datasets: [{
    label: 'Cumulative Publications (S-Curve)',
    data: [5, 12, 25, 45, 70, 90, 105],
    borderColor: '#4a9eff',
    backgroundColor: 'rgba(74, 158, 255, 0.2)',
    fill: true,
    tension: 0.4
  }]
};

// --- MOCK DATA FOR TRL PROGRESSION & FORECAST ---
const mockTrlProgressionData = {
  labels: ['2020', '2021', '2022', '2023', '2024', '2025', '2026', '2027'],
  datasets: [
    {
      label: 'Historical Avg. TRL',
      data: [2.5, 3.1, 3.5, 4.2, 4.8, null, null, null], // Historical data ends at the last known point
      borderColor: '#198754',
      backgroundColor: 'rgba(25, 135, 84, 0.2)',
      fill: false,
      tension: 0.1
    },
    {
      label: 'Forecasted Avg. TRL',
      data: [null, null, null, null, 4.8, 5.3, 5.8, 6.2], // Forecast data starts where history ends
      borderColor: '#ffc107',
      backgroundColor: 'rgba(255, 193, 7, 0.2)',
      borderDash: [5, 5], // Dashed line for forecast
      fill: false,
      tension: 0.1
    }
  ]
};


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
  const [convergenceData, setConvergenceData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!topic) return;

    const fetchAnalytics = async () => {
      setLoading(true);
      try {
        // Fetch only synthesis and convergence data
        const [synthesisRes, convergenceRes] = await Promise.all([
          fetch(`http://127.0.0.1:5000/api/analytics/synthesis/${encodeURIComponent(topic)}`),
          fetch(`http://127.0.0.1:5000/api/analytics/convergence/${encodeURIComponent(topic)}`),
        ]);

        if (synthesisRes.ok) setSynthesis(await synthesisRes.json());
        if (convergenceRes.ok) setConvergenceData(await convergenceRes.json());

      } catch (error) {
        console.error("Failed to fetch analytics data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [topic]);
  
  if (!topic || loading) {
    return null;
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
            <Line options={chartOptions} data={mockSCurveData} />
          </div>
        </div>
        <div className="card chart-card">
          <h3>TRL Progression & Forecast</h3>
          <div className="chart-wrapper">
            <Line options={chartOptions} data={mockTrlProgressionData} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;