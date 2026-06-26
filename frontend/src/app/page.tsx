import React from 'react';

export default function HomePage() {
  const steps = [
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
          <button className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold rounded-lg shadow-lg shadow-indigo-500/20 transition-all">
            Create Review Project
          </button>
          <button className="px-6 py-3 bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold rounded-lg border border-slate-700 transition-all">
            View Live Demo
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
          {steps.map((item, idx) => (
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
    </div>
  );
}
