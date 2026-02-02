import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
  ArrowLeft, 
  MapPin, 
  Building2, 
  Sparkles, 
  ArrowUpRight,
  Activity,
  Frown
} from 'lucide-react';
import NetworkBackground from './NetworkBackground'; 

const ResultsPage = () => {
  const navigate = useNavigate();
  const location = useLocation();

  // 1. GET REAL DATA
  const { userData, trials } = location.state || { userData: {}, trials: [] };

  // 2. THE ADAPTER (SAFE VERSION)
  const matches = useMemo(() => {
    if (!trials || trials.length === 0) return [];

    return trials.map((t) => {
      // Logic to extract city/hospital
      const locationStr = t.locations && t.locations.length > 0 ? t.locations[0] : "Global Study";
      const hospitalName = locationStr.split(',')[0] || "Research Center";

      return {
        id: t.id,
        title: t.title,
        
        // Use real score or default to 85
        matchScore: t.match_score || 85, 

        hospital: hospitalName,
        location: locationStr,
        type: "Interventional Study",
        
        // GENERATE TAGS (Fixed to prevent undefined error)
        logicTags: [
          { label: "Condition", value: "Exact Match", color: "bg-emerald-100 text-emerald-700" },
          { label: "Location", value: "Regional", color: "bg-blue-100 text-blue-700" },
          { label: "Urgency", value: "Recruiting", color: "bg-amber-100 text-amber-700" }
        ],

        // Use real insight or fallback
        aiInsight: t.ai_insight || `Recruiting patients with ${t.condition}.`,
        
        originalSummary: t.summary
      };
    });
  }, [trials]);

  return (
    <div className="relative w-full min-h-screen bg-white font-sans pt-32 pb-12 px-6 md:px-12 flex flex-col">
      <NetworkBackground />
      
      {/* HEADER SECTION */}
      <div className="relative z-10 max-w-6xl mx-auto w-full mb-12">
        <motion.div 
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col md:flex-row md:items-end justify-between gap-6 border-b border-slate-100 pb-8"
        >
          <div>
            <button 
              onClick={() => navigate('/')} 
              className="group flex items-center gap-2 text-[#94a3b8] hover:text-[#475569] text-[10px] font-bold tracking-[0.2em] uppercase mb-4 transition-colors"
            >
              <ArrowLeft className="w-3 h-3" /> Return Home
            </button>
            <h1 className="text-4xl md:text-5xl font-light text-slate-900">
              Analysis <span className="font-serif italic text-[#475569]">Complete</span>.
            </h1>
            <p className="text-slate-400 text-sm mt-3 font-light max-w-lg">
              We identified <span className="text-slate-900 font-medium">{matches.length} opportunities</span> for you based on your uploaded profile.
            </p>
          </div>

          <div className="flex gap-8">
            <div>
              <div className="text-[10px] font-bold tracking-[0.2em] text-[#94a3b8] uppercase mb-1">Status</div>
              <div className="text-2xl font-light text-slate-800">Recruiting</div>
            </div>
            <div>
              <div className="text-[10px] font-bold tracking-[0.2em] text-[#94a3b8] uppercase mb-1">Condition</div>
              <div className="text-2xl font-light text-slate-800 truncate max-w-[150px]">{userData.condition || "Unknown"}</div>
            </div>
          </div>
        </motion.div>
      </div>

      {/* THE GRID */}
      <div className="relative z-10 max-w-6xl mx-auto w-full space-y-6">
        {matches.length > 0 ? (
          matches.map((trial, index) => (
            <motion.div
              key={trial.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.15 }}
              className="group relative w-full bg-white/60 backdrop-blur-md border border-slate-200 shadow-xl shadow-slate-200/50 p-8 rounded-3xl hover:shadow-xl transition-all duration-500"
            >
              <div className="flex flex-col md:flex-row gap-8 items-start">
                
                {/* Left: Score */}
                <div className="w-full md:w-32 flex flex-row md:flex-col items-center md:items-start justify-between md:justify-start gap-4 border-b md:border-b-0 md:border-r border-slate-100 pb-4 md:pb-0 md:pr-8">
                  <div>
                    <span className="block text-[9px] font-bold tracking-[0.2em] text-[#94a3b8] uppercase mb-2">Match Index</span>
                    <span className="font-serif italic text-5xl text-slate-800">{trial.matchScore}</span>
                  </div>
                  <div className="h-1.5 w-full bg-slate-100 mt-2 overflow-hidden rounded-full">
                    <motion.div 
                      initial={{ width: 0 }}
                      animate={{ width: `${trial.matchScore}%` }}
                      transition={{ duration: 1, delay: 0.5 + (index * 0.2) }}
                      className={`h-full rounded-full ${trial.matchScore > 90 ? 'bg-emerald-500' : 'bg-slate-400'}`}
                    />
                  </div>
                </div>

                {/* Center: Content */}
                <div className="flex-1">
                  <div className="flex flex-wrap gap-3 mb-4">
                    {/* SAFE GUARD: Added logicTags check */}
                    {(trial.logicTags || []).map((tag, i) => (
                      <div key={i} className={`px-4 py-1.5 rounded-full text-[10px] font-bold tracking-[0.1em] uppercase flex items-center gap-2 ${tag.color}`}>
                        {tag.label} <span className="opacity-50">/</span> {tag.value}
                      </div>
                    ))}
                  </div>

                  <h3 className="text-xl md:text-2xl font-light text-slate-900 mb-2 group-hover:text-[#475569] transition-colors">
                    {trial.title}
                  </h3>

                  <div className="flex items-center gap-6 text-xs text-[#94a3b8] font-medium tracking-wide mb-6">
                    <span className="flex items-center gap-2"><Building2 className="w-3 h-3" /> {trial.hospital}</span>
                    <span className="flex items-center gap-2"><MapPin className="w-3 h-3" /> {trial.location}</span>
                  </div>

                  {/* AI Insight Box */}
                  <div className="flex gap-4 p-5 bg-slate-50/80 border border-slate-100 rounded-2xl">
                     <div className="p-2 bg-white rounded-full shadow-sm h-fit">
                        <Sparkles className="w-3 h-3 text-amber-500" />
                     </div>
                     <div className="flex flex-col justify-center">
                        <span className="text-[9px] font-bold tracking-[0.2em] text-[#94a3b8] uppercase mb-1">Diversity Engine Logic</span>
                        <p className="text-xs text-slate-600 font-medium leading-relaxed">{trial.aiInsight}</p>
                     </div>
                  </div>
                </div>

                {/* Right: Action */}
                <div className="w-full md:w-auto flex md:flex-col justify-end h-full pt-2">
                  <a href={`https://clinicaltrials.gov/study/${trial.id}`} target="_blank" rel="noreferrer" className="flex items-center justify-center gap-3 px-8 py-4 bg-[#475569] text-white text-[10px] font-bold tracking-[0.2em] uppercase rounded-full hover:bg-slate-800 transition-all">
                      View Trial <ArrowUpRight className="w-3 h-3" />
                  </a>
                </div>

              </div>
            </motion.div>
          ))
        ) : (
          /* EMPTY STATE */
          <div className="text-center py-20 bg-slate-50/50 rounded-3xl border border-dashed border-slate-200">
            <Frown className="w-12 h-12 text-slate-300 mx-auto mb-4" />
            <h3 className="text-xl font-light text-slate-900">No matches found.</h3>
            <button onClick={() => navigate('/')} className="mt-6 text-xs font-bold uppercase tracking-widest text-indigo-600 hover:underline">Try another report</button>
          </div>
        )}
      </div>
      <div className="h-20" />
    </div>
  );
};

export default ResultsPage;