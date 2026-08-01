import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import SeverityChart from '../components/SeverityChart';

function Dashboard() {
  const location = useLocation();
  const navigate = useNavigate();
  const analysisResult = location.state?.analysisResult || {
    severityData: [
      { name: 'High', count: 2 },
      { name: 'Medium', count: 5 },
      { name: 'Low', count: 3 }
    ],
    issues: [
      { type: 'Security', message: 'Potential SQL injection risk detected', line: 14 },
      { type: 'Performance', message: 'Unused variable declaration', line: 28 },
      { type: 'Style', message: 'Inconsistent indentation format', line: 42 }
    ],
    codeSnippet: `// Sample Code Snippet Preview\nfunction authenticateUser(req, res) {\n  const query = "SELECT * FROM users WHERE user = '" + req.body.user + "';";\n  db.query(query, (err, results) => {\n    if (err) throw err;\n    res.send(results);\n  });\n}`
  };

  const handleDownloadPDF = async () => {
    try {
      const response = await fetch('http://localhost:5000/download-pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ results: analysisResult }),
      });
      if (!response.ok) throw new Error('PDF generation failed');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'code-analysis-report.pdf';
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download error:', error);
      alert('Failed to download PDF report.');
    }
  };

  return (
    <div style={{ padding: '30px', backgroundColor: '#0f172a', minHeight: '100vh', color: '#f8fafc', fontFamily: 'Arial, sans-serif' }}>
      {/* Header Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px', borderBottom: '1px solid #334155', paddingBottom: '15px' }}>
        <div>
          <h1 style={{ margin: 0, fontSize: '24px', color: '#38bdf8' }}>Code Analyzer Dashboard</h1>
          <p style={{ margin: '5px 0 0 0', color: '#94a3b8', fontSize: '14px' }}>Prototype View: Dual-Pane Code & Analytics Workspace</p>
        </div>
        <div>
          <button 
            onClick={handleDownloadPDF} 
            style={{ backgroundColor: '#0284c7', color: '#fff', border: 'none', padding: '10px 18px', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold', marginRight: '10px' }}
          >
            Download PDF Report
          </button>
          <button 
            onClick={() => navigate('/')} 
            style={{ backgroundColor: '#334155', color: '#fff', border: 'none', padding: '10px 18px', borderRadius: '6px', cursor: 'pointer' }}
          >
            ← Back to Input
          </button>
        </div>
      </div>

      {/* Dual-Pane Layout */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '25px' }}>
        
        {/* Left Pane: Code Viewer */}
        <div style={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', padding: '20px', display: 'flex', flexDirection: 'column' }}>
          <h3 style={{ marginTop: 0, color: '#e2e8f0', borderBottom: '1px solid #334155', paddingBottom: '10px' }}>📄 Code Snippet Viewer</h3>
          <pre style={{ backgroundColor: '#090d16', padding: '15px', borderRadius: '6px', color: '#34d399', overflowX: 'auto', flex: 1, fontSize: '13px', lineHeight: '1.5' }}>
            {analysisResult.codeSnippet}
          </pre>
          <div style={{ marginTop: '10px', fontSize: '12px', color: '#94a3b8' }}>
            <span>⚠️ Warning Icons Highlighted on Detected Lines</span>
          </div>
        </div>

        {/* Right Pane: Interactive Analytics & Severity */}
        <div style={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <h3 style={{ marginTop: 0, color: '#e2e8f0', borderBottom: '1px solid #334155', paddingBottom: '10px' }}>📊 Analytics & Severity Distribution</h3>
          
          <div>
            <SeverityChart data={analysisResult.severityData || []} />
          </div>

          <div style={{ flex: 1, overflowY: 'auto' }}>
            <h4 style={{ color: '#cbd5e1', marginBottom: '10px' }}>Collapsible Issues List</h4>
            <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
              {analysisResult.issues?.map((issue, index) => (
                <li key={index} style={{ backgroundColor: '#0f172a', borderLeft: '4px solid #f59e0b', padding: '10px 15px', marginBottom: '8px', borderRadius: '4px', fontSize: '13px' }}>
                  <strong style={{ color: '#f59e0b' }}>{issue.type} (Line {issue.line}):</strong> {issue.message}
                </li>
              ))}
            </ul>
          </div>
        </div>

      </div>
    </div>
  );
}

export default Dashboard;