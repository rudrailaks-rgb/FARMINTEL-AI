import React from 'react';
import {
  LayoutGrid,
  Compass,
  Sun,
  Satellite,
  Layers,
  Cpu,
  Sprout,
  BarChart3,
  ShieldCheck,
  Database,
  BookOpen,
  ChevronRight,
  X
} from 'lucide-react';

export type DashboardView =
  | 'overview'
  | 'field'
  | 'climate'
  | 'explorer'
  | 'soil'
  | 'suitability'
  | 'rotations'
  | 'ml_models'
  | 'evidence';

interface SidebarProps {
  activeView: DashboardView;
  onSelectView: (view: DashboardView) => void;
  isOpenMobile: boolean;
  onCloseMobile: () => void;
  onOpenRegistry: () => void;
  onOpenCrops: () => void;
  backendConnected: boolean;
}

const NAV_ITEMS: { id: DashboardView; label: string; icon: React.ComponentType<{ className?: string }>; badge?: string }[] = [
  { id: 'overview', label: 'Overview', icon: LayoutGrid },
  { id: 'field', label: 'Field Intelligence', icon: Compass },
  { id: 'climate', label: 'Climate Intelligence', icon: Sun },
  { id: 'explorer', label: 'Satellite Explorer', icon: Satellite },
  { id: 'soil', label: 'Soil Intelligence', icon: Layers },
  { id: 'suitability', label: 'Crop Suitability', icon: Cpu },
  { id: 'rotations', label: 'Rotation Optimizer', icon: Sprout },
  { id: 'ml_models', label: 'ML Models', icon: BarChart3 },
  { id: 'evidence', label: 'Evidence & Reports', icon: ShieldCheck },
];

export const Sidebar: React.FC<SidebarProps> = ({
  activeView,
  onSelectView,
  isOpenMobile,
  onCloseMobile,
  onOpenRegistry,
  onOpenCrops,
  backendConnected,
}) => {
  return (
    <>
      {/* Mobile Backdrop */}
      {isOpenMobile && (
        <div
          className="fixed inset-0 bg-black/70 backdrop-blur-sm z-40 lg:hidden"
          onClick={onCloseMobile}
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed lg:sticky top-0 left-0 z-50 h-screen w-64 bg-[#0A0F1D] border-r border-[#1B253D] flex flex-col justify-between transition-transform duration-300 ease-in-out select-none ${
          isOpenMobile ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        {/* Top: Identity / Branding */}
        <div>
          <div className="h-16 px-5 border-b border-[#1B253D] flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-gradient-to-br from-emerald-500 to-teal-700 rounded-xl shadow-md shadow-emerald-500/20 text-white flex-shrink-0">
                <Sprout className="w-5 h-5 stroke-[2.2]" />
              </div>
              <div>
                <h1 className="text-base font-black tracking-tight text-white flex items-center gap-1.5">
                  FARMINTEL <span className="text-emerald-400 font-extrabold">AI</span>
                </h1>
                <p className="text-[11px] font-medium text-slate-400">
                  NASA Space Apps 2026
                </p>
              </div>
            </div>

            {/* Mobile close button */}
            <button
              onClick={onCloseMobile}
              className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 lg:hidden"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Core Navigation List */}
          <nav className="p-3 space-y-1.5">
            <div className="px-3 py-1.5 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
              Intelligence Suites
            </div>

            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              const isActive = activeView === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    onSelectView(item.id);
                    onCloseMobile();
                  }}
                  className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-semibold transition-all ${
                    isActive
                      ? 'bg-emerald-500 text-slate-950 font-bold shadow-md shadow-emerald-950/40 ring-1 ring-emerald-400'
                      : 'text-slate-300 hover:text-white hover:bg-[#141C30]'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <Icon className={`w-4 h-4 flex-shrink-0 ${isActive ? 'text-slate-950 stroke-[2.2]' : 'text-slate-400'}`} />
                    <span>{item.label}</span>
                  </div>
                  {isActive && <ChevronRight className="w-4 h-4 text-slate-950 stroke-[2.5]" />}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Bottom: Registry, Crops, and Status */}
        <div className="p-3 border-t border-[#1B253D] space-y-2 bg-[#080D1A]">
          <div className="px-3 py-1 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
            Resources & Data
          </div>

          <button
            onClick={() => {
              onOpenRegistry();
              onCloseMobile();
            }}
            className="w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-semibold text-slate-300 hover:text-cyan-300 hover:bg-[#141C30] border border-[#1B253D] hover:border-cyan-500/40 transition-all"
          >
            <div className="flex items-center space-x-2">
              <Database className="w-3.5 h-3.5 text-cyan-400" />
              <span>Data Registry</span>
            </div>
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
              28 Feeds
            </span>
          </button>

          <button
            onClick={() => {
              onOpenCrops();
              onCloseMobile();
            }}
            className="w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-semibold text-slate-300 hover:text-emerald-300 hover:bg-[#141C30] border border-[#1B253D] hover:border-emerald-500/40 transition-all"
          >
            <div className="flex items-center space-x-2">
              <BookOpen className="w-3.5 h-3.5 text-emerald-400" />
              <span>Crop Catalog</span>
            </div>
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
              10 Species
            </span>
          </button>

          {/* Engine Status */}
          <div className="flex items-center justify-between px-3 py-2 rounded-lg bg-[#0E1526] border border-[#1B253D] text-xs">
            <div className="flex items-center space-x-2">
              <span className="relative flex h-2 w-2">
                {backendConnected ? (
                  <>
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                  </>
                ) : (
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-rose-500"></span>
                )}
              </span>
              <span className="text-slate-300 text-xs font-medium">
                {backendConnected ? 'Engine Online' : 'Connecting...'}
              </span>
            </div>
            <span className="text-[10px] font-mono text-emerald-400">v2.0.0</span>
          </div>
        </div>
      </aside>
    </>
  );
};
