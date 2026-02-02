import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom'; // Added for smooth navigation
import {
  UploadCloud,
  FileText,
  User,
  MapPin,
  Activity,
  Calendar,
  CheckCircle2,
  ArrowRight,
  Loader2
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
    condition: '',
    history: ''
  });
  const handleFileUpload = async (e) => {
    const uploadedFile = e.target.files ? e.target.files[0] : null;

    if (uploadedFile) {
      setFile(uploadedFile);
      setIsScanning(true);

      try {
        // 1. Prepare the file for the API
        const formDataPayload = new FormData();
        formDataPayload.append("file", uploadedFile); // 'file' matches the backend parameter

        // 2. Send to Backend (Agent 1 & 2)
        const response = await axios.post("http://127.0.0.1:8000/api/upload-and-match", formDataPayload, {
          headers: { "Content-Type": "multipart/form-data" },
        });

        // 3. Extract the Agent's answer
        const { extraction, matching } = response.data;
        // Check if extraction succeeded
        if (!extraction.success) {
          alert(extraction.error || "Failed to extract patient data");
          return;
        }
        const profile = extraction.profile;
        const trials = matching?.trials || [];
        setFormData({
          age: profile.age || '',
          gender: profile.gender || 'select',
          location: profile.location || '',
          condition: profile.conditions ? profile.conditions[0] : '', // First condition only
          history: profile.conditions?.join(', ') || ''
        });
        setFoundTrials(trials);
        console.log(" Extraction confidence:", extraction.confidence);
        console.log(" Missing fields:", extraction.missing_fields);
        console.log(" Found trials:", trials.length);
        console.log("Trials saved to state:", trials); // Debug check

        // OPTIONAL: You might want to store the 'trials' somewhere to pass to the next page
        // For now, we just auto-fill the form.

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
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragging(true);
    } else if (e.type === "dragleave") {
      setIsDragging(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      // Trigger the same upload logic
      handleFileUpload({ target: { files: e.dataTransfer.files } });
    }
  };




  // Update handleFileUpload to save trials too:
  // Inside the try block above, add: setFoundTrials(trials);

  const handleSubmit = () => {
    navigate('/results', {
      state: {
        userData: formData,    // The profile
        trials: foundTrials    // The list of matched trials <--- CRITICAL
      }
    });
  };
  return (
    // FIX 1: Added h-screen and overflow-hidden to main wrapper to prevent body scroll
    <div className="relative w-full h-screen bg-white font-sans selection:bg-indigo-100 selection:text-indigo-900 overflow-hidden pt-28 pb-12 px-6">

      <NetworkBackground />

      {/* Main Container */}
      <div className="relative z-10 max-w-6xl mx-auto h-full flex flex-col justify-center">

        {/* Header */}
        <div className="text-center mb-6 shrink-0">
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-4xl md:text-5xl font-light text-slate-900 mb-4"
          >
            Let's build your <span className="font-serif italic text-[#475569]">Profile</span>.
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-slate-500 max-w-lg mx-auto text-sm md:text-base"
          >
            Upload your medical reports for instant extraction, or manually enter your details below to begin the matching process.
          </motion.p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start h-auto max-h-[70vh]">

          {/* ---------------- LEFT COL: UPLOAD ZONE ---------------- */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="lg:col-span-5 h-full"
          >
            <div className={`relative h-full min-h-[400px] rounded-3xl border-2 border-dashed transition-all duration-300 flex flex-col items-center justify-center p-8 text-center group bg-white/50 backdrop-blur-sm ${isDragging
                ? 'border-indigo-500 bg-indigo-50/50 scale-[1.02]'
                : 'border-slate-200 hover:border-indigo-300 hover:bg-slate-50/50'
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >

              <input
                type="file"
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-20"
                onChange={handleFileUpload}
                accept=".pdf,.jpg,.png,.doc"
              />

              {/* Icon Animation */}
              <div className={`w-20 h-20 rounded-full bg-white shadow-lg flex items-center justify-center mb-6 transition-transform duration-500 ${isDragging ? 'scale-110' : 'group-hover:scale-110'}`}>
                {isScanning ? (
                  <Loader2 className="w-8 h-8 text-indigo-600 animate-spin" />
                ) : file ? (
                  <CheckCircle2 className="w-10 h-10 text-emerald-500" />
                ) : (
                  <UploadCloud className="w-8 h-8 text-indigo-500" />
                )}
              </div>

              {/* Text States */}
              <div className="relative z-10">
                {isScanning ? (
                  <div className="space-y-2">
                    <h3 className="text-lg font-bold text-slate-800">Analysing Document...</h3>
                    <p className="text-xs text-slate-500">The Profiler Agent is extracting your data.</p>
                  </div>
                ) : file ? (
                  <div className="space-y-2">
                    <h3 className="text-lg font-bold text-slate-800">Extraction Complete</h3>
                    <p className="text-xs text-slate-500 flex items-center justify-center gap-2">
                      <FileText className="w-3 h-3" /> {file.name}
                    </p>
                    <button
                      onClick={(e) => {
                        e.preventDefault();
                        setFile(null);
                        setFormData({ age: '', gender: 'select', location: '', condition: '', history: '' });
                      }}
                      className="text-xs text-red-500 font-bold hover:underline mt-2 z-30 relative"
                    >
                      Remove & Upload New
                    </button>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <h3 className="text-lg font-bold text-slate-800">Upload Report</h3>
                    <p className="text-xs text-slate-400 font-medium uppercase tracking-wider">Drag & Drop or Click</p>
                    <p className="text-[10px] text-slate-400 pt-4 max-w-[200px] mx-auto">
                      Supports PDF, JPG, PNG. Data is processed locally by the Profiler Agent.
                    </p>
                  </div>
                )}
              </div>

            </div>
          </motion.div>

          {/* ---------------- RIGHT COL: MANUAL FORM ---------------- */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="lg:col-span-7 h-full"
          >
            {/* FIX 2: Added max-h-[65vh] and overflow-y-auto here */}
            {/* This ensures the CARD scrolls internally if content expands, keeping the page fixed. */}
            <div className="bg-white rounded-3xl border border-slate-200 shadow-xl shadow-slate-200/50 p-8 relative max-h-[65vh] overflow-y-auto custom-scrollbar">

              {/* Highlight if Auto-filled */}
              {file && !isScanning && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  className="bg-emerald-50 border border-emerald-100 rounded-lg p-3 mb-6 flex items-center gap-3"
                >
                  <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                  <span className="text-xs text-emerald-800 font-bold">Data extracted successfully. Please verify below.</span>
                </motion.div>
              )}

              <div className="space-y-6">

                {/* Row 1: Age & Gender */}
                <div className="grid grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Age</label>
                    <div className="relative">
                      <Calendar className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                      <input
                        type="number"
                        value={formData.age}
                        onChange={(e) => setFormData({ ...formData, age: e.target.value })}
                        className="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-semibold text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
                        placeholder="24"
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Gender</label>
                    <div className="relative">
                      <User className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                      <select
                        value={formData.gender}
                        onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                        className="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-semibold text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all appearance-none"
                      >
                        <option value="select" disabled>Select</option>
                        <option value="Male">Male</option>
                        <option value="Female">Female</option>
                        <option value="Other">Other</option>
                      </select>
                    </div>
                  </div>
                </div>

                {/* Location */}
                <div className="space-y-2">
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Current Location</label>
                  <div className="relative">
                    <MapPin className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                    <input
                      type="text"
                      value={formData.location}
                      onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                      className="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-semibold text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
                      placeholder="e.g. Mumbai, Maharashtra"
                    />
                  </div>
                </div>

                {/* Condition */}
                <div className="space-y-2">
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Primary Diagnosis / Condition</label>
                  <div className="relative">
                    <Activity className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                    <input
                      type="text"
                      value={formData.condition}
                      onChange={(e) => setFormData({ ...formData, condition: e.target.value })}
                      className="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-semibold text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
                      placeholder="e.g. Type 2 Diabetes"
                    />
                  </div>
                </div>

                {/* Medical History */}
                <div className="space-y-2">
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Brief Medical History</label>
                  <textarea
                    rows={4}
                    value={formData.history}
                    onChange={(e) => setFormData({ ...formData, history: e.target.value })}
                    className="w-full p-4 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all resize-none"
                    placeholder="List previous treatments, allergies, or genetic markers..."
                  />
                </div>

                {/* CTA Button */}
                <button
                  onClick={handleSubmit}
                  disabled={!formData.condition || !formData.location} // Basic validation
                  className="w-full py-4 bg-[#475569] text-white rounded-xl font-bold uppercase tracking-widest text-xs hover:bg-slate-700 hover:scale-[1.02] transition-all shadow-lg shadow-slate-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  Launch Matching Agents <ArrowRight className="w-4 h-4" />
                </button>

              </div>
            </div>
          </motion.div>

        </div>
      </div>
    </div>
  );
};

export default FindMatch;