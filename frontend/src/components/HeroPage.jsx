import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import NetworkBackground from './NetworkBackground';
import DashboardCard from './DashboardCard';
import {
  BarChart3,
  ScanLine,
  Radio,
  Zap,
  ShieldCheck,
  Check
} from 'lucide-react';


const HeroPage = () => {
  const navigate = useNavigate();

  // Navigate to find match page
  function goToTrials() {
    navigate('/find-match');
  }

  // scroll to dashboard
  function scrollToDashboard() {
    const section = document.getElementById('dashboard-section');
    if (section) {
      section.scrollIntoView({ behavior: 'smooth' });
    }
  }

  return (
    <div className="relative w-full bg-white font-sans overflow-hidden">
      <NetworkBackground />

      <div className="relative z-10 h-screen w-full flex flex-col items-center justify-center px-6">

        {/* beta tag thing */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="flex items-center gap-2 px-3 py-1 rounded-full bg-white/80 border border-white shadow-sm mb-8">
          <div className="w-2 h-2 bg-indigo-500 rounded-full animate-pulse shadow-[0_0_10px_#6366f1]" />
          <span className="text-xs font-bold tracking-widest text-slate-500">BETA LIVE</span>
        </motion.div>

        {/* main title */}
        <motion.h1
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-5xl md:text-8xl font-light tracking-tight text-slate-900 leading-[1] mb-6 text-center">
          Connecting Diversity <br />
          <span className="font-serif italic text-[#475569]">
            to Discovery.
          </span>
        </motion.h1>

        {/* subtitle text */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="text-lg text-slate-500 font-light max-w-xl mx-auto leading-relaxed mb-10 text-center"
        >
          Ensuring clinical trials represent everyone. Our AI connects patients from all backgrounds: urban, rural and across genders to research opportunities they are eligible for.
        </motion.p>

        {/* buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="flex flex-col md:flex-row gap-4 items-center justify-center"
        >
          <button
            onClick={goToTrials}
            className="px-8 py-4 bg-[#475569] text-white text-xs font-bold tracking-[0.2em] rounded-full hover:bg-slate-800 hover:scale-105 transition-all shadow-xl shadow-slate-300/50">
            FIND MATCH
          </button>
          <button
            onClick={scrollToDashboard}
            className="px-8 py-4 bg-white/80 text-slate-600 border border-white shadow-sm text-xs font-bold tracking-[0.2em] rounded-full hover:bg-white transition-all">
            HOW IT WORKS
          </button>
        </motion.div>

        {/* scroll down arrow */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1, y: [0, 10, 0] }}
          transition={{ delay: 1.5, duration: 2, repeat: Infinity }}
          className="absolute bottom-10 text-slate-400">
          <span className="text-[10px] uppercase tracking-widest block mb-2 text-center">Scroll</span>
          <svg className="w-5 h-5 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path>
          </svg>
        </motion.div>

      </div>


      {/* dashboard section */}
      <div id="dashboard-section" className="relative z-10 w-full min-h-screen py-24 px-6 flex flex-col items-center">

        <div className="max-w-6xl w-full">
          <div className="mb-12 text-center">
            <h2 className="text-3xl text-slate-900 font-light mb-2">The <span className="font-serif italic text-[#475569]">Engine</span>.</h2>
            <p className="text-sm text-slate-500 uppercase tracking-widest">Bridging the Representation Gap</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 md:grid-rows-2 gap-6 h-auto md:h-[500px]">

            {/* card 1 - participation gap*/}
            <DashboardCard
              title="The Participation Gap"
              subtitle="Urban vs Rural"
              icon={<BarChart3 className="w-5 h-5 text-[#475569]" />}
              className="md:col-span-2 md:row-span-1"
              delay={0.1}>
              <div className="flex flex-col justify-center h-full gap-4">
                <div className="w-full">
                  <div className="flex justify-between text-xs font-medium text-slate-600 mb-2">
                    <span>Metropolitan Areas (High Access)</span>
                    <span>85%</span>
                  </div>
                  <div className="w-full h-2 bg-slate-100 rounded-full">
                    <div className="h-full bg-slate-400 w-[85%] rounded-full"></div>
                  </div>
                </div>

                <div className="w-full">
                  <div className="flex justify-between text-xs font-medium text-slate-600 mb-2">
                    <span>Rural / Tier-2 Cities</span>
                    <span className="text-red-500 font-bold">15%</span>
                  </div>
                  <div className="w-full h-2 bg-slate-100 rounded-full">
                    <div className="h-full bg-red-400 w-[15%] rounded-full"></div>
                  </div>
                </div>

                <p className="text-[10px] text-slate-400 mt-1">
                  Most trials are concentrated in major cities, excluding vast populations eligible for treatment.
                </p>
              </div>
            </DashboardCard>

            {/* card 2 - profiler */}
            <DashboardCard
              title="The Profiler"
              subtitle="Data Agent"
              icon={<ScanLine className="w-5 h-5 text-[#475569]" />}
              className="md:col-span-1 md:row-span-1"
              delay={0.2}>
              <div className="space-y-3 mt-2">
                <div className="bg-slate-50/80 border border-slate-100 p-3 rounded text-[10px] font-mono text-slate-500">
                  <div className="mb-1 border-b border-slate-200 pb-1">Input Data:</div>
                  <div className="flex items-center gap-2">
                    <span className="text-slate-700">Medical History</span>
                    <Check className="w-3.5 h-3.5 text-emerald-600" />
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-slate-700">Demographics</span>
                    <Check className="w-3.5 h-3.5 text-emerald-600" />
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-slate-700">Location</span>
                    <Check className="w-3.5 h-3.5 text-emerald-600" />
                  </div>
                </div>
                <div className="text-xs text-slate-700 font-medium text-center leading-tight">
                  Structures raw patient data into a searchable profile.
                </div>
              </div>
            </DashboardCard>

            {/* card 3 - scout */}
            <DashboardCard
              title="The Scout"
              subtitle="Real-Time Scraper"
              icon={<Radio className="w-5 h-5 text-[#45569]" />}
              className="md:col-span-1 md:row-span-2"
              delay={0.3}>
              <div className="flex flex-col h-full justify-between">
                <div>
                  <p className="text-slate-500 text-xs mb-4">Constantly scanning registries for new clinical studies.</p>

                  {/* scan animation box */}
                  <div className="relative w-full h-24 bg-slate-50/80 rounded-xl overflow-hidden border border-slate-100 flex items-center justify-center">
                    <div className="absolute w-[1px] h-full bg-indigo-400/50 left-0 animate-scout-scan"></div>
                    <div className="text-[9px] text-slate-400 font-mono">
                      Scanning Trial: <br />
                      <span className="text-slate-600">NCT048291...</span>
                    </div>
                  </div>

                  <div className="space-y-2 mt-4">
                    <div className="flex items-center gap-2 text-[10px] text-slate-400">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                      <span>Phase 2 • Diabetes</span>
                    </div>
                    <div className="flex items-center gap-2 text-[10px] text-slate-400">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                      <span>Phase 3 • Oncology</span>
                    </div>
                  </div>
                </div>

                <div className="text-center mt-4">
                  <div className="text-2xl font-light text-slate-800">10k+</div>
                  <div className="text-[8px] uppercase tracking-widest text-slate-400">Studies Indexed</div>
                </div>
              </div>
            </DashboardCard>

            {/* card 4 - matching */}
            <DashboardCard
              title="The Bridge"
              subtitle="Matching Agent"
              icon={<Zap className="w-5 h-5 text-[#475569]" />}
              className="md:col-span-1 md:row-span-1"
              delay={0.4}>
              <div className="flex flex-col items-center justify-center h-full gap-2 w-full">
                <div className="w-full bg-slate-50/80 rounded p-2">
                  <div className="flex justify-between items-center text-[10px] mb-1">
                    <span className="text-slate-500">Criterion: Age (18-45)</span>
                    <span className="text-emerald-600 font-bold flex items-center gap-1">
                      <Check className="w-3 h-3" /> Pass
                    </span>
                  </div>
                  <div className="flex justify-between items-center text-[10px] mb-1">
                    <span className="text-slate-500">Criterion: Diagnosis</span>
                    <span className="text-emerald-600 font-bold flex items-center gap-1">
                      <Check className="w-3 h-3" /> Pass
                    </span>
                  </div>
                  <div className="flex justify-between items-center text-[10px]">
                    <span className="text-slate-500">Criterion: Location</span>
                    <span className="text-emerald-600 font-bold flex items-center gap-1">
                      <Check className="w-3 h-3" /> Pass
                    </span>
                  </div>
                </div>

                <div className="w-full mt-2 text-center bg-emerald-50/80 border border-emerald-100 py-2 rounded">
                  <div className="text-[10px] uppercase font-bold text-emerald-700 tracking-widest">
                    Status: Eligible
                  </div>
                </div>
              </div>
            </DashboardCard>

            {/* card 5 - privacy stuff */}
            <DashboardCard
              title="Privacy First"
              subtitle="Anonymized Matching"
              icon={<ShieldCheck className="w-5 h-5 text-[#475569]" />}
              className="md:col-span-2 md:row-span-1"
              delay={0.5}>
              <div className="flex items-center gap-6 h-full">
                <ShieldCheck className="w-12 h-12 text-indigo-300" />
                <div className="flex-1">
                  <h4 className="text-sm font-bold text-slate-800 mb-1">Your Identity is Protected</h4>
                  <p className="text-xs text-slate-500">
                    We match based on de-identified health profiles.
                    Researchers only see your eligibility data, not your name, until you choose to connect.
                  </p>
                </div>
              </div>
            </DashboardCard>

          </div>
        </div>
      </div>

      {/* css animation for scanner */}
      <style>{`
        @keyframes scout-scan {
          0% { left: 0; opacity: 0; }
          10% { opacity: 1; }
          90% { opacity: 1; }
          100% { left: 100%; opacity: 0; }
        }
        .animate-scout-scan {
          animation: scout-scan 2s linear infinite;
        }
      `}</style>

    </div>
  );
};

export default HeroPage;