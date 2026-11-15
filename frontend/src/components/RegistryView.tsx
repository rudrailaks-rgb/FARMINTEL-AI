import React, { useState } from 'react';
import {
  Database,
  ExternalLink,
  ShieldCheck,
  AlertCircle,
  CheckCircle2,
  Search,
  Filter,
  Layers,
  Clock,
  Globe
} from 'lucide-react';
import { OfficialDataSource } from '../types';

interface Props {
  datasets: OfficialDataSource[];
}

export const RegistryView: React.FC<Props> = ({ datasets }) => {
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [selectedDataset, setSelectedDataset] = useState<OfficialDataSource | null>(null);

  const filtered = datasets.filter(ds => {
    const matchesSearch =
      ds.dataset_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ds.official_provider.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ds.intended_agricultural_use.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesStatus =
      statusFilter === 'ALL' ||
      (statusFilter === 'CONNECTED' && (ds.integration_status === 'CONNECTED' || ds.integration_status === 'DATA_FEED_ACTIVE')) ||
      (statusFilter === 'METADATA_ONLY' && ds.integration_status === 'METADATA_ONLY') ||
      (statusFilter === 'AUTH_REQUIRED' && ds.integration_status === 'AUTH_REQUIRED');

    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none" />
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="px-2.5 py-1 text-xs font-semibold rounded-md bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                LABORATORY 10
              </span>
              <span className="px-2.5 py-1 text-xs font-semibold rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3" />
                NASA CHALLENGE SPECIFICATION
              </span>
              <span className="text-xs text-slate-400 font-mono">
                [19 AUDITED DATASETS]
              </span>
            </div>
            <h2 className="text-2xl font-bold text-white tracking-tight">
              Official Data Source Registry
            </h2>
            <p className="text-slate-400 text-sm mt-1 max-w-2xl">
              Strict audit of all 19 challenge datasets. Delineates real REST APIs, Earthdata authentication protocols, modern waterdata APIs, and eliminates metadata discovery misrepresentation.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="relative">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="Search datasets..."
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
                className="pl-9 pr-3 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 w-56"
              />
            </div>

            <div className="flex bg-slate-950 p-1 rounded-lg border border-slate-800 text-xs">
              {['ALL', 'CONNECTED', 'METADATA_ONLY', 'AUTH_REQUIRED'].map(status => (
                <button
                  key={status}
                  onClick={() => setStatusFilter(status)}
                  className={`px-2.5 py-1 rounded text-[11px] font-semibold transition-colors ${
                    statusFilter === status
                      ? 'bg-cyan-600 text-white'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  {status.replace('_', ' ')}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Dataset Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map(ds => {
          const isConnected = ds.integration_status === 'CONNECTED' || ds.integration_status === 'DATA_FEED_ACTIVE';
          const isMetadataOnly = ds.integration_status === 'METADATA_ONLY';

          return (
            <div
              key={ds.dataset_id}
              className="bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition-all flex flex-col justify-between shadow-md"
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-2">
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400">
                    {ds.official_provider}
                  </span>
                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider ${
                      isConnected
                        ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                        : isMetadataOnly
                        ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                        : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                    }`}
                  >
                    {ds.integration_status.replace('_', ' ')}
                  </span>
                </div>

                <h3 className="text-base font-bold text-white mb-1 leading-snug">
                  {ds.dataset_name}
                </h3>
                <p className="text-xs text-slate-400 mb-3 line-clamp-2">
                  {ds.intended_agricultural_use}
                </p>

                <div className="space-y-1.5 text-[11px] bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/80 mb-3">
                  <div className="flex justify-between text-slate-400">
                    <span>Access Method:</span>
                    <span className="text-slate-300 font-mono font-medium">{ds.access_method}</span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Authentication:</span>
                    <span className="text-slate-300 font-medium">{ds.authentication_requirement}</span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Spatial / Temporal:</span>
                    <span className="text-slate-300 font-mono">{ds.spatial_resolution} • {ds.temporal_resolution}</span>
                  </div>
                </div>

                {ds.known_limitations && (
                  <p className="text-[11px] text-slate-500 italic mb-3">
                    <strong className="text-slate-400 not-italic">Limitation:</strong> {ds.known_limitations}
                  </p>
                )}
              </div>

              <div className="flex items-center justify-between pt-3 border-t border-slate-800/60 text-xs">
                <a
                  href={ds.official_access_url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-cyan-400 hover:text-cyan-300 flex items-center gap-1 font-medium transition-colors"
                >
                  Official Portal <ExternalLink className="w-3 h-3" />
                </a>
                <span className="text-[10px] text-slate-500 font-mono">
                  Audited: {ds.last_successful_test}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
