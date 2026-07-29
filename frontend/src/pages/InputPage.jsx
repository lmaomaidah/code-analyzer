import React, { useState } from 'react';
import LoadingSpinner from '../components/LoadingSpinner';

export default function InputPage() {
  const [activeTab, setActiveTab] = useState('code'); // 'code' ya 'github'
  const [codeContent, setCodeContent] = useState('');
  const [githubUrl, setGithubUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const MAX_CHARS = 5000;

  // Validation aur Submit handler
  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');

    if (activeTab === 'code') {
      if (!codeContent.trim()) {
        setError('Please enter some Python code to analyze.');
        return;
      }
      if (codeContent.length > MAX_CHARS) {
        setError(`Code exceeds the maximum limit of ${MAX_CHARS} characters.`);
        return;
      }
    } else {
      if (!githubUrl.trim()) {
        setError('Please enter a GitHub repository URL.');
        return;
      }
      if (!githubUrl.includes('github.com')) {
        setError('Please enter a valid GitHub URL.');
        return;
      }
    }

    setLoading(true);
    // Yahan analysis request ya API call aayegi
    setTimeout(() => {
      setLoading(false);
      alert('Analysis completed successfully!');
    }, 2000);
  };

  return (
    <div style={{ maxWidth: '800px', margin: '40px auto', padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h2>Python Code Quality Analyzer</h2>
      <p>Select input method to run static analysis (Pylint, Radon, Bandit).</p>

      {/* Tabs Switcher */}
      <div style={{ display: 'flex', marginBottom: '20px', borderBottom: '2px solid #ccc' }}>
        <button
          onClick={() => { setActiveTab('code'); setError(''); }}
          style={{
            padding: '10px 20px',
            background: activeTab === 'code' ? '#14C9A8' : 'transparent',
            border: 'none',
            cursor: 'pointer',
            fontWeight: 'bold',
            color: activeTab === 'code' ? '#fff' : '#333'
          }}
        >
          Paste Code
        </button>
        <button
          onClick={() => { setActiveTab('github'); setError(''); }}
          style={{
            padding: '10px 20px',
            background: activeTab === 'github' ? '#14C9A8' : 'transparent',
            border: 'none',
            cursor: 'pointer',
            fontWeight: 'bold',
            color: activeTab === 'github' ? '#fff' : '#333'
          }}
        >
          GitHub Repository
        </button>
      </div>

      {/* Error Message */}
      {error && <div style={{ color: 'red', marginBottom: '15px' }}>{error}</div>}

      <form onSubmit={handleSubmit}>
        {activeTab === 'code' ? (
          <div>
            <textarea
              rows="12"
              value={codeContent}
              onChange={(e) => setCodeContent(e.target.value)}
              placeholder="Paste your Python code here..."
              style={{ width: '100%', padding: '10px', fontFamily: 'monospace', fontSize: '14px' }}
            />
            <div style={{ textAlign: 'right', fontSize: '12px', color: codeContent.length > MAX_CHARS ? 'red' : '#666' }}>
              {codeContent.length} / {MAX_CHARS} characters
            </div>
          </div>
        ) : (
          <div>
            <input
              type="text"
              value={githubUrl}
              onChange={(e) => setGithubUrl(e.target.value)}
              placeholder="https://github.com/username/repository"
              style={{ width: '100%', padding: '10px', fontSize: '14px' }}
            />
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '10px',
            marginTop: '20px',
            padding: '10px 20px',
            backgroundColor: '#1E3A54',
            color: '#fff',
            border: 'none',
            cursor: 'pointer',
            fontSize: '16px'
          }}
        >
          {loading && <LoadingSpinner />}
          {loading ? 'Analyzing...' : 'Analyze Code'}
        </button>
      </form>
    </div>
  );
}