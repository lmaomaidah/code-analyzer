import React from 'react';
import { useNavigate } from 'react-router-dom';

function InputPage({ inputCode, setInputCode, loading, handleSubmit }) {
  const navigate = useNavigate();

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h1>Code Analyzer</h1>
      
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '15px' }}>
          <label style={{ display: 'block', marginBottom: '8px' }}>
            Paste your code below:
          </label>
          <textarea
            value={inputCode}
            onChange={(e) => setInputCode(e.target.value)}
            rows={12}
            style={{ width: '100%', fontFamily: 'monospace', padding: '10px' }}
            placeholder="Paste source code here..."
            required
          />
        </div>

        <button 
          type="submit" 
          disabled={loading}
          style={{ padding: '10px 20px', fontSize: '16px', cursor: 'pointer' }}
        >
          {loading ? 'Analyzing...' : 'Analyze Code'}
        </button>
      </form>
    </div>
  );
}

export default InputPage;