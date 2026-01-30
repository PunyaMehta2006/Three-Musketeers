import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import logoVideo from '../assets/logo-animation.mp4';

const SplashScreen = ({ onComplete }) => {
  const [showText, setShowText] = useState(false);

  // check if video is near the end to show text
  function handleTimeUpdate(e) {
    const video = e.target;
    if (video.duration > 0 && video.duration - video.currentTime <= 4.0) {
      setShowText(true);
    }
  }

  return (
    <motion.div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        zIndex: 9999,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: 'white'
      }}
      initial={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 1.2, ease: "easeInOut" }}>
      
      <video
        autoPlay
        muted
        playsInline
        onEnded={onComplete}
        onTimeUpdate={handleTimeUpdate}
        style={{
          maxWidth: '800px',
          width: '90%',
          WebkitMaskImage: 'radial-gradient(circle, black 20%, transparent 100%)',
          maskImage: 'radial-gradient(circle, black 20%, transparent 100%)',
          transform: 'translateX(10px)'
        }}>
        <source src={logoVideo} type="video/mp4" />
      </video>

      <AnimatePresence>
        {showText && (
          <motion.div
            style={{
              position: 'absolute',
              bottom: '15%', 
              textAlign: 'center',
              fontFamily: '"Inter", "system-ui", sans-serif'
            }}
            initial={{ opacity: 0, filter: 'blur(12px)', y: 12 }}
            animate={{ opacity: 1, filter: 'blur(0px)', y: 0 }}
            transition={{ 
              duration: 2.0, 
              ease: [0.22, 1, 0.36, 1] 
            }}>
            
            <h1 
              className="text-4xl font-extralight tracking-[0.4em] uppercase"
              style={{ color: '#475569' }}> 
              Diversity Match
            </h1>

            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.2, duration: 1.2 }}
              className="text-[15px] mt-4 tracking-[0.6em] font-medium uppercase"
              style={{ color: '#94a3b8' }}>
              Equal Access to Innovation
            </motion.p>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default SplashScreen;