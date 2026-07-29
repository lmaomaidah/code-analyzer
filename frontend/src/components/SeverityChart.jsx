import React from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

export default function SeverityChart({ summary }) {
  const pylint = summary?.pylint || { high: 0, medium: 0, low: 0 };
  const bandit = summary?.bandit || { high: 0, medium: 0, low: 0 };

  const data = {
    labels: ['Pylint', 'Bandit'],
    datasets: [
      { label: 'High', data: [pylint.high || 0, bandit.high || 0], backgroundColor: '#E05C7A' },
      { label: 'Medium', data: [pylint.medium || 0, bandit.medium || 0], backgroundColor: '#E8A230' },
      { label: 'Low', data: [pylint.low || 0, bandit.low || 0], backgroundColor: '#4D9EE8' },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'top', labels: { color: '#D8E8F0' } },
      title: { display: true, text: 'Issues by Severity', color: '#fff', font: { size: 16 } },
    },
    scales: {
      x: { grid: { color: '#1E3A54' }, ticks: { color: '#6A8FA8' } },
      y: { grid: { color: '#1E3A54' }, ticks: { color: '#6A8FA8', stepSize: 1 } },
    },
  };

  return (
    <div style={{ background: '#112338', border: '1px solid #1E3A54', borderRadius: '12px', padding: '20px', height: '300px', marginTop: '20px' }}>
      <Bar data={data} options={options} />
    </div>
  );
}
