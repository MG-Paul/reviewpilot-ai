"use client";

import React, { useState } from 'react';
import { Play, Plus, Check, X, Layers, AlertCircle, FileText, Database, TrendingUp, HelpCircle } from 'lucide-react';

export default function HomePage() {
  const [activeTab, setActiveTab] = useState<'info' | 'prototype'>('info');
  
  // Interactive prototype states
  const [projectCreated, setProjectCreated] = useState(false);
  const [projectName, setProjectName] = useState('Hypertension Study');
  const [currentStep, setCurrentStep] = useState<'import' | 'dedup' | 'screen' | 'extract' | 'analysis'>('import');
  
  // Dedup states
  const [duplicateResolved, setDuplicateResolved] = useState(false);
  
  // Screening states
  const [screenedCount, setScreenedCount] = useState(0);
  const [screeningDecision, setScreeningDecision] = useState<string | null>(null);
  
  // Extraction states
  const [hoveredField, setHoveredField] = useState<string | null>(null);
  const [extractionVerified, setExtractionVerified] = useState(false);
  
  // Meta-analysis states
  const [metaRunning, setMetaRunning] = useState(false);
  const [metaResults, setMetaResults] = useState<any>(null);

  const sampleStudies = [
    { author: "Smith et al.", year: 2023, n_exp: 60, event_exp: 12, n_ctrl: 60, event_ctrl: 22 },
    { author: "Müller et al.", year: 2024, n_exp: 45, event_exp: 8, n_ctrl: 45, event_ctrl: 18 },
    { author: "Chen et al.", year: 2025, n_exp: 80, event_exp: 15, n_ctrl: 80, event_ctrl: 30 }
  ];

  const triggerMetaAnalysis = () => {
    setMetaRunning(true);
    setTimeout(() => {
      setMetaRunning(false);
      setMetaResults({
        effect_size: 0.45,
        lower_ci: 0.28,
        upper_ci: 0.72,
        i2: "12%",
        p_value: 0.001
      });
    }, 1500);
  };

  const stepsInfo = [
    {
      step: "01",
      title: "Protocol & Import",
      description: "Upload RIS, BibTeX, or PDF files. AI reads your PROSPERO protocol to generate customized extraction schemas.",
      badge: "FastAPI / S3"
    },
    {
      step: "02",
      title: "Semantic Deduplication",
      description: "Identify and resolve duplicates with PubMedBERT embeddings and side-by-side visual diff comparisons.",
      badge: "pgvector"
    },
    {
      step: "03",
      title: "Blind Screening",
      description: "Perform double-blind title/abstract screening. AI recommends inclusions/exclusions with explanations.",
      badge: "LangGraph Agent"
    },
    {
      step: "04",
      title: "Grounded Extraction",
      description: "Extract characteristics with pixel-level highlights mapped directly to source text in the PDF canvas viewer.",
      badge: "Marker OCR"
    },
    {
      step: "05",
      title: "Reactive Meta-Analysis",
      description: "Perform instant local synthesis and forest plots via client-side webR (WASM) or server-side Plumber API.",
      badge: "webR / R Sandbox"
    },
    {
      step: "06",
      title: "AI Synthesis & Draft",
      description: "Auto-generate draft Methods and Results sections based on study databases with full audit tracking.",
      badge: "GPT-4 / DeepSeek"
    }
  ];

  return (
    <div className="space-y-12">
      {/* Navigation Tabs */}
      <div className="flex justify-center border-b border-slate-800">
        <button
          onClick={() => setActiveTab('info')}
          className={`px-6 py-3 font-semibold text-sm transition-all border-b-2 ${
            activeTab === 'info' 
              ? 'border-indigo-500 text-indigo-400' 
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Product Architecture
        </button>
        <button
          onClick={() => setActiveTab('prototype')}
          className={`px-6 py-3 font-semibold text-sm transition-all border-b-2 ${
            activeTab === 'prototype' 
              ? 'border-indigo-500 text-indigo-400' 
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Interactive App Sandbox
        </button>
      </div>

      {activeTab === 'info' ? (
        <>
          {/* Hero Section */}
          <section className="text-center py-16 space-y-6 relative overflow-hidden rounded-3xl border border-slate-800 bg-slate-900/20 backdrop-blur-sm px-6">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-indigo-500/10 opacity-30 pointer-events-none" />
            <h1 className="text-4xl md:text-6xl font-black tracking-tight leading-none bg-gradient-to-r from-white via-slate-100 to-indigo-200 bg-clip-text text-transparent">
              Evidence Synthesis,<br />Accelerated by AI.
            </h1>
            <p className="max-w-2xl mx-auto text-lg text-slate-400">
              Automate systematic reviews from RIS imports to forest plots with grounded PDF extraction and a local WebAssembly R execution sandbox.
            </p>
            <div className="flex justify-center gap-4 pt-4">
              <button 
                onClick={() => setActiveTab('prototype')}
                className="px-6 py-3 flex items-center gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold rounded-lg shadow-lg shadow-indigo-500/20 transition-all"
              >
                <Plus size={18} /> Create Review Project
              </button>
              <button 
                onClick={() => setActiveTab('prototype')}
                className="px-6 py-3 flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold rounded-lg border border-slate-700 transition-all"
              >
                <Play size={16} /> Open Interactive Sandbox
              </button>
            </div>
          </section>

          {/* Review Pilot Workflow Steps */}
          <section className="space-y-8">
            <div className="text-center space-y-2">
              <h2 className="text-3xl font-bold tracking-tight text-white">Coordinated Review Pipeline</h2>
              <p className="text-slate-400">Automate systematic reviews while keeping researchers in complete control of final decisions.</p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {stepsInfo.map((item, idx) => (
                <div key={idx} className="group relative border border-slate-800 hover:border-slate-700 bg-slate-900/40 p-6 rounded-xl hover:bg-slate-900/60 transition-all duration-300">
                  <div className="absolute top-4 right-4 text-xs font-semibold px-2 py-0.5 rounded bg-slate-800 text-slate-400 group-hover:bg-slate-700 group-hover:text-indigo-400 transition-all">
                    {item.badge}
                  </div>
                  <div className="text-4xl font-extrabold text-blue-500/20 mb-4">{item.step}</div>
                  <h3 className="text-lg font-bold text-white mb-2">{item.title}</h3>
                  <p className="text-slate-400 text-sm leading-relaxed">{item.description}</p>
                </div>
              ))}
            </div>
          </section>
        </>
      ) : (
        /* Interactive App Sandbox */
        <div className="bg-slate-950 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl">
          {/* Header Panel */}
          <div className="bg-slate-900/80 px-6 py-4 border-b border-slate-800 flex justify-between items-center">
            <div>
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <Database className="text-indigo-400" size={18} />
                {projectName} {!projectCreated && <span className="text-xs bg-amber-500/10 text-amber-400 border border-amber-500/20 px-2 py-0.5 rounded-full font-normal">New Project Config</span>}
              </h2>
              <p className="text-xs text-slate-400">Systematic Review Interactive Sandbox Pipeline</p>
            </div>
            {projectCreated && (
              <div className="flex gap-1.5 bg-slate-950 p-1 rounded-lg border border-slate-800">
                {(['import', 'dedup', 'screen', 'extract', 'analysis'] as const).map((step) => (
                  <button
                    key={step}
                    onClick={() => setCurrentStep(step)}
                    className={`text-xs px-3 py-1.5 rounded-md font-medium transition-all capitalize ${
                      currentStep === step 
                        ? 'bg-indigo-600 text-white shadow-md' 
                        : 'text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    {step}
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="p-8 min-h-[480px]">
            {/* Project Creation step */}
            {!projectCreated ? (
              <div className="max-w-md mx-auto space-y-6 py-8">
                <div className="text-center space-y-2">
                  <h3 className="text-xl font-semibold text-white">Create Systematic Review</h3>
                  <p className="text-sm text-slate-400">Configure your review scope and title to initialize the pipeline.</p>
                </div>
                <div className="space-y-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Project Title</label>
                    <input 
                      type="text" 
                      value={projectName}
                      onChange={(e) => setProjectName(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-800 rounded-lg px-4 py-3 text-sm text-white focus:outline-none focus:border-indigo-500 transition-all"
                      placeholder="e.g. Beta-Blockers impact on Hypertension"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">PICOS Target Population</label>
                    <input 
                      type="text" 
                      defaultValue="Hypertensive Adults"
                      className="w-full bg-slate-900 border border-slate-800 rounded-lg px-4 py-3 text-sm text-white focus:outline-none focus:border-indigo-500 transition-all"
                    />
                  </div>
                  <button 
                    onClick={() => setProjectCreated(true)}
                    className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-lg shadow-lg shadow-indigo-500/10 transition-all flex items-center justify-center gap-2"
                  >
                    Configure Project <Plus size={16} />
                  </button>
                </div>
              </div>
            ) : (
              /* Pipeline Steps UI rendering */
              <div className="space-y-6">
                {/* 1. Import step */}
                {currentStep === 'import' && (
                  <div className="space-y-6">
                    <div className="border-2 border-dashed border-slate-800 rounded-xl p-12 text-center bg-slate-900/10 hover:bg-slate-900/20 transition-all">
                      <FileText className="mx-auto text-indigo-400 mb-4" size={42} />
                      <h3 className="text-lg font-bold text-white mb-1">Import Reference Dataset</h3>
                      <p className="text-sm text-slate-400 max-w-sm mx-auto mb-6">Drag and drop your RIS, BibTeX, or Zotero XML files to load them into the screening queue.</p>
                      <button 
                        onClick={() => setCurrentStep('dedup')}
                        className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-lg transition-all"
                      >
                        Load 5 Sample Studies
                      </button>
                    </div>
                  </div>
                )}

                {/* 2. Deduplication step */}
                {currentStep === 'dedup' && (
                  <div className="space-y-6">
                    <div className="flex justify-between items-center bg-slate-900/40 p-4 border border-slate-800 rounded-xl">
                      <div className="flex items-center gap-3">
                        <AlertCircle className="text-amber-400 animate-pulse" size={20} />
                        <div>
                          <h4 className="text-sm font-semibold text-white">Duplicate Records Flagged</h4>
                          <p className="text-xs text-slate-400">pgvector cosine similarity detected 1 potential duplicate pair.</p>
                        </div>
                      </div>
                      <span className="text-xs font-semibold bg-red-500/10 text-red-400 border border-red-500/20 px-2.5 py-1 rounded-full">
                        Similarity: 98.4%
                      </span>
                    </div>

                    <div className="grid md:grid-cols-2 gap-6">
                      <div className="border border-slate-800 bg-slate-900/20 p-5 rounded-xl space-y-3 relative">
                        <span className="absolute top-4 right-4 text-[10px] bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 px-2 py-0.5 rounded uppercase font-semibold">Primary (Database)</span>
                        <h4 className="text-sm font-bold text-white pr-16">Effect of Drug X on Hypertension patients: a randomized trial</h4>
                        <p className="text-xs text-slate-400 leading-relaxed"><strong>Abstract:</strong> We conducted a trial evaluating drug X in patients diagnosed with chronic hypertension. High blood pressure levels dropped significantly in the treatment group compared to placebo...</p>
                        <div className="text-xs text-slate-500">DOI: 10.1016/j.jmi.2025.01.002 | Year: 2025</div>
                      </div>

                      <div className="border border-slate-800 bg-slate-900/20 p-5 rounded-xl space-y-3 relative">
                        <span className="absolute top-4 right-4 text-[10px] bg-amber-500/10 text-amber-300 border border-amber-500/20 px-2 py-0.5 rounded uppercase font-semibold">Import Record</span>
                        <h4 className="text-sm font-bold text-white pr-16">Effect of Drug X on Hypertension Patients: A Randomized Trial</h4>
                        <p className="text-xs text-slate-400 leading-relaxed"><strong>Abstract:</strong> We conducted a trial evaluating drug X in patients diagnosed with chronic hypertension. High blood pressure levels dropped significantly in the treatment group compared to placebo...</p>
                        <div className="text-xs text-slate-500">DOI: 10.1016/j.jmi.2025.01.002 | Year: 2025</div>
                      </div>
                    </div>

                    <div className="flex justify-end gap-3 pt-2">
                      <button 
                        onClick={() => setDuplicateResolved(true)}
                        className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-lg text-sm transition-all"
                      >
                        Merge Records (Keep Primary)
                      </button>
                      <button 
                        onClick={() => setDuplicateResolved(true)}
                        className="px-5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold rounded-lg text-sm border border-slate-700 transition-all"
                      >
                        Keep Separate
                      </button>
                    </div>

                    {duplicateResolved && (
                      <div className="bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 px-4 py-3 rounded-lg text-sm flex items-center justify-between">
                        <span>Success: Duplicate pair resolved.</span>
                        <button 
                          onClick={() => setCurrentStep('screen')}
                          className="font-semibold hover:underline"
                        >
                          Proceed to Screening &rarr;
                        </button>
                      </div>
                    )}
                  </div>
                )}

                {/* 3. Screening step */}
                {currentStep === 'screen' && (
                  <div className="space-y-6">
                    <div className="border border-slate-800 bg-slate-900/20 rounded-xl p-6 space-y-4">
                      <div className="flex justify-between items-center">
                        <span className="text-xs text-slate-500 font-mono">Reference ID: study_03_chen</span>
                        <span className="text-xs bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 px-2 py-0.5 rounded">Double Blind Screening Queue</span>
                      </div>
                      <h3 className="text-lg font-bold text-white">Efficacy of Drug X on primary hypertension in older adults</h3>
                      <p className="text-sm text-slate-300 leading-relaxed">
                        <strong>Abstract:</strong> Objectives: To test whether drug X reduces diastolic and systolic blood pressure in individuals over 65 years. Methods: A multi-center randomized placebo-controlled cohort study. Results: Mean systolic pressure dropped by 14 mmHg (p &lt; 0.001) in treatment compared to placebo group.
                      </p>
                    </div>

                    {/* AI Screening Suggestion Auditor panel */}
                    <div className="bg-indigo-950/20 border border-indigo-500/20 rounded-xl p-5 space-y-2">
                      <h4 className="text-xs font-semibold text-indigo-400 flex items-center gap-2 uppercase tracking-wider">
                        <Layers size={14} /> AI Copilot Recommendation
                      </h4>
                      <p className="text-sm text-slate-200"><strong>Recommendation: Include</strong> (Confidence: 94%)</p>
                      <p className="text-xs text-slate-400">
                        The study aligns with your PICOS criteria. 
                        <strong>Population:</strong> Adults over 65 (matches "hypertensive adults"). 
                        <strong>Intervention:</strong> Drug X (matches "drug X").
                      </p>
                    </div>

                    <div className="flex gap-3 justify-center">
                      <button 
                        onClick={() => {
                          setScreeningDecision('include');
                          setScreenedCount(prev => prev + 1);
                        }}
                        className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-lg text-sm flex items-center gap-2 transition-all"
                      >
                        <Check size={16} /> Include Study
                      </button>
                      <button 
                        onClick={() => {
                          setScreeningDecision('exclude');
                          setScreenedCount(prev => prev + 1);
                        }}
                        className="px-6 py-2.5 bg-red-600 hover:bg-red-500 text-white font-semibold rounded-lg text-sm flex items-center gap-2 transition-all"
                      >
                        <X size={16} /> Exclude Study
                      </button>
                    </div>

                    {screeningDecision && (
                      <div className="bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 px-4 py-3 rounded-lg text-sm flex items-center justify-between">
                        <span>Decision registered: Study marked as <strong>{screeningDecision}</strong>. Total Screened: {screenedCount}</span>
                        <button 
                          onClick={() => {
                            setScreeningDecision(null);
                            setCurrentStep('extract');
                          }}
                          className="font-semibold hover:underline"
                        >
                          Proceed to PDF Extraction &rarr;
                        </button>
                      </div>
                    )}
                  </div>
                )}

                {/* 4. Extraction step */}
                {currentStep === 'extract' && (
                  <div className="space-y-6">
                    <div className="text-xs bg-slate-900 p-3 rounded-lg border border-slate-800 text-slate-400">
                      💡 <strong>Grounded PDF Provenance:</strong> Hover over the extracted fields on the left to see the source coordinates highlight in the PDF text layout on the right.
                    </div>

                    <div className="grid md:grid-cols-2 gap-6">
                      {/* Left: Fields */}
                      <div className="space-y-4">
                        <h4 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">Extracted Fields</h4>
                        
                        <div 
                          onMouseEnter={() => setHoveredField('sample_size')}
                          onMouseLeave={() => setHoveredField(null)}
                          className={`p-4 rounded-lg border transition-all cursor-pointer ${
                            hoveredField === 'sample_size' 
                              ? 'border-indigo-500 bg-indigo-500/5' 
                              : 'border-slate-800 bg-slate-900/30'
                          }`}
                        >
                          <div className="text-xs font-semibold text-indigo-400">Sample Size (N)</div>
                          <div className="text-lg font-bold text-white mt-1">120 patients</div>
                          <div className="text-[10px] text-slate-500 mt-1">AI Confidence: 92% | Page 3</div>
                        </div>

                        <div 
                          onMouseEnter={() => setHoveredField('study_design')}
                          onMouseLeave={() => setHoveredField(null)}
                          className={`p-4 rounded-lg border transition-all cursor-pointer ${
                            hoveredField === 'study_design' 
                              ? 'border-indigo-500 bg-indigo-500/5' 
                              : 'border-slate-800 bg-slate-900/30'
                          }`}
                        >
                          <div className="text-xs font-semibold text-indigo-400">Study Design</div>
                          <div className="text-lg font-bold text-white mt-1">Randomized Controlled Trial (RCT)</div>
                          <div className="text-[10px] text-slate-500 mt-1">AI Confidence: 98% | Page 1</div>
                        </div>
                      </div>

                      {/* Right: PDF Viewer simulator */}
                      <div className="border border-slate-850 bg-slate-900/10 rounded-xl p-5 flex flex-col justify-between h-[280px]">
                        <div>
                          <div className="flex justify-between items-center text-[10px] text-slate-500 border-b border-slate-850 pb-2 mb-3">
                            <span>study_pdf_viewer.pdf (Page 1)</span>
                            <span>Scale: 100%</span>
                          </div>
                          
                          <div className="text-xs leading-relaxed space-y-3 font-mono text-slate-400">
                            <p>
                              We conducted a multicenter study.{' '}
                              <span className={`px-1.5 py-0.5 rounded transition-all ${
                                hoveredField === 'study_design' 
                                  ? 'bg-yellow-400/25 text-yellow-300 font-bold border border-yellow-500/30' 
                                  : ''
                              }`}>
                                Randomized Controlled Trial
                              </span>{' '}
                              recruitment occurred between 2023 and 2024.
                            </p>
                            <p>
                              Patient recruitment summary: A total of{' '}
                              <span className={`px-1.5 py-0.5 rounded transition-all ${
                                hoveredField === 'sample_size' 
                                  ? 'bg-yellow-400/25 text-yellow-300 font-bold border border-yellow-500/30' 
                                  : ''
                              }`}>
                                120 patients
                              </span>{' '}
                              diagnosed with hypertension were randomized 1:1.
                            </p>
                          </div>
                        </div>

                        <div className="flex justify-end gap-2 mt-4 pt-2 border-t border-slate-850">
                          <button 
                            onClick={() => setExtractionVerified(true)}
                            className="text-xs bg-indigo-600 hover:bg-indigo-500 text-white font-semibold px-4 py-2 rounded transition-all"
                          >
                            Verify Extracted Fields
                          </button>
                        </div>
                      </div>
                    </div>

                    {extractionVerified && (
                      <div className="bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 px-4 py-3 rounded-lg text-sm flex items-center justify-between">
                        <span>Characteristics verified. Baseline tables generated.</span>
                        <button 
                          onClick={() => setCurrentStep('analysis')}
                          className="font-semibold hover:underline"
                        >
                          Open Meta-Analysis &rarr;
                        </button>
                      </div>
                    )}
                  </div>
                )}

                {/* 5. Meta-Analysis step */}
                {currentStep === 'analysis' && (
                  <div className="space-y-6">
                    <div className="grid md:grid-cols-3 gap-6">
                      <div className="md:col-span-1 border border-slate-800 bg-slate-900/30 p-5 rounded-xl space-y-4 h-fit">
                        <h4 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">Parameters</h4>
                        <div className="space-y-3">
                          <div>
                            <label className="block text-xs text-slate-400 mb-1">Synthesis Model</label>
                            <select className="w-full bg-slate-900 border border-slate-850 rounded px-3 py-2 text-xs text-white">
                              <option>Random Effects (Inverse Variance)</option>
                              <option>Fixed Effect</option>
                            </select>
                          </div>
                          <div>
                            <label className="block text-xs text-slate-400 mb-1">Effect Measure</label>
                            <select className="w-full bg-slate-900 border border-slate-850 rounded px-3 py-2 text-xs text-white">
                              <option>Odds Ratio (OR)</option>
                              <option>Risk Ratio (RR)</option>
                              <option>Mean Difference (MD)</option>
                            </select>
                          </div>
                        </div>

                        <button 
                          onClick={triggerMetaAnalysis}
                          disabled={metaRunning}
                          className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-lg text-xs shadow-md transition-all flex items-center justify-center gap-2"
                        >
                          {metaRunning ? 'Compiling R Engine...' : 'Run Analysis in webR (WASM)'}
                        </button>
                      </div>

                      <div className="md:col-span-2 border border-slate-800 bg-slate-900/10 rounded-xl p-5 min-h-[250px] flex flex-col justify-center items-center">
                        {metaRunning && (
                          <div className="text-center space-y-2">
                            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-indigo-500 mx-auto" />
                            <p className="text-xs text-slate-400">Loading WebAssembly package dependencies...</p>
                          </div>
                        )}

                        {!metaRunning && !metaResults && (
                          <div className="text-center space-y-1">
                            <TrendingUp className="mx-auto text-slate-600 mb-2" size={32} />
                            <p className="text-sm text-slate-400">No active calculations loaded.</p>
                            <p className="text-xs text-slate-500">Configure parameters on the left and trigger compilation.</p>
                          </div>
                        )}

                        {!metaRunning && metaResults && (
                          <div className="w-full space-y-6">
                            <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Live Forest Plot SVG Output</h4>
                            
                            {/* Forest Plot SVG visualization */}
                            <div className="bg-white/5 border border-slate-800 p-4 rounded-lg flex flex-col space-y-4">
                              <div className="flex justify-between text-[10px] text-slate-400 border-b border-slate-800 pb-2 font-mono">
                                <span>Study (Year)</span>
                                <span>OR [95% CI]</span>
                              </div>
                              {sampleStudies.map((study, idx) => (
                                <div key={idx} className="flex justify-between items-center text-xs font-mono">
                                  <span>{study.author} ({study.year})</span>
                                  
                                  {/* Graphical forest plot representation */}
                                  <div className="flex-1 mx-6 relative h-4 bg-slate-800/30 rounded flex items-center">
                                    {/* Line for confidence interval */}
                                    <div className="absolute left-[30%] right-[40%] h-0.5 bg-slate-400" />
                                    {/* Dot for effect size */}
                                    <div className="absolute left-[45%] h-2 w-2 bg-indigo-500 rounded-sm" />
                                    {/* Line for null effect */}
                                    <div className="absolute left-[50%] top-0 bottom-0 w-0.5 bg-red-500/40 border-dashed" />
                                  </div>

                                  <span>0.45 [0.28, 0.72]</span>
                                </div>
                              ))}

                              {/* Heterogeneity and summary line */}
                              <div className="border-t border-slate-800 pt-3 flex justify-between text-xs font-mono font-bold">
                                <span>Random Effects Model</span>
                                <div className="flex-1 mx-6 relative h-4 flex items-center">
                                  <div className="absolute left-[38%] right-[42%] h-0.5 bg-indigo-400" />
                                  <div className="absolute left-[40%] h-2 w-2 bg-indigo-500 transform rotate-45" />
                                  <div className="absolute left-[50%] top-0 bottom-0 w-0.5 bg-red-500/40 border-dashed" />
                                </div>
                                <span>{metaResults.effect_size} [{metaResults.lower_ci}, {metaResults.upper_ci}]</span>
                              </div>
                            </div>

                            {/* Summary Metrics list */}
                            <div className="grid grid-cols-3 gap-4 text-center">
                              <div className="bg-slate-900/40 border border-slate-850 p-3 rounded-lg">
                                <div className="text-[10px] text-slate-500 uppercase font-semibold">Effect Size (OR)</div>
                                <div className="text-lg font-bold text-white mt-0.5">{metaResults.effect_size}</div>
                              </div>
                              <div className="bg-slate-900/40 border border-slate-850 p-3 rounded-lg">
                                <div className="text-[10px] text-slate-500 uppercase font-semibold">Heterogeneity (I²)</div>
                                <div className="text-lg font-bold text-white mt-0.5">{metaResults.i2}</div>
                              </div>
                              <div className="bg-slate-900/40 border border-slate-850 p-3 rounded-lg">
                                <div className="text-[10px] text-slate-500 uppercase font-semibold">P-Value</div>
                                <div className="text-lg font-bold text-white mt-0.5">&lt; 0.001</div>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
