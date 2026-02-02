import React from 'react';
import { motion } from 'framer-motion';
import logoImage from '../assets/logo.png'; 
import { Link } from 'react-router-dom'; // 👈 Import Link

const Navbar = () => {
  return (
    <motion.nav
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 1.2, ease: [0.22, 1, 0.36, 1] }}
      className="fixed top-0 left-0 w-full z-50 bg-white/80 backdrop-blur-md border-b border-slate-100"
    >
      
      <div className="w-full px-8 md:px-12 h-24 flex items-center justify-between">
        
        {/* logo and text - NOW CLICKABLE TO HOME */}
        <Link to="/" className="flex items-center gap-4 hover:opacity-80 transition-opacity">
          <img 
            src={logoImage} 
            alt="Diversity Match Logo" 
            className="w-18 h-18 object-contain -translate-y-1" 
          />
          
          <div className="flex flex-col justify-center">
            <span className="text-[#475569] text-lg font-light tracking-[0.3em] uppercase leading-none">
              Diversity Match
            </span>
            <span className="text-[#94a3b8] text-[9px] font-bold tracking-[0.4em] uppercase mt-2">
              Equal Access to Innovation
            </span>
          </div>
        </Link>

        {/* navigation links */}
        <div className="flex items-center gap-10">
          <div className="hidden md:flex gap-8">
            
            {/* 1. HOME - Uses Link to go to "/" */}
            <Link 
              to="/"
              className="text-[#94a3b8] hover:text-[#475569] text-[11px] font-medium tracking-[0.2em] transition-colors duration-300"
            >
              Home
            </Link>

            {/* 2. FIND MATCH - Already correct */}
            <Link 
              to="/find-match"
              className="text-[#94a3b8] hover:text-[#475569] text-[11px] font-medium tracking-[0.2em] transition-colors duration-300"
            >
              Find Match
            </Link>
            
            
            {/* 4. RESULTS - Updated for the final page */}
            <Link 
              to="/results"
              className="text-[#94a3b8] hover:text-[#475569] text-[11px] font-medium tracking-[0.2em] transition-colors duration-300"
            >
              Results
            </Link>
          </div>

          <button className="px-6 py-2.5 bg-[#475569] text-white text-[10px] font-bold tracking-[0.2em] rounded-full hover:bg-slate-800 transition-all shadow-md shadow-slate-200/50">
            Language
          </button>
        </div>
      </div>
    </motion.nav>
  );
};

export default Navbar;