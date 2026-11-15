import React from 'react';
import { Menu, Play, Loader2, MapPin, Database, BookOpen } from 'lucide-react';

interface HeaderProps {
  onToggleMobileMenu: () => void;
  activeViewLabel: string;
  fieldName: string;
  latitude: number;
  longitude: number;
  previousCrop: string;
  farmerPriority: string;
  analysisYear: number;
  onEvaluate: () => void;
  isLoading: boolean;
  onOpenRegistry: () => void;
  onOpenCrops: () => void;
  backendConnected: boolean;
  isStale?: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  onToggleMobileMenu,
  activeViewLabel,
  fieldName,
  latitude,
  longitude,
  previousCrop,
  farmerPriority,
  analysisYear,
  onEvaluate,
  isLoading,
  onOpenRegistry,
  onOpenCrops,
  backendConnected,
  isStale = false,
}) => {
  return (
    <header className="h-16 bg-[#0E1526] border-b border-[#1B253D] px-4 sm:px-6 flex items-center justify-between sticky top-0 z-30 shadow-md">
      {/* Left: Mobile hamburger & Active View Heading */}
      <div className="flex items-center space-x-3 sm:space-x-4">
        <button
          onClick={onToggleMobileMenu}
          className="p-2 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 lg:hidden"
          aria-label="Open Navigation Menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div>
          <div className="flex items-center space-x-2">
            <h2 className="text-lg sm:text-xl font-bold text-white tracking-tight">
              {activeViewLabel}
            </h2>
            <span className="hidden md:inline-flex px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              NASA Earth Data Workspace
            </span>
          </div>
          <p className="text-xs text-slate-400 hidden sm:block">
            Agricultural Decision Intelligence Platform • United States
          </p>
        </div>
      </div>

      {/* Center/Right: Active Field Context & Primary Action Button */}
      <div className="flex items-center space-x-3 sm:space-x-4">
        {/* Active Field Badge */}
        <div className={`hidden xl:flex items-center space-x-2 bg-[#090D18] px-3.5 py-1.5 rounded-xl border ${isStale ? 'border-amber-500/50 bg-amber-950/20' : 'border-[#1B253D]'} text-xs transition-colors`}>
          <MapPin className={`w-4 h-4 ${isStale ? 'text-amber-400' : 'text-emerald-400'} flex-shrink-0`} />
          <span className="font-semibold text-slate-200">{fieldName}</span>
          <span className="font-mono text-emerald-400 font-medium">
            ({(Number(latitude) || 0).toFixed(4)}°, {(Number(longitude) || 0).toFixed(4)}°)
          </span>
          {isStale && (
            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40 animate-pulse">
              PENDING EVALUATION
            </span>
          )}
          <span className="text-slate-600">•</span>
          <span className="text-slate-400">
            Prior: <strong className="text-slate-200 capitalize">{previousCrop}</strong>
          </span>
          <span className="text-slate-600">•</span>
          <span className="text-slate-400">
            Priority: <strong className="text-slate-200 capitalize">{farmerPriority.replace('_', ' ')}</strong>
          </span>
          <span className="text-slate-600">•</span>
          <span className="text-slate-400">
            Year: <strong className="text-slate-200">{analysisYear}</strong>
          </span>
        </div>

        {/* Quick Resource Buttons (Tablet/Desktop) */}
        <div className="hidden md:flex items-center space-x-2">
          <button
            onClick={onOpenRegistry}
            className="flex items-center space-x-1.5 px-3 py-2 rounded-lg bg-[#141C30] hover:bg-[#1A253F] text-slate-300 hover:text-cyan-300 border border-[#1B253D] text-xs font-semibold transition-all shadow-sm"
          >
            <Database className="w-3.5 h-3.5 text-cyan-400" />
            <span>Registry</span>
          </button>
          <button
            onClick={onOpenCrops}
            className="flex items-center space-x-1.5 px-3 py-2 rounded-lg bg-[#141C30] hover:bg-[#1A253F] text-slate-300 hover:text-emerald-300 border border-[#1B253D] text-xs font-semibold transition-all shadow-sm"
          >
            <BookOpen className="w-3.5 h-3.5 text-emerald-400" />
            <span>Crops</span>
          </button>
        </div>

        {/* Primary Evaluate Button */}
        <button
          onClick={onEvaluate}
          disabled={isLoading}
          className="flex items-center space-x-2 px-4 sm:px-5 py-2 rounded-xl text-xs sm:text-sm font-bold bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 shadow-lg shadow-emerald-500/20 uppercase tracking-wider transition-all disabled:opacity-50"
        >
          {isLoading ? (
            <Loader2 className="w-4 h-4 animate-spin text-slate-950" />
          ) : (
            <Play className="w-4 h-4 fill-slate-950 stroke-none" />
          )}
          <span>{isLoading ? 'Analyzing...' : 'Evaluate Plan'}</span>
        </button>
      </div>
    </header>
  );
};
