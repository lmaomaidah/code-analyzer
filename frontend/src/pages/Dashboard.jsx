import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { FileText, BarChart3, AlertTriangle } from 'lucide-react';
import SeverityChart from '../components/SeverityChart';
import ReportButton from '../components/ReportButton';

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
      { tool: 'Security', message: 'Potential SQL injection risk detected', line: 14 },
      { tool: 'Performance', message: 'Unused variable declaration', line: 28 },
      { tool: 'Style', message: 'Inconsistent indentation format', line: 42 }
    ],
    codeSnippet: 'No code submitted yet.'
  };

  const codeLines = analysisResult.codeSnippet.split('\n');

  const issuesByLine = {};
  (analysisResult.issues || []).forEach((issue) => {
    if (!issuesByLine[issue.line]) issuesByLine[issue.line] = [];
    issuesByLine[issue.line].push(issue);
  });

  return (
    <div id="dashboard-report-content" className="dashboard">
      <div className="dashboard-header">
        <div>
          <h1>Code Analyzer Dashboard</h1>
          <p>Static code analysis for security, performance, and style issues</p>
        </div>
        <div className="dashboard-header-actions">
          <ReportButton />
          <button className="back-button" onClick={() => navigate('/')}>
            ← Back to Input
          </button>
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="dashboard-panel">
          <h3><FileText size={18} style={{ verticalAlign: 'middle', marginRight: '8px' }} />Code Snippet Viewer</h3>
          <pre className="code-snippet">
            {codeLines.map((line, index) => {
              const lineNumber = index + 1;
              const lineIssues = issuesByLine[lineNumber];
              const hasIssue = !!lineIssues;
              return (
                <div
                  key={index}
                  className={hasIssue ? 'code-line code-line-issue' : 'code-line'}
                  title={hasIssue ? lineIssues.map((i) => i.message).join(' | ') : undefined}
                >
                  <span className="code-line-number">{lineNumber}</span>
                  {hasIssue && <AlertTriangle size={12} className="code-line-warning-icon" />}
                  <span className="code-line-text">{line || ' '}</span>
                </div>
              );
            })}
          </pre>
          <div className="code-snippet-note">
            <AlertTriangle size={14} style={{ verticalAlign: 'middle', marginRight: '6px' }} />
            <span>Warning icons highlighted on detected lines</span>
          </div>
        </div>

        <div className="dashboard-panel analytics-panel">
          <h3><BarChart3 size={18} style={{ verticalAlign: 'middle', marginRight: '8px' }} />Analytics & Severity Distribution</h3>
          <div>
            <SeverityChart data={analysisResult.severityData || []} />
          </div>
          <div>
            <h4 className="issues-list-title">Collapsible Issues List</h4>
            <ul className="issues-list">
              {analysisResult.issues?.map((issue, index) => (
                <li key={index} className="issue-item">
                  <strong className="issue-type">{issue.tool || issue.type} (Line {issue.line}):</strong> {issue.message}
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