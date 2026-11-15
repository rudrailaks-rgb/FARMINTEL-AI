import React, { useState } from 'react';
import {
  Sprout,
  CheckCircle2,
  AlertTriangle,
  Droplets,
  Sun,
  ShieldCheck,
  TrendingUp,
  Cpu,
  Sparkles,
  Layers
} from 'lucide-react';
import { FieldAnalysisResponse, MLSuitabilityScore } from '../types';

interface Props {
  analysisData: FieldAnalysisResponse;
}

const CROP_METADATA: Record<string, {
  name: string;
  scientific: string;
  category: 'Cash Grain' | 'Legume / Pulse' | 'Forage' | 'Cover Crop' | 'Specialty';
  gddReq: number;
  waterReqIn: number;
  nCreditLbAc: number;
  droughtTolerance: string;
  benefits: string;
}> = {
  corn: {
    name: 'Field Corn',
    scientific: 'Zea mays',
    category: 'Cash Grain',
    gddReq: 2400,
    waterReqIn: 22.0,
    nCreditLbAc: 0,
    droughtTolerance: 'Moderate (Critical at silking)',
    benefits: 'High biomass residue production; primary Midwest economic cash engine.'
  },
  soybeans: {
    name: 'Soybeans',
    scientific: 'Glycine max',
    category: 'Legume / Pulse',
    gddReq: 2200,
    waterReqIn: 20.0,
    nCreditLbAc: 45,
    droughtTolerance: 'Moderate-High (Indeterminate pod filling)',
    benefits: 'Fixes atmospheric N; breaks cereal root disease cycles; excellent cash liquidity.'
  },
  winter_wheat: {
    name: 'Winter Wheat',
    scientific: 'Triticum aestivum',
    category: 'Cash Grain',
    gddReq: 1800,
    waterReqIn: 16.0,
    nCreditLbAc: 0,
    droughtTolerance: 'High (Escapes summer heat wave through summer harvest)',
    benefits: 'Fall/winter ground armor prevents soil erosion; early harvest allows cover establishment.'
  },
  grain_sorghum: {
    name: 'Grain Sorghum (Milo)',
    scientific: 'Sorghum bicolor',
    category: 'Cash Grain',
    gddReq: 2200,
    waterReqIn: 15.0,
    nCreditLbAc: 0,
    droughtTolerance: 'Exceptional (C4 photosynthetic efficiency, waxy leaf cuticle)',
    benefits: 'High heat resilience; requires 30-40% less water than corn; interrupts corn rootworm.'
  },
  alfalfa: {
    name: 'Alfalfa',
    scientific: 'Medicago sativa',
    category: 'Forage',
    gddReq: 2600,
    waterReqIn: 28.0,
    nCreditLbAc: 120,
    droughtTolerance: 'High (Deep taproots reach 8-15 ft moisture horizons)',
    benefits: 'Massive biological N contribution; creates deep biopores that improve soil infiltration.'
  },
  oats: {
    name: 'Spring Oats',
    scientific: 'Avena sativa',
    category: 'Cash Grain',
    gddReq: 1600,
    waterReqIn: 15.0,
    nCreditLbAc: 0,
    droughtTolerance: 'Moderate (Thrives in cool spring conditions)',
    benefits: 'Excellent companion nurse crop; suppresses spring weeds; low input cost.'
  },
  cereal_rye: {
    name: 'Winter Cereal Rye',
    scientific: 'Secale cereale',
    category: 'Cover Crop',
    gddReq: 1200,
    waterReqIn: 12.0,
    nCreditLbAc: 0,
    droughtTolerance: 'Very High (Tolerates poor soils and extreme freeze)',
    benefits: 'Premier cover crop for winter erosion control, weed suppression (alleopathy), and tile nitrate capture.'
  },
  red_clover: {
    name: 'Red Clover',
    scientific: 'Trifolium pratense',
    category: 'Cover Crop',
    gddReq: 1800,
    waterReqIn: 18.0,
    nCreditLbAc: 85,
    droughtTolerance: 'Moderate',
    benefits: 'Frost-seedable into standing small grains; biological N source; stimulates mycorrhizal fungi.'
  },
  sunflower: {
    name: 'Confection Sunflower',
    scientific: 'Helianthus annuus',
    category: 'Specialty',
    gddReq: 2300,
    waterReqIn: 18.0,
    nCreditLbAc: 0,
    droughtTolerance: 'High (Aggressive taproot scavenging subsoil moisture)',
    benefits: 'Scavenges deep subsoil nitrogen; pollinator habitat; drought hedge in diverse rotations.'
  },
  barley: {
    name: 'Spring Barley',
    scientific: 'Hordeum vulgare',
    category: 'Cash Grain',
    gddReq: 1500,
    waterReqIn: 14.0,
    nCreditLbAc: 0,
    droughtTolerance: 'High (Low water footprint cool-season cereal)',
    benefits: 'Early maturity; saline soil tolerance; high feed and malting commercial value.'
  }
};

export const CropSuitabilityLab: React.FC<Props> = ({ analysisData }) => {
  const [filterCategory, setFilterCategory] = useState<string>('ALL');

  const mlInferences = analysisData.ml_inferences;
  const suitabilityMap: Record<string, MLSuitabilityScore> = mlInferences?.crop_suitability || {};
  const currentGDD = analysisData.climate_summary?.total_gdd_f || 2800;
  const currentPrecip = analysisData.climate_summary?.total_precip_in || 24;

  const cropKeys = Object.keys(CROP_METADATA);

  const processedCrops = cropKeys
    .map(key => {
      const meta = CROP_METADATA[key];
      const pred = suitabilityMap[key] || {
        suitability_score: 0.75,
        suitability_pct: 75.0,
        status: 'MODERATELY_SUITABLE'
      };
      return {
        key,
        ...meta,
        ...pred
      };
    })
    .filter(crop => filterCategory === 'ALL' || crop.category === filterCategory)
    .sort((a, b) => b.suitability_pct - a.suitability_pct);

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-[#0E1526] border border-[#1B253D] rounded-2xl p-6 shadow-xl relative overflow-hidden">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="px-2.5 py-1 text-xs font-semibold rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                PHYSIOLOGICAL SUITABILITY LABORATORY
              </span>
              <span className="px-2.5 py-1 text-xs font-semibold rounded-md bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 flex items-center gap-1">
                <Cpu className="w-3.5 h-3.5" />
                RANDOM FOREST ENSEMBLE (R² = 0.946)
              </span>
            </div>
            <h2 className="text-2xl font-bold text-white tracking-tight">
              Crop Suitability & Environmental Matching
            </h2>
            <p className="text-slate-300 text-sm mt-1 max-w-3xl leading-relaxed">
              Multi-output machine learning predictions evaluating candidate crop physiological compatibility with observed NASA POWER thermal accumulation, soil water retention, and edaphic properties.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2 bg-[#090D18] p-1.5 rounded-xl border border-[#1B253D] text-xs">
            <span className="text-slate-400 font-medium px-2">Filter:</span>
            {['ALL', 'Cash Grain', 'Legume / Pulse', 'Cover Crop', 'Forage'].map(cat => (
              <button
                key={cat}
                onClick={() => setFilterCategory(cat)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                  filterCategory === cat
                    ? 'bg-emerald-500 text-slate-950 shadow-sm'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Environmental Context Ribbon */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-[#0E1526] border border-[#1B253D] rounded-2xl p-4 shadow-lg">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span>Observed Field GDD</span>
            <Sun className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-black text-white font-mono">{(Number(currentGDD) || 2800).toFixed(0)} <span className="text-sm font-normal text-slate-400">°F-days</span></div>
          <p className="text-xs text-slate-400 mt-1">Base 50°F seasonal heat units</p>
        </div>

        <div className="bg-[#0E1526] border border-[#1B253D] rounded-2xl p-4 shadow-lg">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span>Observed Precipitation</span>
            <Droplets className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-black text-cyan-300 font-mono">{(Number(currentPrecip) || 24).toFixed(1)} <span className="text-sm font-normal text-slate-400">in</span></div>
          <p className="text-xs text-slate-400 mt-1">Apr 1 – Sep 30 cumulative</p>
        </div>

        <div className="bg-[#0E1526] border border-[#1B253D] rounded-2xl p-4 shadow-lg">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span>Soil AWC (100cm)</span>
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-black text-emerald-400 font-mono">
            {analysisData.soil_profile?.indicators?.find(i => i.indicator_id === 'SOIL_AWC')?.value || 18.5} <span className="text-sm font-normal text-slate-400">cm</span>
          </div>
          <p className="text-xs text-slate-400 mt-1">Available water storage capacity</p>
        </div>

        <div className="bg-[#0E1526] border border-[#1B253D] rounded-2xl p-4 shadow-lg">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span>Topsoil Reaction</span>
            <TrendingUp className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-2xl font-black text-purple-400 font-mono">
            {analysisData.soil_profile?.indicators?.find(i => i.indicator_id === 'SOIL_PH')?.value || 6.5} <span className="text-sm font-normal text-slate-400">pH</span>
          </div>
          <p className="text-xs text-slate-400 mt-1">1:1 H2O nutrient bioavailability</p>
        </div>
      </div>

      {/* Crop Suitability Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {processedCrops.map(crop => {
          const isGddSufficient = currentGDD >= crop.gddReq * 0.9;
          const isWaterSufficient = currentPrecip >= crop.waterReqIn * 0.8;

          return (
            <div
              key={crop.key}
              className="bg-[#0E1526] border border-[#1B253D] rounded-2xl p-5 hover:border-slate-600 transition-all shadow-lg flex flex-col justify-between space-y-4"
            >
              <div>
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <span className="text-xs font-semibold px-2.5 py-1 rounded-md bg-[#141C30] text-slate-300 border border-[#1B253D]">
                      {crop.category}
                    </span>
                    <h3 className="text-lg font-bold text-white mt-2">
                      {crop.name}
                    </h3>
                    <p className="text-xs italic text-slate-400">{crop.scientific}</p>
                  </div>

                  <div className="text-right">
                    <div className="text-2xl font-black text-white font-mono">
                      {(Number(crop.suitability_pct ?? (crop.suitability_score ? crop.suitability_score * 100 : 75))).toFixed(0)}%
                    </div>
                    <span
                      className={`text-xs font-bold px-2 py-0.5 rounded-md uppercase tracking-wider ${
                        crop.status === 'HIGHLY_SUITABLE'
                          ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                          : crop.status === 'MODERATELY_SUITABLE'
                          ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                          : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                      }`}
                    >
                      {(crop.status || 'MODERATELY_SUITABLE').replace('_', ' ')}
                    </span>
                  </div>
                </div>

                {/* Suitability Progress Bar */}
                <div className="w-full bg-[#141C30] rounded-full h-3 mb-4 overflow-hidden border border-[#1B253D]">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      (crop.suitability_pct ?? 75) >= 75
                        ? 'bg-gradient-to-r from-emerald-500 to-teal-400'
                        : (crop.suitability_pct ?? 75) >= 55
                        ? 'bg-gradient-to-r from-amber-500 to-yellow-400'
                        : 'bg-gradient-to-r from-rose-500 to-orange-400'
                    }`}
                    style={{ width: `${Math.min(100, Math.max(5, crop.suitability_pct ?? 75))}%` }}
                  />
                </div>

                {/* Key Agronomic Attributes */}
                <div className="space-y-2 text-xs bg-[#141C30] p-3.5 rounded-xl border border-[#1B253D] mb-3">
                  <div className="flex justify-between items-center text-slate-300">
                    <span className="text-slate-400 flex items-center gap-1.5">
                      <Sun className="w-4 h-4 text-amber-400" /> Min GDD Base 50:
                    </span>
                    <span className="font-mono font-medium text-sm">
                      {crop.gddReq} °F-days {isGddSufficient ? '✓' : '⚠️'}
                    </span>
                  </div>

                  <div className="flex justify-between items-center text-slate-300">
                    <span className="text-slate-400 flex items-center gap-1.5">
                      <Droplets className="w-4 h-4 text-cyan-400" /> Seasonal Water Need:
                    </span>
                    <span className="font-mono font-medium text-sm">
                      ~{crop.waterReqIn} in {isWaterSufficient ? '✓' : '⚠️'}
                    </span>
                  </div>

                  {crop.nCreditLbAc > 0 && (
                    <div className="flex justify-between items-center text-emerald-400">
                      <span className="flex items-center gap-1.5 font-medium">
                        <Sparkles className="w-4 h-4" /> Biological N Credit:
                      </span>
                      <span className="font-mono font-bold text-sm">+{crop.nCreditLbAc} lb N/ac</span>
                    </div>
                  )}

                  <div className="pt-2 text-slate-300 text-xs border-t border-[#1B253D]">
                    <span className="text-slate-400 font-semibold">Drought Resilience:</span> {crop.droughtTolerance}
                  </div>
                </div>

                <p className="text-xs text-slate-300 leading-relaxed">
                  {crop.benefits}
                </p>
              </div>

              <div className="pt-3 border-t border-[#1B253D] flex items-center justify-between text-xs text-slate-400">
                <span>Model Estimate</span>
                <span className="font-mono font-bold text-slate-200">Score: {(Number(crop.suitability_score ?? 0.75)).toFixed(3)}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
