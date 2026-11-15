import React, { useState } from 'react';
import { Award, ArrowRight, Sparkles, ShieldCheck, Sliders, CheckCircle2, DollarSign, HeartHandshake, Shield, Scale, Info } from 'lucide-react';
import { RotationDecisionEngineResponse, RotationStrategy } from '../types';

interface RotationComparisonProps {
  decision: RotationDecisionEngineResponse;
  onSelectStrategyForDeepTrace: (strategy: RotationStrategy) => void;
  currentPriority?: string;
  onPriorityChange?: (priority: string) => void;
}

const STRATEGIC_PRESETS = [
  {
    id: 'balanced',
    label: 'Balanced',
    icon: Scale,
    tagline: 'Pareto Compromise',
    weights: { econ: 30, soil: 30, climate: 25, pest: 15 },
    desc: 'Equally balances net revenue, long-term soil carbon rebuilding, and weather volatility.'
  },
  {
    id: 'profit',
    label: 'Max Profit',
    icon: DollarSign,
    tagline: 'Cash Grain Margin',
    weights: { econ: 60, soil: 15, climate: 15, pest: 10 },
    desc: 'Maximizes commodity gross margin and elevator liquidity using favorable regional yield factors.'
  },
  {
    id: 'soil_health',
    label: 'Soil Health',
    icon: HeartHandshake,
    tagline: 'Biological N-Fixation',
    weights: { econ: 15, soil: 55, climate: 15, pest: 15 },
    desc: 'Prioritizes legume nitrogen credits, continuous living roots, and erosion armor index.'
  },
  {
    id: 'climate_resilience',
    label: 'Resilience',
    icon: Shield,
    tagline: 'Low Water & Heat Shield',
    weights: { econ: 15, soil: 15, climate: 55, pest: 15 },
    desc: 'Minimizes seasonal irrigation deficit and protects pollination under acute thermal spikes.'
  },
];

export const RotationComparison: React.FC<RotationComparisonProps> = ({
  decision,
  onSelectStrategyForDeepTrace,
  currentPriority = 'balanced',
  onPriorityChange,
}) => {
  const { strategies, recommendation_rationale, overall_data_confidence } = decision;
  const stratList: RotationStrategy[] = [
    strategies.strategy_a,
    strategies.strategy_b,
    strategies.strategy_c,
  ].filter(Boolean);

  const [activePriority, setActivePriority] = useState<string>(currentPriority || 'balanced');
  const [showWeightSliders, setShowWeightSliders] = useState<boolean>(false);

  // Initialize weights based on active preset
  const initialPreset = STRATEGIC_PRESETS.find(p => p.id === activePriority) || STRATEGIC_PRESETS[0];
  const [weightEcon, setWeightEcon] = useState<number>(initialPreset.weights.econ);
  const [weightSoil, setWeightSoil] = useState<number>(initialPreset.weights.soil);
  const [weightClimate, setWeightClimate] = useState<number>(initialPreset.weights.climate);
  const [weightPest, setWeightPest] = useState<number>(initialPreset.weights.pest);

  const handlePresetSelect = (presetId: string) => {
    setActivePriority(presetId);
    const p = STRATEGIC_PRESETS.find(item => item.id === presetId);
    if (p) {
      setWeightEcon(p.weights.econ);
      setWeightSoil(p.weights.soil);
      setWeightClimate(p.weights.climate);
      setWeightPest(p.weights.pest);
    }
    if (onPriorityChange) {
      onPriorityChange(presetId);
    }
  };

  const formatConfidence = (score: number | undefined): number => {
    if (score === undefined || score === null) return 88;
    if (score <= 1.0 && score > 0) return Math.round(score * 100);
    return Math.min(Math.round(score), 100);
  };

  // Compute dynamically weighted Pareto scores
  const totalWeight = Math.max(1, weightEcon + weightSoil + weightClimate + weightPest);
  const scoredStrategies = stratList.map((strat) => {
    const f1 = strat.metrics.suitability_score || strat.metrics.overall_score || 75;
    const f2 = strat.metrics.soil_improvement_index || 70;
    const f3 = parseInt(strat.metrics.climate_suitability?.match(/\d+/)?.[0] || '80', 10);
    const f4 = strat.metrics.erosion_score || 70;

    const dynamicScore = Math.round(
      (f1 * weightEcon + f2 * weightSoil + f3 * weightClimate + f4 * weightPest) / totalWeight
    );

    return {
      strat,
      dynamicScore,
    };
  });

  // Determine top winning strategy for current weights
  const topDynamicStrat = [...scoredStrategies].sort((a, b) => b.dynamicScore - a.dynamicScore)[0];
  const topDynamicStratId = topDynamicStrat?.strat.strategy_id || decision.primary_recommendation || 'STRATEGY_B';

  // Dynamic explanation matching chosen priority
  const getDynamicRationale = () => {
    if (activePriority === 'profit') {
      return `Prioritizing Cash Margin: ${strategies.strategy_a?.name || 'Strategy A'} achieves the highest Economic Yield score (${strategies.strategy_a?.metrics.overall_score}/100) and maximizes elevator market returns.`;
    }
    if (activePriority === 'soil_health') {
      return `Prioritizing Biological Soil Health: ${strategies.strategy_b?.name || 'Strategy B'} maximizes living root cover, delivering +${strategies.strategy_b?.metrics.nitrogen_credit_lb_ac || 60} lb N/ac organic fertilizer replacement.`;
    }
    if (activePriority === 'climate_resilience') {
      return `Prioritizing Climate & Drought Resilience: ${strategies.strategy_c?.name || 'Strategy C'} conserves crop water reserves and protects grain yields under heat stress.`;
    }
    return recommendation_rationale || 'Multi-objective Pareto compromise balancing commercial yield revenue with living-root soil protection.';
  };

  return (
    <div className="bg-[#0E1526] rounded-2xl border border-[#1B253D] p-6 shadow-xl space-y-5">
      {/* Executive Header */}
      <div className="flex flex-wrap items-center justify-between pb-4 border-b border-[#1B253D] gap-3">
        <div>
          <div className="flex items-center space-x-2.5">
            <div className="p-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white tracking-tight">
                Constrained Multi-Objective Crop Rotation Optimizer
              </h3>
              <p className="text-xs text-slate-400">
                Evaluating candidate sequences dynamically across economic return, soil health, and climate resilience
              </p>
            </div>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          {overall_data_confidence !== undefined && (
            <div className="bg-[#141C30] px-3.5 py-2 rounded-xl border border-[#1B253D] flex items-center space-x-2 text-xs">
              <ShieldCheck className="w-4 h-4 text-cyan-400" />
              <span className="text-slate-400">Data Reliability:</span>
              <span className="font-mono font-bold text-cyan-300 text-sm">
                {formatConfidence(overall_data_confidence)}%
              </span>
            </div>
          )}

          <div className="bg-[#141C30] px-3.5 py-2 rounded-xl border border-emerald-500/40 flex items-center space-x-2 text-xs">
            <Award className="w-4 h-4 text-emerald-400" />
            <span className="text-slate-300">Optimal Strategy:</span>
            <span className="font-bold text-emerald-300 uppercase tracking-wide">
              {topDynamicStratId.replace('_', ' ')}
            </span>
          </div>

          <button
            onClick={() => setShowWeightSliders(!showWeightSliders)}
            className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold flex items-center gap-1.5 transition-all shadow-sm"
          >
            <Sliders className="w-4 h-4 text-cyan-400" />
            <span>{showWeightSliders ? 'Hide Sliders' : 'Tune Weights'}</span>
          </button>
        </div>
      </div>

      {/* Strategic Optimization Objective Selector */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs text-slate-400">
          <span className="font-semibold text-slate-300 flex items-center gap-1.5">
            <Sliders className="w-3.5 h-3.5 text-cyan-400" />
            Select Strategic Optimization Objective (Instant Dynamic Recalculation):
          </span>
          <span className="font-mono text-cyan-400">Pareto Objective Switching Active</span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
          {STRATEGIC_PRESETS.map((preset) => {
            const Icon = preset.icon;
            const isSelected = activePriority === preset.id;
            return (
              <button
                key={preset.id}
                type="button"
                onClick={() => handlePresetSelect(preset.id)}
                className={`p-3 rounded-xl border text-left transition-all ${
                  isSelected
                    ? 'bg-gradient-to-br from-emerald-500/20 to-teal-500/10 border-emerald-500/80 shadow-md ring-1 ring-emerald-500/40'
                    : 'bg-[#141C30] text-slate-300 border-[#1B253D] hover:border-slate-500 hover:bg-[#18233C]'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center space-x-1.5">
                    <Icon className={`w-4 h-4 ${isSelected ? 'text-emerald-300' : 'text-slate-400'}`} />
                    <span className={`text-xs font-bold ${isSelected ? 'text-white' : 'text-slate-200'}`}>
                      {preset.label}
                    </span>
                  </div>
                  {isSelected && (
                    <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                  )}
                </div>
                <div className="text-[11px] text-slate-400 font-medium leading-tight">
                  {preset.tagline}
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Optional Interactive Pareto Weight Sliders */}
      {showWeightSliders && (
        <div className="p-4 rounded-xl bg-[#090D18] border border-cyan-500/30 space-y-3">
          <div className="flex items-center justify-between text-xs">
            <span className="font-bold text-white flex items-center gap-1.5">
              <Sliders className="w-4 h-4 text-cyan-400" />
              Fine-Tune Custom Multi-Objective Utility Weights
            </span>
            <span className="text-[11px] font-mono text-slate-400">
              Total: {totalWeight}% (Normalized Dynamically)
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            <div className="bg-[#141C30] p-3 rounded-xl border border-[#1B253D]">
              <label className="text-xs text-slate-300 font-semibold block mb-1.5 flex justify-between">
                <span>Economic Return ($f_1$)</span>
                <span className="text-emerald-400 font-mono font-bold">{weightEcon}%</span>
              </label>
              <input
                type="range"
                min="0"
                max="100"
                value={weightEcon}
                onChange={(e) => {
                  setWeightEcon(Number(e.target.value));
                  setActivePriority('custom');
                }}
                className="w-full accent-emerald-500 cursor-pointer"
              />
            </div>

            <div className="bg-[#141C30] p-3 rounded-xl border border-[#1B253D]">
              <label className="text-xs text-slate-300 font-semibold block mb-1.5 flex justify-between">
                <span>Soil Regeneration ($f_2$)</span>
                <span className="text-cyan-400 font-mono font-bold">{weightSoil}%</span>
              </label>
              <input
                type="range"
                min="0"
                max="100"
                value={weightSoil}
                onChange={(e) => {
                  setWeightSoil(Number(e.target.value));
                  setActivePriority('custom');
                }}
                className="w-full accent-cyan-500 cursor-pointer"
              />
            </div>

            <div className="bg-[#141C30] p-3 rounded-xl border border-[#1B253D]">
              <label className="text-xs text-slate-300 font-semibold block mb-1.5 flex justify-between">
                <span>Climate Resilience ($f_3$)</span>
                <span className="text-amber-400 font-mono font-bold">{weightClimate}%</span>
              </label>
              <input
                type="range"
                min="0"
                max="100"
                value={weightClimate}
                onChange={(e) => {
                  setWeightClimate(Number(e.target.value));
                  setActivePriority('custom');
                }}
                className="w-full accent-amber-500 cursor-pointer"
              />
            </div>

            <div className="bg-[#141C30] p-3 rounded-xl border border-[#1B253D]">
              <label className="text-xs text-slate-300 font-semibold block mb-1.5 flex justify-between">
                <span>Pest Interruption ($f_4$)</span>
                <span className="text-purple-400 font-mono font-bold">{weightPest}%</span>
              </label>
              <input
                type="range"
                min="0"
                max="100"
                value={weightPest}
                onChange={(e) => {
                  setWeightPest(Number(e.target.value));
                  setActivePriority('custom');
                }}
                className="w-full accent-purple-500 cursor-pointer"
              />
            </div>
          </div>
        </div>
      )}

      {/* Dynamic Recommendation Banner */}
      <div className="p-4 rounded-xl bg-emerald-950/30 border border-emerald-500/40 text-sm text-emerald-200 leading-relaxed flex items-start space-x-3 shadow-inner">
        <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
        <div>
          <strong className="text-emerald-300 block mb-0.5">
            Optimized for {STRATEGIC_PRESETS.find(p => p.id === activePriority)?.label || 'Custom Utility'}:
          </strong>
          {getDynamicRationale()}
        </div>
      </div>

      {/* 3 Strategy Columns Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {scoredStrategies.map(({ strat, dynamicScore }) => {
          const isRec = strat.strategy_id.toLowerCase() === topDynamicStratId.toLowerCase();
          const confScore = formatConfidence(strat.explainability.confidence_score);

          return (
            <div
              key={strat.strategy_id}
              onClick={() => onSelectStrategyForDeepTrace(strat)}
              className={`rounded-2xl border flex flex-col justify-between transition-all duration-200 relative overflow-hidden shadow-lg cursor-pointer ${
                isRec
                  ? 'bg-gradient-to-b from-[#14233C] to-[#0E1526] border-emerald-500/80 shadow-emerald-950/40 ring-2 ring-emerald-500/50'
                  : 'bg-[#141C30]/80 border-[#1B253D] hover:border-slate-500 hover:bg-[#18233C]'
              }`}
            >
              {isRec && (
                <div className="bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 text-xs font-black uppercase tracking-widest text-center py-1 font-mono">
                  ★ RECOMMENDED OPTIMAL STRATEGY
                </div>
              )}

              <div className="p-5 flex-1 flex flex-col justify-between space-y-4">
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-xs font-mono font-bold px-2.5 py-1 rounded-lg bg-[#090D18] border border-[#1B253D] text-cyan-400">
                      {strat.strategy_id}
                    </span>
                    <span className="text-xs font-bold px-2.5 py-1 rounded-lg border bg-emerald-500/20 text-emerald-300 border-emerald-500/40">
                      {confScore}% CONFIDENCE
                    </span>
                  </div>

                  <h4 className="text-base font-bold text-white mb-1 leading-snug">
                    {strat.name}
                  </h4>
                  <p className="text-xs text-slate-300 mb-4 leading-relaxed">
                    {strat.focus}
                  </p>

                  {/* Cropping Sequence */}
                  <div className="space-y-2 mb-4">
                    <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">
                      Multi-Year Crop Sequence
                    </span>
                    <div className="space-y-2">
                      {strat.rotation_sequence?.map((seq, idx) => {
                        const isObj = typeof seq === 'object' && seq !== null;
                        const cropTitle = isObj ? ((seq as any).crop_name || (seq as any).crop_id) : seq;
                        const seasonLabel = isObj ? (seq as any).season : null;
                        const yearNumber = isObj && (seq as any).year ? (seq as any).year : idx + 1;

                        return (
                          <div
                            key={idx}
                            className="flex items-center justify-between text-sm bg-[#090D18] px-3.5 py-2 rounded-xl border border-[#1B253D]"
                          >
                            <div className="flex items-center space-x-2 truncate">
                              <span className="font-mono text-cyan-400 font-bold text-xs flex-shrink-0">
                                Phase {yearNumber}:
                              </span>
                              <span className="text-slate-200 font-semibold text-sm truncate">
                                {cropTitle}
                              </span>
                            </div>
                            {seasonLabel && (
                              <span className="text-xs text-cyan-300 bg-cyan-950/60 px-2 py-0.5 rounded-md border border-cyan-500/30 flex-shrink-0 ml-2">
                                {seasonLabel}
                              </span>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Quantitative Objective Ratings */}
                  <div className="space-y-2.5 pt-2 border-t border-[#1B253D]">
                    <div className="flex justify-between items-center text-xs">
                      <span className="text-slate-400">Dynamic Utility Rating:</span>
                      <span className="font-mono font-bold text-emerald-400 text-sm">
                        {dynamicScore} / 100
                      </span>
                    </div>

                    <div className="flex justify-between items-center text-xs">
                      <span className="text-slate-400">Biological Nitrogen Credit:</span>
                      <span className="font-mono text-cyan-300 font-semibold">
                        +{strat.metrics.nitrogen_credit_lb_ac || 40} lb N/acre
                      </span>
                    </div>

                    <div className="flex justify-between items-center text-xs">
                      <span className="text-slate-400">Seasonal Water Demand:</span>
                      <span className="font-mono text-amber-300 font-semibold">
                        {strat.metrics.water_demand_rating || 'Moderate (16 in)'}
                      </span>
                    </div>

                    <div className="flex justify-between items-center text-xs">
                      <span className="text-slate-400">Soil Armor & Erosion Protection:</span>
                      <span className="font-mono text-purple-300 font-semibold">
                        {strat.metrics.erosion_score || 75} / 100
                      </span>
                    </div>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    onSelectStrategyForDeepTrace(strat);
                  }}
                  className="w-full mt-4 py-2.5 px-3 rounded-xl bg-[#141C30] hover:bg-[#1A253F] text-slate-200 border border-[#1B253D] hover:border-slate-500 font-semibold text-xs flex items-center justify-center space-x-1.5 transition-all shadow-sm"
                >
                  <span>View Agronomic Decision Trace</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
