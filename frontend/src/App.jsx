import React, { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import Navbar from './components/navbar';
import HeroPage from './components/HeroPage';
import FindMatch from './components/FindMatch';
import ResultsPage from './components/ResultsPage';
import './index.css';
import SplashScreen from './components/SplashScreen';

function App() {
  // track if splash screen is showing
  const [showSplash, setShowSplash] = useState(true);

  // Show splash screen first
  if (showSplash) {
    return (
      <div className="min-h-screen bg-gray-50 text-gray-900">
        <AnimatePresence mode='wait'>
          <SplashScreen key="splash" onComplete={() => setShowSplash(false)} />
        </AnimatePresence>
      </div>
    );
  }

  // Once splash is done, show router-enabled app
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50 text-gray-900">
        <Navbar />
        <Routes>
          <Route path="/" element={<HeroPage />} />
          <Route path="/find-match" element={<FindMatch />} />
          <Route path="/results" element={<ResultsPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;