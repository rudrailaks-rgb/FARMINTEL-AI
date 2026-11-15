import React from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  AreaChart,
  Area
} from 'recharts';
import { Sun, CloudRain, Flame, Activity, Wind } from 'lucide-react';
import { ClimateIndicator, MonthlyRecord } from '../types';

interface ClimateChartsProps {
  indicators: ClimateIndicator[];
  monthly: MonthlyRecord[];
  isFullPage?: boolean;
  era5Data?: any;
}

export const ClimateCharts: React.FC<ClimateChartsProps> = ({ indicators, monthly, isFullPage = false, era5Data }) => {
  const getIndVal = (id: string) => {
    const ind = indicators.find((i) => i.indicator_id === id);
    return ind ? ind.value : 0;
  };

  const gdd = getIndVal('GDD_BASE50');
  const precip = getIndVal('TOTAL_PRECIPITATION');
  const heatDays = getIndVal('HEAT_STRESS_DAYS');
  const et0 = getIndVal('REFERENCE_ET0');
  const waterBal = getIndVal('CLIMATIC_WATER_BALANCE');
  const drySpell = getIndVal('MAX_DRY_SPELL');

  const chartHeight = isFullPage ? 'h-80' : 'h-64';

  return (
    <div className="bg-[#0E1526] rounded-2xl border border-[#1B253D] p-6 shadow-xl space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between pb-4 border-b border-[#1B253D] gap-3">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400">
            <Sun className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white tracking-tight">
              NASA POWER Agroclimatic Intelligence
            </h3>
            <p className="text-xs text-slate-400">
              Solar insolation, thermal heat accumulation (GDD Base 50°F), and hydrologic water balance
            </p>
          </div>
        </div>
        <div className="text-xs text-emerald-400 font-mono bg-emerald-500/10 px-3 py-1 rounded-lg border border-emerald-500/30">
          Daily MERRA-2 Point Reanalysis Feed
        </div>
      </div>

      {/* 6 KPI Metric Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 xl:grid-cols-6 gap-3">
        <div className="bg-[#141C30] p-4 rounded-xl border border-[#1B253D]">
          <div className="text-xs text-slate-400 flex items-center gap-1.5 font-semibold">
            <Sun className="w-4 h-4 text-amber-400 flex-shrink-0" />
            <span>Thermal GDD</span>
          </div>
          <div className="text-2xl font-black text-white mt-1.5 font-mono">
            {typeof gdd === 'number' ? gdd.toFixed(0) : gdd}
          </div>
          <div className="text-xs text-slate-400 mt-1">Base 50°F Units</div>
        </div>

        <div className="bg-[#141C30] p-4 rounded-xl border border-[#1B253D]">
          <div className="text-xs text-slate-400 flex items-center gap-1.5 font-semibold">
            <CloudRain className="w-4 h-4 text-cyan-400 flex-shrink-0" />
            <span>Precipitation</span>
          </div>
          <div className="text-2xl font-black text-cyan-300 mt-1.5 font-mono">
            {typeof precip === 'number' ? precip.toFixed(1) : precip} <span className="text-sm font-normal text-slate-400">in</span>
          </div>
          <div className="text-xs text-slate-400 mt-1">Seasonal Cumulative</div>
        </div>

        <div className="bg-[#141C30] p-4 rounded-xl border border-[#1B253D]">
          <div className="text-xs text-slate-400 flex items-center gap-1.5 font-semibold">
            <Activity className="w-4 h-4 text-emerald-400 flex-shrink-0" />
            <span>Reference ET₀</span>
          </div>
          <div className="text-2xl font-black text-emerald-300 mt-1.5 font-mono">
            {typeof et0 === 'number' ? et0.toFixed(1) : et0} <span className="text-sm font-normal text-slate-400">in</span>
          </div>
          <div className="text-xs text-slate-400 mt-1">Atmospheric Demand</div>
        </div>

        <div className="bg-[#141C30] p-4 rounded-xl border border-[#1B253D]">
          <div className="text-xs text-slate-400 flex items-center gap-1.5 font-semibold">
            <Flame className="w-4 h-4 text-rose-400 flex-shrink-0" />
            <span>Heat Stress</span>
          </div>
          <div className="text-2xl font-black text-rose-300 mt-1.5 font-mono">
            {heatDays} <span className="text-sm font-normal text-slate-400">days</span>
          </div>
          <div className="text-xs text-slate-400 mt-1">Tmax ≥ 35°C (95°F)</div>
        </div>

        <div className="bg-[#141C30] p-4 rounded-xl border border-[#1B253D]">
          <div className="text-xs text-slate-400 flex items-center gap-1.5 font-semibold">
            <CloudRain className="w-4 h-4 text-blue-400 flex-shrink-0" />
            <span>Water Balance</span>
          </div>
          <div className="text-2xl font-black text-blue-300 mt-1.5 font-mono">
            {typeof waterBal === 'number' ? (waterBal > 0 ? `+${waterBal.toFixed(1)}` : waterBal.toFixed(1)) : (waterBal ?? '--')} <span className="text-sm font-normal text-slate-400">in</span>
          </div>
          <div className="text-xs text-slate-400 mt-1">P - ET₀ Balance</div>
        </div>

        <div className="bg-[#141C30] p-4 rounded-xl border border-[#1B253D]">
          <div className="text-xs text-slate-400 flex items-center gap-1.5 font-semibold">
            <Wind className="w-4 h-4 text-amber-300 flex-shrink-0" />
            <span>Max Dry Spell</span>
          </div>
          <div className="text-2xl font-black text-amber-300 mt-1.5 font-mono">
            {drySpell} <span className="text-sm font-normal text-slate-400">days</span>
          </div>
          <div className="text-xs text-slate-400 mt-1">Rain &lt; 1.0mm</div>
        </div>
      </div>

      {/* Real ECMWF ERA5 Multi-Layer Root-Zone Soil Moisture & Temperature Ribbon */}
      {era5Data?.metrics && (
        <div className="bg-[#141C30] p-4 rounded-xl border border-cyan-500/30 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              <Activity className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xs font-bold text-white uppercase tracking-wider">
                  ECMWF ERA5 Reanalysis Soil Moisture Profile
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                  {era5Data.metrics.moisture_status_tier?.replace(/_/g, ' ')}
                </span>
              </div>
              <p className="text-[11px] text-slate-400 mt-0.5">
                Multi-layer volumetric water content ({era5Data.coordinates?.latitude}° N, {era5Data.coordinates?.longitude}° W)
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-6 text-xs font-mono">
            <div>
              <span className="text-slate-400 block text-[10px]">Surface (0-7cm):</span>
              <strong className="text-cyan-300 text-sm">{era5Data.metrics.topsoil_moisture_pct}%</strong>
              <span className="text-slate-500 text-[10px]"> ({era5Data.metrics.topsoil_moisture_volumetric_m3m3} m³/m³)</span>
            </div>
            <div>
              <span className="text-slate-400 block text-[10px]">Root-Zone (28-100cm):</span>
              <strong className="text-emerald-400 text-sm">{era5Data.metrics.rootzone_moisture_pct}%</strong>
              <span className="text-slate-500 text-[10px]"> ({era5Data.metrics.rootzone_moisture_volumetric_m3m3} m³/m³)</span>
            </div>
            <div>
              <span className="text-slate-400 block text-[10px]">Soil Temp (0-7cm):</span>
              <strong className="text-amber-400 text-sm">{era5Data.metrics.mean_soil_temperature_c} °C</strong>
            </div>
          </div>
        </div>
      )}

      {/* Monthly Dual Graphs */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 pt-2">
        {/* Temperature Envelope */}
        <div className="bg-[#141C30] p-5 rounded-xl border border-[#1B253D]">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-bold text-slate-200">
              Monthly Temperature Dynamics (°C)
            </h4>
            <div className="flex items-center space-x-3 text-xs">
              <span className="text-rose-400 font-semibold">• Max</span>
              <span className="text-emerald-400 font-semibold">• Avg</span>
              <span className="text-blue-400 font-semibold">• Min</span>
            </div>
          </div>
          <div className={chartHeight}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={monthly} margin={{ top: 10, right: 15, left: -15, bottom: 5 }}>
                <defs>
                  <linearGradient id="tempGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#F59E0B" stopOpacity={0.35} />
                    <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.05} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F2B48" />
                <XAxis dataKey="month" stroke="#94A3B8" fontSize={11} tickLine={false} />
                <YAxis stroke="#94A3B8" fontSize={11} tickLine={false} unit="°C" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0E1526', borderColor: '#1F2B48', borderRadius: 8, fontSize: 12 }}
                />
                <Area type="monotone" dataKey="max_temp_c" stroke="#EF4444" fillOpacity={1} fill="url(#tempGrad)" name="Max Temp (°C)" />
                <Line type="monotone" dataKey="avg_temp_c" stroke="#10B981" strokeWidth={2.5} dot={{ r: 3 }} name="Avg Temp (°C)" />
                <Line type="monotone" dataKey="min_temp_c" stroke="#3B82F6" strokeWidth={2} dot={{ r: 3 }} name="Min Temp (°C)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Rainfall vs Solar Radiation */}
        <div className="bg-[#141C30] p-5 rounded-xl border border-[#1B253D]">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-bold text-slate-200">
              Rainfall (mm) vs Solar Insolation (MJ/m²/day)
            </h4>
            <div className="flex items-center space-x-3 text-xs">
              <span className="text-cyan-400 font-semibold">■ Rain</span>
              <span className="text-amber-400 font-semibold">• Solar</span>
            </div>
          </div>
          <div className={chartHeight}>
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={monthly} margin={{ top: 10, right: 15, left: -15, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F2B48" />
                <XAxis dataKey="month" stroke="#94A3B8" fontSize={11} tickLine={false} />
                <YAxis yAxisId="left" stroke="#06B6D4" fontSize={11} tickLine={false} unit="mm" />
                <YAxis yAxisId="right" orientation="right" stroke="#F59E0B" fontSize={11} tickLine={false} unit="MJ" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0E1526', borderColor: '#1F2B48', borderRadius: 8, fontSize: 12 }}
                />
                <Bar yAxisId="left" dataKey="rainfall_mm" fill="#06B6D4" radius={[4, 4, 0, 0]} name="Rainfall (mm)" />
                <Line yAxisId="right" type="monotone" dataKey="solar_radiation" stroke="#F59E0B" strokeWidth={2.5} dot={{ r: 3 }} name="Solar (MJ)" />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
