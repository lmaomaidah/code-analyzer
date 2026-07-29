import React from 'react';

function SeverityChart({ data }) {
  const total = data.reduce((acc, curr) => acc + curr.count, 0) || 1;

  const colors = {
    High: '#ef4444',
    Medium: '#f59e0b',
    Low: '#3b82f6'
  };

  return (
    <div style={{ backgroundColor: '#0f172a', padding: '15px', borderRadius: '6px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '13px', color: '#94a3b8' }}>
        <span>Issue Severity Breakdown</span>
        <span>Total Issues: {total}</span>
      </div>

      <div style={{ display: 'flex', height: '12px', borderRadius: '6px', overflow: 'hidden', backgroundColor: '#334155', gap: '2px' }}>
        {data.map((item, index) => {
          const percentage = (item.count / total) * 100;
          return (
            <div 
              key={index}
              style={{ 
                width: `${percentage}%`, 
                backgroundColor: colors[item.name] || '#38bdf8',
                transition: 'width 0.3s ease'
              }}
              title={`${item.name}: ${item.count}`}
            />
          );
        })}
      </div>

      <div style={{ display: 'flex', gap: '15px', marginTop: '10px', fontSize: '12px', color: '#cbd5e1' }}>
        {data.map((item, index) => (
          <div key={index} style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: colors[item.name] || '#38bdf8' }}></span>
            <span>{item.name}: {item.count}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default SeverityChart;