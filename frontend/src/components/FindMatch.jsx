import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
  UploadCloud, FileText, User, MapPin, Activity, Calendar,
  CheckCircle2, ArrowRight, Loader2, Pill, FlaskConical,
  AlertCircle,
  CloudCog
} from 'lucide-react';
import NetworkBackground from './NetworkBackground';
import axios from 'axios';

const FindMatch = () => {
  const navigate = useNavigate();
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState(null);
  const [isScanning, setIsScanning] = useState(false);
  const [foundTrials, setFoundTrials] = useState([]);

  const [formData, setFormData] = useState({
    age: '',
    gender: 'select',
    location: '',
    conditions: '',
    medications: '',
    lab_values: '',
    allergies: ''
  });

  const handleFileUpload = async (e) => {
    const uploadedFile = e.target.files ? e.target.files[0] : null;

    if (uploadedFile) {
      setFile(uploadedFile);
      setIsScanning(true);

      try {
        const formDataPayload = new FormData();
        formDataPayload.append("file", uploadedFile);

        const response = await axios.post("http://127.0.0.1:8000/api/complete-workflow", formDataPayload, {
          headers: { "Content-Type": "multipart/form-data" },
        });

        const { extraction, trials, eligible_count, total_trials_found } = response.data;
        if (!extraction.success) {
          alert(extraction.error || "Failed to extract patient data");
          return;
        }
        const p = extraction.profile;
        // Log agent results
        console.log("✅ Agent 1: Profile Extracted");
        console.log("✅ Agent 2: Found", total_trials_found, "trials");
        console.log("✅ Agent 3-5: Processed", trials.length, "trials");
        console.log("📊 Eligible trials:", eligible_count);
        console.log("🎯 Sample trial data:", trials[0]); // Debug log
        // Show enriched trials (now includes eligibility, diversity, explanation)
        setFoundTrials(trials);
        const formatMeds = (meds) => meds && meds.length ? meds.map(m => `${m.name} ${m.dose} (${m.frequency})`).join('\n') : '';
        const formatLabs = (labs) => labs ? Object.entries(labs).map(([k, v]) => `${k}: ${v.value} ${v.unit || ''}`).join('\n') : '';
        setFormData({
          age: p.age || '',
          gender: p.gender || 'select',
          location: p.location || '',
          conditions: p.conditions ? p.conditions.join(', ') : '',
          medications: formatMeds(p.medications),
          lab_values: formatLabs(p.lab_values),
          allergies: p.allergies ? p.allergies.join(', ') : ''
        });

      } catch (error) {
        console.error("API Error:", error);
        alert("Agent failed to read file. Please try again.");
      } finally {
        setIsScanning(false);
      }
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(e.type === "dragenter" || e.type === "dragover");
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload({ target: { files: e.dataTransfer.files } });
    }
  };

  const handleSubmit = () => {
    navigate('/results', {
      state: { userData: formData, trials: foundTrials }
    });
  };

  const isValid = formData.age && formData.gender !== 'select' && formData.location && formData.conditions;

  return (
    <div className="relative w-full h-screen bg-white font-sans selection:bg-indigo-100 selection:text-indigo-900 overflow-hidden pt-28 pb-12 px-6">

      <NetworkBackground />

      <div className="relative z-10 max-w-6xl mx-auto h-full flex flex-col justify-center">

        {/* Header */}
        <div className="text-center mb-6 shrink-0">
          <motion.h1
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
            className="text-4xl md:text-5xl font-light text-slate-900 mb-4"
          >
            Let's build your <span className="font-serif italic text-[#475569]">Profile</span>.
          </motion.h1>
          <p className="text-slate-500 max-w-lg mx-auto text-sm md:text-base">
            Upload your medical reports for instant extraction.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start h-auto max-h-[70vh]">

          {/* ---------------- LEFT COL: UPLOAD ZONE ---------------- */}
          <motion.div
            initial={{ opacity: 0, x: -30 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }}
            className="lg:col-span-5 h-full"
          >
            <div className={`relative h-full min-h-[400px] rounded-3xl border-2 border-dashed transition-all duration-300 flex flex-col items-center justify-center p-8 text-center group bg-white/50 backdrop-blur-sm ${isDragging
                ? 'border-indigo-500 bg-indigo-50/50 scale-[1.02]'
                : 'border-slate-200 hover:border-indigo-400'
              }`}
              onDragEnter={handleDrag} onDragLeave={handleDrag} onDragOver={handleDrag} onDrop={handleDrop}
            >
              <input type="file" className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-20" onChange={handleFileUpload} accept=".pdf,.jpg,.png,.doc" />

              <div className={`w-20 h-20 rounded-full bg-white shadow-lg flex items-center justify-center mb-6 transition-transform duration-500 ${isDragging ? 'scale-110' : 'group-hover:scale-110'}`}>
                {isScanning ? <Loader2 className="w-8 h-8 text-indigo-500 animate-spin" /> :
                  file ? <CheckCircle2 className="w-10 h-10 text-emerald-500" /> :
                    <UploadCloud className="w-8 h-8 text-indigo-500" />}
              </div>

              <div className="relative z-10">
                {isScanning ? (
                  <div className="space-y-2">
                    <h3 className="text-lg font-bold text-slate-800">Analysing Document...</h3>
                    <p className="text-xs text-slate-500">The Profiler Agent is extracting your data.</p>
                  </div>
                ) : file ? (
                  <div className="space-y-2">
                    <h3 className="text-lg font-bold text-slate-800">Extraction Complete</h3>
                    <p className="text-xs text-slate-500 flex items-center justify-center gap-2"><FileText className="w-3 h-3" /> {file.name}</p>
                    <button onClick={(e) => { e.preventDefault(); setFile(null); }} className="text-xs text-red-500 font-bold hover:underline mt-2 z-30 relative">Remove & Upload New</button>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <h3 className="text-lg font-bold text-slate-800">Upload Report</h3>
                    <p className="text-xs text-slate-400 font-medium uppercase tracking-wider">Drag & Drop or Click</p>
                    <p className="text-[10px] text-slate-400 mt-2 font-medium">Upload PDF, PNG, JPG</p>
                  </div>
                )}
              </div>
            </div>
          </motion.div>

          {/* ---------------- RIGHT COL: EDITABLE FORM ---------------- */}
          <motion.div
            initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3 }}
            className="lg:col-span-7 h-full"
          >
            <div className="bg-white rounded-3xl border border-slate-200 shadow-xl shadow-slate-200/50 p-8 relative max-h-[65vh] overflow-y-auto custom-scrollbar">

              {file && !isScanning && (
                <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} className="bg-emerald-50 border border-emerald-100 rounded-lg p-3 mb-6 flex items-center gap-3">
                  <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                  <span className="text-xs text-emerald-800 font-bold">Data extracted. Review and edit below.</span>
                </motion.div>
              )}

              <div className="space-y-6">

                {/* 1. Demographics */}
                <div className="flex items-center gap-2 mb-2 border-b border-slate-100 pb-2">
                  <User className="w-3 h-3 text-[#475569]" />
                  <h3 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Patient Profile</h3>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <label className="text-[9px] font-bold text-slate-500 uppercase tracking-widest">Age <span className="text-red-400">*</span></label>
                    {/* Added px-4 manually here because we removed it from CSS */}
                    <input type="number" value={formData.age} onChange={e => setFormData({ ...formData, age: e.target.value })}
                      className="form-input h-12 px-4" placeholder="--" required />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-[9px] font-bold text-slate-500 uppercase tracking-widest">Gender <span className="text-red-400">*</span></label>
                    {/* Added px-4 manually here */}
                    <select value={formData.gender} onChange={e => setFormData({ ...formData, gender: e.target.value })} className="form-input h-12 px-4 appearance-none cursor-pointer">
                      <option value="select" disabled>Select</option>
                      <option value="Male">Male</option>
                      <option value="Female">Female</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                </div>

                {/* Location - FIXED PADDING */}
                <div className="space-y-1.5">
                  <label className="text-[9px] font-bold text-slate-500 uppercase tracking-widest">Location <span className="text-red-400">*</span></label>
                  <div className="relative">
                    <MapPin className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-[#475569]" />
                    {/* Using pl-14 (3.5rem) to ensure plenty of space */}
                    <input type="text" value={formData.location} onChange={e => setFormData({ ...formData, location: e.target.value })}
                      className="form-input h-12 pl-10 pr-4" placeholder="e.g. Mumbai, Maharashtra" required />
                  </div>
                </div>

                <div className="h-px bg-slate-100 w-full my-2"></div>

                {/* 2. Clinical Data */}
                <div className="space-y-4">

                  {/* Conditions */}
                  <div className="space-y-1.5">
                    <div className="flex items-center gap-2">
                      <Activity className="w-3 h-3 text-[#475569]" />
                      <label className="text-[9px] font-bold text-slate-500 uppercase tracking-widest">Diagnosed Conditions <span className="text-red-400">*</span></label>
                    </div>
                    {/* Added px-4 manually here */}
                    <input type="text" value={formData.conditions} onChange={e => setFormData({ ...formData, conditions: e.target.value })}
                      className="form-input h-12 px-4" placeholder="e.g. Type 2 Diabetes, Hypertension" />
                  </div>

                  {/* Medications */}
                  <div className="space-y-1.5">
                    <div className="flex items-center gap-2">
                      <Pill className="w-3 h-3 text-[#475569]" />
                      <label className="text-[9px] font-bold text-slate-500 uppercase tracking-widest">Current Medications</label>
                    </div>
                    <textarea rows={3} value={formData.medications} onChange={e => setFormData({ ...formData, medications: e.target.value })}
                      className="form-textarea p-4" placeholder={`Lisinopril 20mg (Daily)\nMetformin 500mg (Twice Daily)`} />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    {/* Labs */}
                    <div className="space-y-1.5">
                      <div className="flex items-center gap-2">
                        <FlaskConical className="w-3 h-3 text-[#475569]" />
                        <label className="text-[9px] font-bold text-slate-500 uppercase tracking-widest">Lab Values</label>
                      </div>
                      <textarea rows={2} value={formData.lab_values} onChange={e => setFormData({ ...formData, lab_values: e.target.value })}
                       
                        className="form-textarea p-4" placeholder={`HbA1c: 7.2%\nBP: 130/85`} />
                    </div>

                    {/* Allergies */}
                    <div className="space-y-1.5">
                      <div className="flex items-center gap-2">
                        <AlertCircle className="w-3 h-3 text-[#475569]" />
                        <label className="text-[9px] font-bold text-slate-500 uppercase tracking-widest">Allergies</label>
                      </div>
                      <textarea rows={2} value={formData.allergies} onChange={e => setFormData({ ...formData, allergies: e.target.value })}
                        className="form-textarea p-4" placeholder="e.g. Penicillin, Peanuts" />
                    </div>
                  </div>
                </div>

                {/* CTA Button */}
                <button
                  onClick={handleSubmit}
                  disabled={!isValid}
                  className="w-full py-4 bg-[#475569] text-white rounded-xl font-bold uppercase tracking-widest text-xs hover:bg-slate-800 hover:scale-[1.02] transition-all shadow-lg shadow-slate-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 mt-2"
                >
                  Launch Matching Agents <ArrowRight className="w-4 h-4" />
                </button>

              </div>
            </div>
          </motion.div>

        </div>
      </div>

      {/* CSS: Removed padding from classes so inline utility classes take effect */}
      <style>{`
        .form-input {
          width: 100%;
          background-color: #f8fafc;
          border: 1px solid #e2e8f0;
          border-radius: 0.75rem;
          /* Removed 'padding' here to allow pl-14 to work */
          font-size: 0.875rem;
          color: #334155;
          outline: none;
          transition: all 0.2s;
        }
        .form-input:focus { 
          border-color: #6366f1; /* Indigo Focus */
          background-color: #fff; 
          box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1); 
        }
        
        .form-textarea {
          width: 100%;
          background-color: #f8fafc;
          border: 1px solid #e2e8f0;
          border-radius: 0.75rem;
          /* Removed 'padding' here */
          font-size: 0.875rem;
          color: #334155;
          outline: none;
          transition: all 0.2s;
          resize: none;
          font-family: monospace;
        }
        .form-textarea:focus { 
          border-color: #6366f1; 
          background-color: #fff; 
          box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1); 
        }

        .custom-scrollbar::-webkit-scrollbar { width: 4px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background-color: #cbd5e1; border-radius: 10px; }
      `}</style>
    </div>
  );
};

export default FindMatch;