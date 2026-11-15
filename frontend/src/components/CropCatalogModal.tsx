import React, { useState } from 'react';
import { X, Search, BookOpen, Sprout, DollarSign, Droplets, Thermometer } from 'lucide-react';
import { CropKnowledge } from '../types';

interface CropCatalogModalProps {
  crops: CropKnowledge[];
  isOpen: boolean;
  onClose: () => void;
}

export const CropCatalogModal: React.FC<CropCatalogModalProps> = ({ crops, isOpen, onClose }) => {
  const [search, setSearch] = useState('');

  if (!isOpen) return null;

  const filtered = crops.filter(
    (c) =>
      c.name.toLowerCase().includes(search.toLowerCase()) ||
      c.category.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-[#0E1526] border border-[#1F2B48] rounded-2xl max-w-5xl w-full max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="p-5 border-b border-[#1F2B48] flex items-center justify-between bg-[#141D33]/70">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-emerald-500/10 rounded-lg text-emerald-400 border border-emerald-500/30">
              <BookOpen className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-black text-white">Agronomic Crop Knowledge Base</h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Biological thresholds, thermal energy demand (GDD), moisture envelopes & economics
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg bg-[#0E1526] hover:bg-[#1A2642] text-slate-400 hover:text-white border border-[#1F2B48] transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Search */}
        <div className="p-4 bg-[#141D33]/40 border-b border-[#1F2B48]">
          <div className="relative w-full sm:w-80">
            <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
            <input
              type="text"
              placeholder="Search crops or categories..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-2 bg-[#0E1526] border border-[#1F2B48] rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
            />
          </div>
        </div>

        {/* Grid Body */}
        <div className="flex-1 overflow-y-auto p-5 grid grid-cols-1 md:grid-cols-2 gap-4">
          {filtered.map((c) => (
            <div
              key={c.id}
              className="bg-[#141D33]/70 rounded-xl border border-[#1F2B48] p-4 flex flex-col justify-between hover:border-emerald-500/40 transition-all"
            >
              <div>
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h4 className="text-base font-bold text-white">{c.name}</h4>
                    <span className="text-[11px] font-medium text-emerald-400 uppercase tracking-wider">
                      {c.category}
                    </span>
                  </div>
                  {c.nitrogen_fixer && (
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                      N-Fixer (Legume)
                    </span>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-2 text-xs my-3">
                  <div className="bg-[#0E1526] p-2 rounded border border-[#1F2B48]">
                    <span className="text-[10px] text-slate-400 block">Optimal GDD:</span>
                    <span className="font-mono text-amber-300 font-bold">{c.optimal_gdd_f} GDD</span>
                  </div>
                  <div className="bg-[#0E1526] p-2 rounded border border-[#1F2B48]">
                    <span className="text-[10px] text-slate-400 block">Water Need:</span>
                    <span className="font-mono text-cyan-300 font-bold">{c.water_requirement_mm} mm</span>
                  </div>
                  <div className="bg-[#0E1526] p-2 rounded border border-[#1F2B48]">
                    <span className="text-[10px] text-slate-400 block">Heat Stress Limit:</span>
                    <span className="font-mono text-rose-300 font-bold">{c.heat_stress_threshold_c}°C</span>
                  </div>
                  <div className="bg-[#0E1526] p-2 rounded border border-[#1F2B48]">
                    <span className="text-[10px] text-slate-400 block">pH Range:</span>
                    <span className="font-mono text-slate-200 font-bold">{c.optimal_ph_min} – {c.optimal_ph_max}</span>
                  </div>
                </div>

                <div className="space-y-1 text-xs text-slate-300">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Root Depth:</span>
                    <span className="font-medium text-slate-200">{c.root_depth_cm} cm</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Erosion Protection:</span>
                    <span className="font-medium text-emerald-400">{c.erosion_protection}</span>
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-[#1F2B48] flex justify-between items-center text-xs">
                <div>
                  <span className="text-[10px] text-slate-400 block">Baseline Yield</span>
                  <span className="font-mono font-bold text-white">
                    {c.average_yield} {c.yield_units}
                  </span>
                </div>
                <div className="text-right">
                  <span className="text-[10px] text-slate-400 block">Est. Gross Revenue</span>
                  <span className="font-mono font-bold text-emerald-400">
                    ${c.gross_revenue_usd_acre} / acre
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-[#1F2B48] bg-[#141D33]/50 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
