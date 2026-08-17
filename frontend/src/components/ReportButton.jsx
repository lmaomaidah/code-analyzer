import React, { useState } from 'react';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';

export default function ReportButton() {
  const [loading, setLoading] = useState(false);

  const handleDownloadPDF = async () => {
    setLoading(true);
    try {
      const dashboardElement = document.getElementById('dashboard-report-content');
      if (!dashboardElement) {
        alert('Dashboard content not found!');
        setLoading(false);
        return;
      }

      const canvas = await html2canvas(dashboardElement, { scale: 2, useCORS: true });
      const imgData = canvas.toDataURL('image/png');
      
      const pdf = new jsPDF('p', 'mm', 'a4');
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = (canvas.height * pdfWidth) / canvas.width;

      pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
      pdf.save('quality-report.pdf');
    } catch (error) {
      console.error('Error generating PDF:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleDownloadPDF}
      disabled={loading}
      style={{
        background: '#0F9E83',
        color: '#fff',
        border: 'none',
        borderRadius: '8px',
        padding: '10px 20px',
        fontFamily: 'JetBrains Mono, monospace',
        fontSize: '12px',
        fontWeight: '600',
        cursor: 'pointer',
      }}
    >
      {loading ? 'Generating PDF...' : 'Download PDF Report'}
    </button>
  );
}