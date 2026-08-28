import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const API_BASE = import.meta.env.VITE_API_BASE || '/api';

function InputPage() {
  const [inputCode, setInputCode] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: inputCode }),
      });
      const data = await response.json();

      if (!response.ok) {
        alert(data.error || 'Analysis failed. Please check your code and try again.');
        return;
      }

      const severityCounts = { High: 0, Medium: 0, Low: 0 };
      (data.issues || []).forEach((issue) => {
        const sev = (issue.severity || 'LOW').toUpperCase();
        if (sev === 'HIGH') severityCounts.High++;
        else if (sev === 'MEDIUM') severityCounts.Medium++;
        else severityCounts.Low++;
      });
      const severityData = [
        { name: 'High', count: severityCounts.High },
        { name: 'Medium', count: severityCounts.Medium },
        { name: 'Low', count: severityCounts.Low },
      ];

      navigate('/results', {
        state: { analysisResult: { ...data, severityData, codeSnippet: inputCode } },
      });
    } catch (err) {
      console.error(err);
      alert('Something went wrong while connecting to the server. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="input-page">
      <h1>Code Analyzer</h1>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '15px' }}>
          <label>Paste your code below:</label>
          <textarea
            value={inputCode}
            onChange={(e) => setInputCode(e.target.value)}
            rows={12}
            placeholder="Paste source code here..."
            required
          />
        </div>
        <button type="submit" disabled={loading}>
          {loading ? 'Analyzing...' : 'Analyze Code'}
        </button>
      </form>
    </div>
  );
}

export default InputPage;