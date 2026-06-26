import React from 'react';
import './globals.css';

export const metadata = {
  title: 'ReviewPilot AI - Evidence Synthesis Copilot',
  description: 'AI-powered Systematic Review Copilot for biomedical researchers.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-950 text-slate-100 font-sans antialiased">
        <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-md sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-xl font-bold bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
                🚀 ReviewPilot AI
              </span>
              <span className="px-2 py-0.5 text-[10px] font-semibold tracking-wider text-indigo-300 bg-indigo-500/10 border border-indigo-500/20 rounded-full uppercase">
                Copilot
              </span>
            </div>
            <nav className="flex items-center gap-6">
              <a href="#" className="text-sm font-medium text-slate-300 hover:text-white transition">Dashboard</a>
              <a href="#" className="text-sm font-medium text-slate-300 hover:text-white transition">Projects</a>
              <a href="#" className="text-sm font-medium text-slate-300 hover:text-white transition">Documentation</a>
            </nav>
          </div>
        </header>
        <main className="max-w-7xl mx-auto px-4 py-8">
          {children}
        </main>
        <footer className="border-t border-slate-900 bg-slate-950 py-8 text-center text-sm text-slate-500">
          <p>© {new Date().getFullYear()} ReviewPilot AI. Designed for modern evidence synthesis.</p>
        </footer>
      </body>
    </html>
  );
}
