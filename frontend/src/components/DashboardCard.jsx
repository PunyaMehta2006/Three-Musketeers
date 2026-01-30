import React from 'react';
import { motion } from 'framer-motion';

const DashboardCard = ({ title, subtitle, icon, children, className = "", delay = 0 }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.6, delay }}
      className={`
        relative overflow-hidden rounded-2xl 
        bg-white/60 backdrop-blur-sm 
        border border-white 
        shadow-lg shadow-slate-200/50 
        p-6 
        hover:shadow-xl hover:shadow-slate-300/30 
        transition-all duration-300
        ${className}
      `}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-bold text-slate-900 uppercase tracking-widest">{title}</h3>
          <p className="text-[10px] text-slate-400 uppercase tracking-wider mt-0.5">{subtitle}</p>
        </div>
        <div className="p-2 rounded-lg bg-slate-50/80 border border-slate-100">
          {icon}
        </div>
      </div>

      {/* Content */}
      <div className="relative z-10">
        {children}
      </div>
    </motion.div>
  );
};

export default DashboardCard;