import React from 'react';
import SeverityChart from './SeverityChart';
import ReportButton from './ReportButton';

export default function Dashboard() {
  return (
    <div style={{ padding: '20px', fontFamily: 'JetBrains Mono, monospace', background: '#0d1117', color: '#c9d1d9', minHeight: '100vh' }}>
      <div id="dashboard-report-content" style={{ background: '#161b22', padding: '24px', borderRadius: '12px', border: '1px solid #30363d' }}>
        <h1 style={{ fontSize: '20px', marginBottom: '16px', color: '#58a6ff' }}>Code Quality Dashboard</h1>
        <p style={{ fontSize: '13px', color: '#8b949e', marginBottom: '24px' }}>
          Overview of code analysis metrics, security vulnerabilities, and issue severity breakdowns.
        </p>
        
        <div style={{ marginBottom: '24px' }}>
          <SeverityChart />
        </div>
      </div>

      <ReportButton />
    </div>
  );
}
