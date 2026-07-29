const express = require('express');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

app.post('/analyze', (req, res) => {
  const { code } = req.body;

  if (!code) {
    return res.status(400).json({ error: 'No code provided' });
  }

  const mockAnalysisResult = {
    severityData: [
      { severity: 'High', count: 2 },
      { severity: 'Medium', count: 3 },
      { severity: 'Low', count: 5 }
    ],
    issues: [
      { type: 'Security', message: 'Potential SQL Injection vulnerability detected.', line: 12 },
      { type: 'Performance', message: 'Unused variable declaration.', line: 5 },
      { type: 'Style', message: 'Missing semicolon at the end of statement.', line: 18 }
    ]
  };

  res.json(mockAnalysisResult);
});

app.post('/download-pdf', (req, res) => {
  const { results } = req.body;

  if (!results) {
    return res.status(400).json({ error: 'No analysis results provided for PDF' });
  }

  const dummyPdfContent = `Code Analysis Report\n\nIssues Found: ${results.issues.length}\nGenerated successfully.`;
  
  res.setHeader('Content-Type', 'application/pdf');
  res.setHeader('Content-Disposition', 'attachment; filename=code-analysis-report.pdf');
  res.send(Buffer.from(dummyPdfContent));
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});