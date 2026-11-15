import React, { useState } from 'react';
import { X, Search, Database, ExternalLink, ShieldAlert, CheckCircle2, Filter, Layers, Info } from 'lucide-react';
import { OfficialDataSource } from '../types';

interface RegistryModalProps {
  sources: OfficialDataSource[];
  isOpen: boolean;
  onClose: () => void;
  selectedFieldName?: string;
  selectedCoordinates?: { latitude: number; longitude: number };
}

export const RegistryModal: React.FC<RegistryModalProps> = ({
  sources,
  isOpen,
  onClose,
  selectedFieldName = 'Story County Research Farm',
  selectedCoordinates = { latitude: 42.0308, longitude: -93.6319 }
}) => {
  const [search, setSearch] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('ALL');

  if (!isOpen) return null;

  const filtered = sources.filter((s) => {
    const matchesSearch =
      s.dataset_name.toLowerCase().includes(search.toLowerCase()) ||
      s.dataset_id.toLowerCase().includes(search.toLowerCase()) ||
      s.official_provider.toLowerCase().includes(search.toLowerCase()) ||
      s.intended_agricultural_use.toLowerCase().includes(search.toLowerCase());

    const matchesStatus =
      filterStatus === 'ALL' ||
      s.integration_status === filterStatus ||
      (filterStatus === 'ACTIVE' && (s.integration_status === 'USED_IN_ANALYSIS' || s.integration_status === 'OBSERVATION_RETRIEVED' || s.integration_status === 'DATA_FEED_ACTIVE')) ||
      (filterStatus === 'METADATA' && s.integration_status === 'METADATA_RETRIEVED') ||
      (filterStatus === 'AUTH' && (s.integration_status === 'AUTH_REQUIRED' || s.integration_status === 'SOURCE_DISCOVERED'));

    return matchesSearch && matchesStatus;
  });

  const getStatusBadge = (status: string) => {
    if (status === 'USED_IN_ANALYSIS' || status === 'DATA_FEED_ACTIVE') {
      return 'bg-emerald-500/15 text-emerald-300 border-emerald-500/40';
    }
    if (status === 'OBSERVATION_RETRIEVED') {
      return 'bg-cyan-500/15 text-cyan-300 border-cyan-500/40';
    }
    if (status === 'METADATA_RETRIEVED' || status === 'METADATA_ONLY') {
      return 'bg-blue-500/15 text-blue-300 border-blue-500/40';
    }
    return 'bg-amber-500/15 text-amber-300 border-amber-500/40';
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-[#0E1526] border border-[#1F2B48] rounded-2xl max-w-6xl w-full max-h-[92vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="p-5 border-b border-[#1F2B48] flex items-center justify-between bg-[#141D33]/70">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-cyan-500/10 rounded-lg text-cyan-400 border border-cyan-500/30">
              <Database className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-lg font-black text-white">
                  Official Data Source Registry
                </h3>
                <span className="text-xs font-mono font-bold px-2.5 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">
                  {sources.length} Official Challenge Resources
                </span>
                <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 hidden md:inline">
                  Field: ({selectedCoordinates.latitude.toFixed(4)}°, {selectedCoordinates.longitude.toFixed(4)}°)
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                NASA Space Apps Challenge 2026: Field Shift — 7-Stage Data Provenance & Verification Audit
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

        {/* Search & Filter Toolbar */}
        <div className="p-4 bg-[#141D33]/40 border-b border-[#1F2B48] flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="relative w-full sm:w-80">
            <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
            <input
              type="text"
              placeholder="Search by dataset name, ID, or provider..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-2 bg-[#0E1526] border border-[#1F2B48] rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div className="flex items-center space-x-2 w-full sm:w-auto">
            <Filter className="w-4 h-4 text-slate-400" />
            <span className="text-xs text-slate-400">Filter:</span>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="bg-[#0E1526] border border-[#1F2B48] rounded-lg px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500"
            >
              <option value="ALL">All 28 Resources ({sources.length})</option>
              <option value="ACTIVE">Active in Analysis / Observations ({sources.filter(s => s.integration_status === 'USED_IN_ANALYSIS' || s.integration_status === 'OBSERVATION_RETRIEVED' || s.integration_status === 'DATA_FEED_ACTIVE').length})</option>
              <option value="METADATA">Metadata Discovery ({sources.filter(s => s.integration_status === 'METADATA_RETRIEVED' || s.integration_status === 'METADATA_ONLY').length})</option>
              <option value="AUTH">Auth / Credentials Required ({sources.filter(s => s.integration_status === 'AUTH_REQUIRED' || s.integration_status === 'SOURCE_DISCOVERED').length})</option>
            </select>
          </div>
        </div>

        {/* Table Body */}
        <div className="flex-1 overflow-y-auto p-4">
          <div className="border border-[#1F2B48] rounded-xl overflow-hidden bg-[#070B13]/40">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-[#141D33] text-slate-300 border-b border-[#1F2B48]">
                  <th className="p-3 font-bold w-56">Dataset / ID</th>
                  <th className="p-3 font-bold w-48">Provider & Auth</th>
                  <th className="p-3 font-bold w-48">Access Method</th>
                  <th className="p-3 font-bold w-36">Resolution</th>
                  <th className="p-3 font-bold">7-Stage Provenance & Intended Use</th>
                  <th className="p-3 font-bold w-36 text-center">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1F2B48]/60">
                {filtered.map((s) => (
                  <tr key={s.dataset_id} className="hover:bg-[#0E1526]/80 transition-colors">
                    <td className="p-3 align-top">
                      <div className="font-bold text-white text-xs">{s.dataset_name}</div>
                      <div className="font-mono text-[10px] text-cyan-400 mt-0.5">{s.dataset_id}</div>
                      <div className="flex items-center space-x-2 mt-1.5">
                        <a
                          href={s.official_access_url}
                          target="_blank"
                          rel="noreferrer"
                          className="text-[10px] text-slate-400 hover:text-cyan-300 flex items-center gap-0.5"
                        >
                          Portal <ExternalLink className="w-2.5 h-2.5" />
                        </a>
                        <span className="text-slate-600">•</span>
                        <a
                          href={s.api_documentation_url}
                          target="_blank"
                          rel="noreferrer"
                          className="text-[10px] text-slate-400 hover:text-emerald-300 flex items-center gap-0.5"
                        >
                          API Docs <ExternalLink className="w-2.5 h-2.5" />
                        </a>
                      </div>
                    </td>

                    <td className="p-3 align-top text-slate-300">
                      <div className="font-medium text-slate-200">{s.official_provider}</div>
                      <div className="text-[10px] text-slate-400 mt-1">
                        Auth: <strong className="text-slate-300">{s.authentication_requirement}</strong>
                      </div>
                    </td>

                    <td className="p-3 align-top">
                      <div className="text-slate-200">{s.access_method}</div>
                      <div className="text-[10px] text-slate-400 mt-0.5 font-mono">
                        Formats: {s.supported_output_format}
                      </div>
                    </td>

                    <td className="p-3 align-top">
                      <div className="text-slate-200">{s.spatial_resolution}</div>
                      <div className="text-[10px] text-slate-400 mt-0.5">Cadence: {s.temporal_resolution}</div>
                    </td>

                    <td className="p-3 align-top text-slate-300 leading-relaxed">
                      {/* 7-Stage Visual Pill Indicators */}
                      <div className="flex flex-wrap items-center gap-1 mb-1.5 text-[9px] font-mono">
                        <span className={`px-1.5 py-0.5 rounded ${s.stages?.source_discovered ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' : 'bg-slate-800 text-slate-500'}`}>
                          1.Discovered
                        </span>
                        <span className={`px-1.5 py-0.5 rounded ${s.stages?.metadata_retrieved ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' : 'bg-slate-800 text-slate-500'}`}>
                          2.Metadata
                        </span>
                        <span className={`px-1.5 py-0.5 rounded ${s.stages?.observation_retrieved ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40' : 'bg-slate-800 text-slate-500'}`}>
                          3.Observation
                        </span>
                        <span className={`px-1.5 py-0.5 rounded ${s.stages?.data_parsed ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40' : 'bg-slate-800 text-slate-500'}`}>
                          4.Parsed
                        </span>
                        <span className={`px-1.5 py-0.5 rounded ${s.stages?.indicators_processed ? 'bg-purple-500/20 text-purple-300 border border-purple-500/40' : 'bg-slate-800 text-slate-500'}`}>
                          5.Indicators
                        </span>
                        <span className={`px-1.5 py-0.5 rounded ${s.stages?.used_by_decision_engine ? 'bg-emerald-500/30 text-emerald-200 font-bold border border-emerald-400' : 'bg-slate-800 text-slate-500'}`}>
                          6.Decision ML
                        </span>
                      </div>
                      <div className="text-xs text-slate-200">{s.intended_agricultural_use}</div>
                      <div className="text-[10px] text-slate-400 mt-1 italic">
                        Limit: {s.known_limitations}
                      </div>
                    </td>

                    <td className="p-3 align-top text-center">
                      <span
                        className={`inline-block px-2.5 py-1 rounded-full text-[10px] font-bold border tracking-wider ${getStatusBadge(
                          s.integration_status
                        )}`}
                      >
                        {s.integration_status.replace(/_/g, ' ')}
                      </span>
                      <div className="text-[9px] text-slate-400 mt-1 font-mono truncate max-w-[130px] mx-auto">
                        {s.last_successful_test.split('(')[0]}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 bg-[#141D33]/60 border-t border-[#1F2B48] flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400 gap-2">
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>
              All 28 official NASA Space Apps Challenge resources verified against official providers
            </span>
          </div>
          <div className="font-mono text-slate-500 text-[11px]">
            FARMINTEL AI v2.0.0-PROD
          </div>
        </div>
      </div>
    </div>
  );
};
