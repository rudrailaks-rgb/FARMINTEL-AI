import React from 'react';
import { Sliders, Play, Loader2, Sparkles, Calendar, Layers, ShieldCheck } from 'lucide-react';

interface FieldControlsProps {
  fieldName: string;
  setFieldName: (val: string) => void;
  latitude: number;
  setLatitude: (val: number) => void;
  longitude: number;
  setLongitude: (val: number) => void;
  analysisYear: number;
  setAnalysisYear: (val: number) => void;
  previousCrop: string;
  setPreviousCrop: (val: string) => void;
  farmerPriority: string;
  setFarmerPriority: (val: string) => void;
  onAnalyze: () => void;
  isLoading: boolean;
}

const PREVIOUS_CROPS = [
  { id: 'corn', name: 'Field Corn' },
  { id: 'soybeans', name: 'Soybeans' },
  { id: 'winter_wheat', name: 'Winter Wheat' },
  { id: 'grain_sorghum', name: 'Grain Sorghum' },
  { id: 'alfalfa', name: 'Alfalfa (Perennial)' },
  { id: 'cereal_rye', name: 'Cereal Rye Cover' },
  { id: 'oats', name: 'Spring Oats' },
  { id: 'barley', name: 'Spring Barley' },
];

const PRIORITIES = [
  { id: 'balanced', label: 'Balanced', desc: 'Yield & soil balance' },
  { id: 'economic_profit', label: 'Max Profit', desc: 'Cash returns' },
  { id: 'soil_health', label: 'Soil Health', desc: 'OM & nitrogen' },
  { id: 'climate_resilience', label: 'Resilience', desc: 'Drought hedge' },
];

export const FieldControls: React.FC<FieldControlsProps> = ({
  fieldName,
  setFieldName,
  latitude,
  setLatitude,
  longitude,
  setLongitude,
  analysisYear,
  setAnalysisYear,
  previousCrop,
  setPreviousCrop,
  farmerPriority,
  setFarmerPriority,
  onAnalyze,
  isLoading,
}) => {
  return (
    <div className="bg-[#0E1526] rounded-2xl border border-[#1B253D] p-5 shadow-xl flex flex-col justify-between h-full">
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center space-x-2.5 pb-3 border-b border-[#1B253D]">
          <div className="p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
            <Sliders className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white tracking-tight">
              Field Configuration & Objectives
            </h3>
            <p className="text-xs text-slate-400">
              Define operational parameters for multi-source satellite and soil analysis
            </p>
          </div>
        </div>

        {/* Input Parameters Form */}
        <div className="space-y-3.5">
          {/* Row 1: Field Name and Analysis Year */}
          <div className="grid grid-cols-1 sm:grid-cols-12 gap-3">
            <div className="sm:col-span-8">
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Field Identifier Name
              </label>
              <input
                type="text"
                value={fieldName}
                onChange={(e) => setFieldName(e.target.value)}
                className="w-full bg-[#141C30] border border-[#1B253D] rounded-xl px-3.5 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
                placeholder="e.g. Story Co. Pilot Field"
              />
            </div>

            <div className="sm:col-span-4">
              <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center gap-1">
                <Calendar className="w-3.5 h-3.5 text-cyan-400" />
                NASA Year
              </label>
              <select
                value={analysisYear}
                onChange={(e) => setAnalysisYear(parseInt(e.target.value) || 2024)}
                className="w-full bg-[#141C30] border border-[#1B253D] rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-500 transition-colors"
              >
                <option value={2024}>2024 Season</option>
                <option value={2023}>2023 Season</option>
                <option value={2022}>2022 Season</option>
                <option value={2021}>2021 Season</option>
              </select>
            </div>
          </div>

          {/* Row 2: Latitude and Longitude with Bounds Validation */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1 flex justify-between">
                <span>Latitude (°N / °S)</span>
                <span className="text-[10px] text-slate-400 font-mono">-90 to +90</span>
              </label>
              <input
                type="number"
                step="0.0001"
                min="-90"
                max="90"
                value={latitude}
                onChange={(e) => setLatitude(parseFloat(e.target.value) || 0)}
                className={`w-full bg-[#141C30] border rounded-xl px-3.5 py-2 text-sm font-mono transition-colors focus:outline-none ${
                  latitude < -90 || latitude > 90 || isNaN(latitude)
                    ? 'border-rose-500 text-rose-300 bg-rose-950/20'
                    : 'border-[#1B253D] text-emerald-400 focus:border-cyan-500'
                }`}
              />
              {(latitude < -90 || latitude > 90 || isNaN(latitude)) && (
                <span className="text-[11px] text-rose-400 mt-1 block font-semibold">
                  Must be between -90° and +90°
                </span>
              )}
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1 flex justify-between">
                <span>Longitude (°W / °E)</span>
                <span className="text-[10px] text-slate-400 font-mono">-180 to +180</span>
              </label>
              <input
                type="number"
                step="0.0001"
                min="-180"
                max="180"
                value={longitude}
                onChange={(e) => setLongitude(parseFloat(e.target.value) || 0)}
                className={`w-full bg-[#141C30] border rounded-xl px-3.5 py-2 text-sm font-mono transition-colors focus:outline-none ${
                  longitude < -180 || longitude > 180 || isNaN(longitude)
                    ? 'border-rose-500 text-rose-300 bg-rose-950/20'
                    : 'border-[#1B253D] text-emerald-400 focus:border-cyan-500'
                }`}
              />
              {(longitude < -180 || longitude > 180 || isNaN(longitude)) && (
                <span className="text-[11px] text-rose-400 mt-1 block font-semibold">
                  Must be between -180° and +180° (use '-' for US West)
                </span>
              )}
            </div>
          </div>

          {/* Row 3: Prior Crop */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center gap-1">
              <Layers className="w-3.5 h-3.5 text-emerald-400" />
              Prior Season Crop (Residual Nutrient Base)
            </label>
            <select
              value={previousCrop}
              onChange={(e) => setPreviousCrop(e.target.value)}
              className="w-full bg-[#141C30] border border-[#1B253D] rounded-xl px-3.5 py-2 text-sm text-white focus:outline-none focus:border-cyan-500 transition-colors"
            >
              {PREVIOUS_CROPS.map((crop) => (
                <option key={crop.id} value={crop.id}>
                  {crop.name}
                </option>
              ))}
            </select>
          </div>

          {/* Row 4: Strategic Priority */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center justify-between">
              <span className="flex items-center gap-1">
                <ShieldCheck className="w-3.5 h-3.5 text-purple-400" />
                Strategic Optimization Priority
              </span>
              <span className="text-[11px] text-slate-400 font-mono">Pareto Objective</span>
            </label>

            <div className="grid grid-cols-2 gap-2">
              {PRIORITIES.map((p) => {
                const isSelected = farmerPriority === p.id;
                return (
                  <button
                    key={p.id}
                    type="button"
                    onClick={() => setFarmerPriority(p.id)}
                    className={`p-2.5 rounded-xl border text-left transition-all ${
                      isSelected
                        ? 'bg-purple-500/15 text-white border-purple-500/60 ring-1 ring-purple-500/30'
                        : 'bg-[#141C30] text-slate-300 border-[#1B253D] hover:border-slate-500'
                    }`}
                  >
                    <div className="text-xs font-bold">{p.label}</div>
                    <div className="text-[11px] text-slate-400 leading-tight mt-0.5">{p.desc}</div>
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Primary Action Button */}
      <div className="mt-5 pt-3 border-t border-[#1B253D]">
        <button
          onClick={onAnalyze}
          disabled={isLoading || latitude < -90 || latitude > 90 || longitude < -180 || longitude > 180 || isNaN(latitude) || isNaN(longitude)}
          className="w-full py-3 px-4 rounded-xl text-sm font-bold bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 hover:from-emerald-400 hover:to-cyan-400 text-slate-950 flex items-center justify-center space-x-2 shadow-lg shadow-emerald-500/20 uppercase tracking-wider transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <Loader2 className="w-4 h-4 animate-spin text-slate-950" />
          ) : (
            <Play className="w-4 h-4 fill-slate-950 stroke-none" />
          )}
          <span>
            {latitude < -90 || latitude > 90 || longitude < -180 || longitude > 180 || isNaN(latitude) || isNaN(longitude)
              ? 'Invalid Coordinates (Bounds Exceeded)'
              : isLoading
              ? 'Retrieving NASA & USDA Data...'
              : 'Run Integrated Analysis'}
          </span>
        </button>
      </div>
    </div>
  );
};
