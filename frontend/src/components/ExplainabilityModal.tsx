import React from 'react';
import { X, CheckCircle, AlertTriangle, ShieldCheck, FileText, ArrowRight, Activity, HelpCircle } from 'lucide-react';
import { RotationStrategy } from '../types';

interface ExplainabilityModalProps {
  strategy: RotationStrategy | null;
  onClose: () => void;
}

export const ExplainabilityModal: React.FC<ExplainabilityModalProps> = ({ strategy, onClose }) => {
  if (!strategy) return null;

  const { explainability, metrics } = strategy;

  const formatItem = (val: any): string => {
    if (typeof val === 'string') return val;
    if (typeof val === 'object' && val !== null) {
      return val.description || val.name || val.text || val.crop_name || JSON.stringify(val);
    }
    return String(val);
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-[#0E1526] border border-[#1F2B48] rounded-2xl max-w-3xl w-full max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Modal Header */}
        <div className="p-5 border-b border-[#1F2B48] flex items-center justify-between bg-[#141D33]/70">
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">
                {strategy.strategy_id}
              </span>
              <h3 className="text-lg font-black text-white">{strategy.name}</h3>
            </div>
            <p className="text-xs text-slate-400 mt-1">{strategy.focus}</p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg bg-[#0E1526] hover:bg-[#1A2642] text-slate-400 hover:text-white border border-[#1F2B48] transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6">
          {/* Confidence Breakdown Card */}
          <div className="bg-[#141D33] p-4 rounded-xl border border-[#1F2B48]">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span className="text-xs font-bold text-white uppercase tracking-wider">
                  Decision Confidence & Data Evidence Quality
                </span>
              </div>
              <span className="text-xs font-mono font-bold text-emerald-400">
                {typeof explainability.confidence_score === 'number' && explainability.confidence_score <= 1.0
                  ? Math.round(explainability.confidence_score * 100)
                  : Math.min(Math.round(explainability.confidence_score || 85), 100)}% Composite Confidence
              </span>
            </div>

            <div className="grid grid-cols-3 gap-3 text-center">
              <div className="bg-[#0E1526] p-2.5 rounded-lg border border-[#1F2B48]">
                <span className="text-[10px] text-slate-400 block">Climate Suitability</span>
                <span className="text-xs font-bold text-cyan-300 truncate block mt-0.5">
                  {metrics.climate_suitability ? 'Validated' : 'Pending'}
                </span>
              </div>
              <div className="bg-[#0E1526] p-2.5 rounded-lg border border-[#1F2B48]">
                <span className="text-[10px] text-slate-400 block">Soil Building Index</span>
                <span className="text-xs font-bold text-emerald-400 block mt-0.5">
                  {metrics.soil_improvement_index} / 100
                </span>
              </div>
              <div className="bg-[#0E1526] p-2.5 rounded-lg border border-[#1F2B48]">
                <span className="text-[10px] text-slate-400 block">Market Liquidity</span>
                <span className="text-xs font-bold text-amber-300 truncate block mt-0.5">
                  {metrics.market_liquidity ? 'High Liquidity' : 'Standard'}
                </span>
              </div>
            </div>
          </div>

          {/* Why Suggested & Supporting Observations */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 mb-2 flex items-center gap-1.5">
              <CheckCircle className="w-4 h-4 text-emerald-400" />
              <span>NASA & USDA Supporting Observations</span>
            </h4>
            <div className="space-y-2">
              {explainability.supporting_observations?.map((obs, idx) => (
                <div
                  key={idx}
                  className="bg-[#141D33]/60 p-3 rounded-lg border border-[#1F2B48] text-xs text-slate-200 leading-relaxed flex items-start space-x-2"
                >
                  <span className="text-emerald-400 font-bold">•</span>
                  <span>{formatItem(obs)}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Expected Agronomic Benefits */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 mb-2 flex items-center gap-1.5">
              <Activity className="w-4 h-4 text-cyan-400" />
              <span>Projected Agronomic & Soil Health Benefits</span>
            </h4>
            <div className="space-y-2">
              {explainability.expected_benefits?.map((ben, idx) => (
                <div
                  key={idx}
                  className="bg-[#141D33]/60 p-3 rounded-lg border border-[#1F2B48] text-xs text-slate-200 leading-relaxed flex items-start space-x-2"
                >
                  <span className="text-cyan-400 font-bold">•</span>
                  <span>{formatItem(ben)}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Inherent Vulnerabilities / Risks */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 mb-2 flex items-center gap-1.5">
              <AlertTriangle className="w-4 h-4 text-amber-400" />
              <span>Identified Agronomic Risks & Stress Vulnerabilities</span>
            </h4>
            <div className="space-y-2">
              {explainability.inherent_risks?.map((risk, idx) => (
                <div
                  key={idx}
                  className="bg-[#141D33]/60 p-3 rounded-lg border border-[#1F2B48] text-xs text-slate-200 leading-relaxed flex items-start space-x-2"
                >
                  <span className="text-amber-400 font-bold">•</span>
                  <span>{formatItem(risk)}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Validation Checklist / Actionable Playbook */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 mb-2 flex items-center gap-1.5">
              <FileText className="w-4 h-4 text-emerald-400" />
              <span>Farmer Actionable Implementation Checklist</span>
            </h4>
            <div className="space-y-2">
              {explainability.validation_checklist?.map((chk, idx) => (
                <div
                  key={idx}
                  className="bg-emerald-950/20 p-3 rounded-lg border border-emerald-500/30 text-xs text-emerald-100/90 leading-relaxed flex items-start space-x-2"
                >
                  <span className="font-mono text-emerald-400 font-bold text-xs">{idx + 1}.</span>
                  <span>{formatItem(chk)}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-[#1F2B48] bg-[#141D33]/50 flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-black transition-colors"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
};
