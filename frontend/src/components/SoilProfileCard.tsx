import React from 'react';
import { Layers, Droplets, ShieldAlert, CheckCircle2, Info, AlertTriangle, ShieldCheck } from 'lucide-react';
import { SoilProfileResponse } from '../types';

interface SoilProfileCardProps {
  soil: SoilProfileResponse;
}

export const SoilProfileCard: React.FC<SoilProfileCardProps> = ({ soil }) => {
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-emerald-400 border-emerald-500/40 bg-emerald-500/10';
    if (score >= 65) return 'text-cyan-400 border-cyan-500/40 bg-cyan-500/10';
    if (score >= 50) return 'text-amber-400 border-amber-500/40 bg-amber-500/10';
    return 'text-rose-400 border-rose-500/40 bg-rose-500/10';
  };

  const getInd = (id: string) => soil.indicators?.find((i) => i.indicator_id === id);
  const awc = getInd('SOIL_AWC');
  const om = getInd('SOIL_OM');
  const ph = getInd('SOIL_PH');
  const drainage = getInd('SOIL_DRAINAGE');

  const isFallback =
    (soil as any).is_fallback ||
    (soil.dominant_series && soil.dominant_series.includes('Benchmark')) ||
    (soil.mapunit_name && soil.mapunit_name.includes('Benchmark'));

  return (
    <div className="bg-[#0E1526] rounded-2xl border border-[#1B253D] p-6 shadow-xl space-y-5 h-full flex flex-col justify-between">
      <div className="space-y-5">
        {/* Header */}
        <div className="flex flex-wrap items-center justify-between pb-3.5 border-b border-[#1B253D] gap-3">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400">
              <Layers className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white tracking-tight">
                USDA SSURGO Soil Profile Intelligence
              </h3>
              <p className="text-xs text-slate-400 line-clamp-1">
                {soil.mapunit_name || 'Clarion-Webster Complex'}
              </p>
            </div>
          </div>

          <div
            className={`px-3.5 py-1.5 rounded-xl border font-mono font-bold text-xs flex items-center space-x-2 ${getScoreColor(
              soil.composite_soil_health_score
            )}`}
          >
            <span>Health Rating:</span>
            <span className="text-sm font-black">{soil.composite_soil_health_score} / 100</span>
            <span className="text-xs uppercase font-medium opacity-90">({soil.soil_health_tier})</span>
          </div>
        </div>

        {/* Fallback Banner */}
        {isFallback && (
          <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 text-xs text-amber-300 flex items-start gap-2.5 leading-relaxed">
            <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
            <span>
              <strong>Outside USDA SSURGO Survey Bounds:</strong> Edaphic parameters approximated using regional North American agroclimatic benchmark profile.
            </span>
          </div>
        )}

        {/* Dominant Series & Texture Details */}
        <div className="bg-[#141C30] p-4 rounded-xl border border-[#1B253D] grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">
              Dominant Soil Series
            </span>
            <div className="text-base font-black text-white mt-1">
              {soil.dominant_series || 'Spillville Series'}
            </div>
          </div>
          <div className="sm:text-right">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">
              Texture & Bearing Capacity
            </span>
            <div className="text-sm font-bold text-emerald-400 mt-1">
              {soil.texture || 'Loam / Clay Loam'}
            </div>
          </div>
        </div>

        {/* 4 Profile Edaphic Metrics (2x2 Grid) */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-[#141C30] p-3.5 rounded-xl border border-[#1B253D]">
            <span className="text-xs text-slate-400 block mb-1">Available Water Capacity (AWC)</span>
            <div className="text-lg font-bold text-cyan-300 font-mono">
              {awc ? `${awc.value} ${awc.units}` : '40.2 cm/100cm'}
            </div>
            <span className="text-xs text-slate-500 mt-0.5 block">Profile drought buffer</span>
          </div>

          <div className="bg-[#141C30] p-3.5 rounded-xl border border-[#1B253D]">
            <span className="text-xs text-slate-400 block mb-1">Organic Matter (OM)</span>
            <div className="text-lg font-bold text-emerald-400 font-mono">
              {om ? `${om.value} %` : '4.5 %'}
            </div>
            <span className="text-xs text-slate-500 mt-0.5 block">Native Mollisol fertility</span>
          </div>

          <div className="bg-[#141C30] p-3.5 rounded-xl border border-[#1B253D]">
            <span className="text-xs text-slate-400 block mb-1">Topsoil Reaction (pH 1:1)</span>
            <div className="text-lg font-bold text-amber-300 font-mono">
              {ph ? `${ph.value} pH` : '6.5 pH'}
            </div>
            <span className="text-xs text-slate-500 mt-0.5 block">Nutrient bioavailability</span>
          </div>

          <div className="bg-[#141C30] p-3.5 rounded-xl border border-[#1B253D]">
            <span className="text-xs text-slate-400 block mb-1">Internal Drainage Class</span>
            <div className="text-sm font-bold text-slate-200 truncate mt-0.5">
              {drainage ? drainage.value : 'Moderately well drained'}
            </div>
            <span className="text-xs text-slate-500 mt-0.5 block">Transmission & hazard</span>
          </div>
        </div>
      </div>

      {/* Management Considerations */}
      <div className="bg-[#141C30] p-4 rounded-xl border border-[#1B253D] mt-4">
        <span className="text-xs font-bold text-slate-300 uppercase tracking-wider block mb-2">
          Agronomic Edaphic Considerations
        </span>
        <div className="space-y-1.5">
          {soil.limitations && soil.limitations.length > 0 ? (
            soil.limitations.slice(0, 3).map((lim, idx) => (
              <div key={idx} className="text-xs text-slate-300 flex items-start gap-2 leading-relaxed">
                <span className="text-cyan-400 font-bold">•</span>
                <span>
                  {typeof lim === 'string' ? lim : (lim as any).description || (lim as any).name || JSON.stringify(lim)}
                </span>
              </div>
            ))
          ) : (
            <div className="text-xs text-slate-400 italic">No significant physical or chemical restrictions identified.</div>
          )}
        </div>
      </div>
    </div>
  );
};
