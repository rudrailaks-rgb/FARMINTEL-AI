import React, { useState } from 'react';
import {
  ShieldAlert,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  Info,
  Layers,
  FileText,
  Activity,
  Compass,
  ArrowRight
} from 'lucide-react';
import { FieldAnalysisResponse, RotationStrategy, formatConfidence } from '../types';

interface Props {
  analysisData: FieldAnalysisResponse;
  onSelectStrategy?: (strategy: RotationStrategy) => void;
}

export const EvidenceExplainabilityView: React.FC<Props> = ({ analysisData, onSelectStrategy }) => {
  const strategies = analysisData.rotation_decision_engine?.strategies;
  const [selectedKey, setSelectedKey] = useState<'strategy_a' | 'strategy_b' | 'strategy_c'>('strategy_b');

  const currentStrat = strategies ? strategies[selectedKey] : null;

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-[#0E1526] border border-[#1B253D] rounded-2xl p-6 shadow-xl relative overflow-hidden">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="px-2.5 py-1 text-xs font-semibold rounded-md bg-purple-500/10 text-purple-400 border border-purple-500/20">
                AUDITABLE DECISION LOG
              </span>
              <span className="px-2.5 py-1 text-xs font-semibold rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" />
                EXPLAINABLE AI ENGINE
              </span>
            </div>
            <h2 className="text-2xl font-bold text-white tracking-tight">
              Evidence Tracing & Decision Explainability
            </h2>
            <p className="text-slate-300 text-sm mt-1 max-w-3xl leading-relaxed">
              Transparent, evidence-based reasoning connecting empirical NASA satellite data, USDA SSURGO soil characteristics, and machine learning models to concrete rotational decisions.
            </p>
          </div>

          {/* Strategy Selector Tabs */}
          <div className="flex gap-2 bg-[#090D18] p-1.5 rounded-xl border border-[#1B253D]">
            {(['strategy_a', 'strategy_b', 'strategy_c'] as const).map(key => {
              const isSelected = selectedKey === key;
              return (
                <button
                  key={key}
                  onClick={() => setSelectedKey(key)}
                  className={`px-3.5 py-2 rounded-lg text-xs font-bold transition-all ${
                    isSelected
                      ? 'bg-purple-600 text-white shadow-md'
                      : 'text-slate-400 hover:text-white hover:bg-slate-800'
                  }`}
                >
                  {key === 'strategy_a' ? 'Strategy A (Cash)' : key === 'strategy_b' ? 'Strategy B (Soil)' : 'Strategy C (Climate)'}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Data Provenance Tier Architecture */}
      <div className="bg-[#0E1526] border border-[#1B253D] rounded-2xl p-6 shadow-xl">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
          <Layers className="w-4 h-4 text-purple-400" />
          Rigorous 5-Tier Data Provenance Architecture
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3.5 text-xs">
          <div className="bg-[#141C30] p-4 rounded-xl border border-[#1B253D]">
            <span className="font-mono text-xs text-emerald-400 font-bold block mb-1">
              [LIVE_SOURCE_DATA]
            </span>
            <p className="text-slate-200 font-bold text-sm">NASA POWER & SSURGO</p>
            <p className="text-xs text-slate-400 mt-1 leading-relaxed">
              Real-time point agroclimatology & official soil mapunit polygons.
            </p>
          </div>

          <div className="bg-[#141C30] p-4 rounded-xl border border-[#1B253D]">
            <span className="font-mono text-xs text-cyan-400 font-bold block mb-1">
              [HISTORICAL_SOURCE_DATA]
            </span>
            <p className="text-slate-200 font-bold text-sm">NASA CMR & USDA NASS</p>
            <p className="text-xs text-slate-400 mt-1 leading-relaxed">
              Landsat/MODIS granules & 7-year county yield statistics.
            </p>
          </div>

          <div className="bg-[#141C30] p-4 rounded-xl border border-[#1B253D]">
            <span className="font-mono text-xs text-amber-400 font-bold block mb-1">
              [DERIVED_INDICATOR]
            </span>
            <p className="text-slate-200 font-bold text-sm">Agroclimatic Indices</p>
            <p className="text-xs text-slate-400 mt-1 leading-relaxed">
              GDD thermal summation, Hargreaves ET0, and water balance.
            </p>
          </div>

          <div className="bg-[#141C30] p-4 rounded-xl border border-[#1B253D]">
            <span className="font-mono text-xs text-purple-400 font-bold block mb-1">
              [MODEL_ESTIMATE]
            </span>
            <p className="text-slate-200 font-bold text-sm">ML Ensembles</p>
            <p className="text-xs text-slate-400 mt-1 leading-relaxed">
              Random Forest suitability ($R^2=0.946$) & GB risk/yield models.
            </p>
          </div>

          <div className="bg-[#141C30] p-4 rounded-xl border border-[#1B253D]">
            <span className="font-mono text-xs text-slate-400 font-bold block mb-1">
              [USER_INPUT]
            </span>
            <p className="text-slate-200 font-bold text-sm">Field Configuration</p>
            <p className="text-xs text-slate-400 mt-1 leading-relaxed">
              Farmer coordinates, prior crop, and strategic priority.
            </p>
          </div>
        </div>
      </div>

      {/* Selected Strategy Deep Evidence */}
      {currentStrat && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: Core Reasoning & Sequence */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-[#0E1526] border border-[#1B253D] rounded-2xl p-6 shadow-xl space-y-5">
              <div className="flex items-center justify-between pb-3 border-b border-[#1B253D]">
                <div>
                  <span className="text-xs font-mono text-purple-400 font-semibold">{currentStrat.strategy_id}</span>
                  <h3 className="text-xl font-bold text-white mt-1">{currentStrat.name}</h3>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-black text-emerald-400 font-mono">
                    {formatConfidence(currentStrat.explainability?.confidence_score)}
                  </div>
                  <div className="text-xs text-slate-400 uppercase font-semibold">Calibrated Confidence</div>
                </div>
              </div>

              {/* Year by Year Sequence */}
              <div>
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2.5">
                  Optimized Dynamic Multi-Year Sequence
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {currentStrat.rotation_sequence.map((item: any, idx: number) => {
                    const yr = typeof item === 'object' ? item.year : idx + 1;
                    const cropName = typeof item === 'object' ? item.crop_name : item;
                    const season = typeof item === 'object' ? item.season : 'Full Season';
                    return (
                      <div key={idx} className="bg-[#141C30] p-4 rounded-xl border border-[#1B253D]">
                        <div className="text-xs font-mono text-purple-400 font-bold">Phase {yr} (Year {yr})</div>
                        <div className="text-sm font-bold text-white mt-1">{cropName}</div>
                        <div className="text-xs text-slate-400 mt-0.5">{season}</div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Why Suggested */}
              <div className="space-y-4">
                <div>
                  <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                    <Info className="w-4 h-4 text-cyan-400" /> Agronomic Rationalization
                  </h4>
                  <p className="text-sm text-slate-300 bg-[#141C30] p-4 rounded-xl border border-[#1B253D] leading-relaxed">
                    {currentStrat.explainability?.why_suggested}
                  </p>
                </div>

                {/* Supporting Observations */}
                <div>
                  <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Empirical Supporting Observations
                  </h4>
                  <ul className="space-y-2 bg-[#141C30] p-4 rounded-xl border border-[#1B253D] text-xs text-slate-300">
                    {currentStrat.explainability?.supporting_observations?.map((obs, i) => (
                      <li key={i} className="flex items-start gap-2.5">
                        <span className="text-emerald-400 font-bold mt-0.5">•</span>
                        <span>{obs}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Expected Benefits */}
                <div>
                  <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                    <Activity className="w-4 h-4 text-purple-400" /> Projected Agronomic Benefits
                  </h4>
                  <ul className="space-y-2 bg-[#141C30] p-4 rounded-xl border border-[#1B253D] text-xs text-slate-300">
                    {currentStrat.explainability?.expected_benefits?.map((ben, i) => (
                      <li key={i} className="flex items-start gap-2.5">
                        <span className="text-purple-400 font-bold mt-0.5">•</span>
                        <span>{ben}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column: Inherent Risks, Missing Info, Checklist */}
          <div className="space-y-6">
            {/* Inherent Risks */}
            <div className="bg-[#0E1526] border border-[#1B253D] rounded-2xl p-5 shadow-xl">
              <h4 className="text-xs font-bold text-amber-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-400" /> Inherent Agronomic Risks
              </h4>
              <ul className="space-y-2.5 text-xs text-slate-300">
                {currentStrat.explainability?.inherent_risks?.map((risk, i) => (
                  <li key={i} className="p-3 bg-amber-500/5 rounded-xl border border-amber-500/20 flex items-start gap-2.5 leading-relaxed">
                    <span className="text-amber-400 font-bold mt-0.5">•</span>
                    <span>{risk}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Missing Information Disclosures */}
            <div className="bg-[#0E1526] border border-[#1B253D] rounded-2xl p-5 shadow-xl">
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                <Info className="w-4 h-4 text-slate-400" /> Honest Missing Information Disclosures
              </h4>
              <ul className="space-y-2 text-xs text-slate-300">
                {currentStrat.explainability?.missing_information?.map((miss, i) => (
                  <li key={i} className="p-3 bg-[#141C30] rounded-xl border border-[#1B253D] flex items-start gap-2.5 leading-relaxed">
                    <span className="text-slate-400 font-bold mt-0.5">•</span>
                    <span>{miss}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Farmer Validation Checklist */}
            <div className="bg-[#0E1526] border border-[#1B253D] rounded-2xl p-5 shadow-xl">
              <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Farmer Implementation Checklist
              </h4>
              <div className="space-y-2 text-xs">
                {currentStrat.explainability?.validation_checklist?.map((check, i) => (
                  <div key={i} className="p-3 bg-emerald-500/5 rounded-xl border border-emerald-500/20 text-slate-200 flex items-start gap-2.5 leading-relaxed">
                    <span className="text-emerald-400 font-bold font-mono">[{i + 1}]</span>
                    <span>{check}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
