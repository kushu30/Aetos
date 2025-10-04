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
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!topic) return;

    const fetchAnalytics = async () => {
      setLoading(true);
      try {
        const response = await fetch(`http://127.0.0.1:5000/api/analytics/synthesis/${encodeURIComponent(topic)}`);
        if (response.ok) {
          const data = await response.json();
          setAnalyticsData(data);
        }
      } catch (error) {
        console.error("Failed to fetch analytics data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [topic]);

  if (!topic || loading || !analyticsData) {
    return null;
  }

  // --- Process data for charts ---
  const sCurveChartData = {
    labels: analyticsData.mock_s_curve?.map(d => d.year) || [],
    datasets: [{
      label: 'Cumulative Publications (S-Curve)',
      data: analyticsData.mock_s_curve?.map(d => d.cumulative_count) || [],
      borderColor: '#4a9eff',
      backgroundColor: 'rgba(74, 158, 255, 0.2)',
      fill: true,
      tension: 0.4
    }]
  };

  const trlProgressionData = {
    labels: [
      ...(analyticsData.mock_trl_progression?.history.map(d => d.year) || []),
      ...(analyticsData.mock_trl_progression?.forecast.map(d => d.year) || [])
    ],
    datasets: [
      {
        label: 'Historical Avg. TRL',
        data: analyticsData.mock_trl_progression?.history.map(d => d.avg_trl) || [],
        borderColor: '#198754',
        fill: false,
        tension: 0.1
      },
      {
        label: 'Forecasted Avg. TRL',
        data: [
          // Add nulls to create a gap for the historical data
          ...(analyticsData.mock_trl_progression?.history.map(() => null) || []),
          ...(analyticsData.mock_trl_progression?.forecast.map(d => d.avg_trl) || [])
        ],
        borderColor: '#ffc107',
        borderDash: [5, 5],
        fill: false,
        tension: 0.1
      }
    ]
  };

  return (
    <div className="analytics-container">
      <h2>Analytics Dashboard for "{topic}"</h2>
      <div className="grid">
        <div className="card">
          <h3>Signal Analysis</h3>
          {analyticsData && !analyticsData.error ? (
            <div>
              <p><strong>Summary:</strong> {analyticsData.overall_summary}</p>
              <h5>Emerging Signals:</h5>
              <ul>{analyticsData.emerging_signals?.map((signal, i) => <li key={i}>{signal}</li>)}</ul>
              <h5>Key Players:</h5>
              <ul>{analyticsData.key_players?.map((player, i) => <li key={i}>{player}</li>)}</ul>
            </div>
          ) : <p>Not enough data for synthesis.</p>}
        </div>
        <div className="card">
          <h3>Technology Convergence</h3>
          {analyticsData.convergence && analyticsData.convergence.length > 0 ? (
            <ul>
              {analyticsData.convergence.map((item, i) => (
                <li key={i}>{item.tech_1} &harr; {item.tech_2} (Strength: {item.strength})</li>
              ))}
            </ul>
          ) : <p>Not enough data for convergence analysis.</p>}
        </div>
        <div className="card chart-card">
          <h3>S-Curve (Adoption Rate)</h3>
          <div className="chart-wrapper">
            {analyticsData.mock_s_curve ? <Line options={chartOptions} data={sCurveChartData} /> : <p>No S-Curve data generated.</p>}
          </div>
        </div>
        <div className="card chart-card">
          <h3>TRL Progression & Forecast</h3>
          <div className="chart-wrapper">
            {analyticsData.mock_trl_progression ? <Line options={chartOptions} data={trlProgressionData} /> : <p>No TRL data generated.</p>}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;