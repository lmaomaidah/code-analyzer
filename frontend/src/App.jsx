import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import InputPage from './pages/InputPage';
import Dashboard from './pages/Dashboard';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<InputPage />} />
        <Route path="/results" element={<Dashboard />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;