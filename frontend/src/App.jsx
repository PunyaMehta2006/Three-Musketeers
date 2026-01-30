import React, { useState } from 'react';
import { AnimatePresence } from 'framer-motion';
import Navbar from './components/navbar';
import HeroPage from './components/HeroPage';
import './index.css';
import SplashScreen from './components/SplashScreen';

function App() {
  
  // track if splash screen is showing
  const [showSplash, setShowSplash] = useState(true);

  // what to show on screen
  let content;
  if (showSplash) {
    content = <SplashScreen key="splash" onComplete={() => setShowSplash(false)} />;
  } else {
    content = (
      <div key="main-content">
        <Navbar />
        <HeroPage />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <AnimatePresence mode='wait'>
        {content}
      </AnimatePresence>
    </div>
  );
}

export default App;