import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import { MapPin, AlertTriangle, RotateCcw, Layers, Globe, Search, Loader2, Navigation } from 'lucide-react';
import { api } from '../api';

interface MapPickerProps {
  latitude: number;
  longitude: number;
  onCoordinatesChange: (lat: number, lon: number, county?: string, state?: string) => void;
  heightClass?: string;
  geocodedLocation?: string;
}

const US_PRESETS = [
  { name: 'Ames, IA', lat: 42.0308, lon: -93.6319, desc: 'Midwest Corn Belt', county: 'Story County', state: 'Iowa' },
  { name: 'Fresno, CA', lat: 36.7468, lon: -119.7726, desc: 'Central Valley', county: 'Fresno County', state: 'California' },
  { name: 'Finney Co, KS', lat: 37.9717, lon: -100.8654, desc: 'Great Plains Wheat', county: 'Finney County', state: 'Kansas' },
  { name: 'Champaign, IL', lat: 40.1164, lon: -88.2434, desc: 'Prairie Loam', county: 'Champaign County', state: 'Illinois' },
  { name: 'Grand Island, NE', lat: 40.9250, lon: -98.3421, desc: 'Platte River Basin', county: 'Hall County', state: 'Nebraska' },
  { name: 'Lubbock, TX', lat: 33.5779, lon: -101.8552, desc: 'High Plains Cotton', county: 'Lubbock County', state: 'Texas' },
  { name: 'Wayne Co, NC', lat: 35.3849, lon: -77.9928, desc: 'Atlantic Coastal Plain', county: 'Wayne County', state: 'North Carolina' },
];

const GLOBAL_PRESETS = [
  { name: 'Punjab, India', lat: 30.9010, lon: 75.8573, desc: 'Indo-Gangetic Wheat/Rice', county: 'Ludhiana', state: 'Punjab' },
  { name: 'Mato Grosso, Brazil', lat: -12.5560, lon: -55.7226, desc: 'Cerrado Soybeans/Corn', county: 'Sorriso', state: 'Mato Grosso' },
  { name: 'Beauce, France', lat: 48.4439, lon: 1.4890, desc: 'European Wheat Granary', county: 'Chartres', state: 'Centre-Val de Loire' },
  { name: 'Alberta, Canada', lat: 58.3095, lon: -116.8210, desc: 'Peace River Grain', county: 'Peace River', state: 'Alberta' },
  { name: 'NSW, Australia', lat: -31.2532, lon: 146.9211, desc: 'Grain & Sheep Belt', county: 'Dubbo', state: 'New South Wales' },
  { name: 'Rift Valley, Kenya', lat: -0.3031, lon: 36.0800, desc: 'Highland Maize/Legumes', county: 'Nakuru', state: 'Rift Valley' },
];

export const MapPicker: React.FC<MapPickerProps> = ({
  latitude,
  longitude,
  onCoordinatesChange,
  heightClass = 'h-[420px]',
  geocodedLocation,
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<L.Map | null>(null);
  const markerRef = useRef<L.Marker | null>(null);
  const tileLayerRef = useRef<L.TileLayer | null>(null);

  const [activeLayer, setActiveLayer] = useState<'standard' | 'satellite'>('standard');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [isSearching, setIsSearching] = useState<boolean>(false);
  const [showSearchResults, setShowSearchResults] = useState<boolean>(false);
  const [localGeocode, setLocalGeocode] = useState<string>('');
  const [presetTab, setPresetTab] = useState<'us' | 'global'>('us');

  const validLat = Math.max(-90, Math.min(90, isNaN(latitude) ? 42.0308 : latitude));
  const validLon = Math.max(-180, Math.min(180, isNaN(longitude) ? -93.6319 : longitude));
  const isOutsideConus = validLat > 50 || validLat < 24 || validLon > -66 || validLon < -125;

  // Reverse geocode whenever coordinates change
  useEffect(() => {
    let active = true;
    const fetchGeocode = async () => {
      try {
        const res = await api.reverseGeocode(validLat, validLon);
        if (active && res.success && res.display_name) {
          const locStr = `${res.county || ''}${res.county && res.state ? ', ' : ''}${res.state || ''}${res.country ? ` (${res.country})` : ''}`;
          setLocalGeocode(locStr || res.display_name);
        }
      } catch {
        if (active) setLocalGeocode(`${validLat.toFixed(4)}°, ${validLon.toFixed(4)}°`);
      }
    };
    fetchGeocode();
    return () => { active = false; };
  }, [validLat, validLon]);

  // Handle location search query
  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    setIsSearching(true);
    try {
      const data = await api.searchLocations(searchQuery);
      setSearchResults(data.results || []);
      setShowSearchResults(true);
    } catch {
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const selectSearchResult = (item: any) => {
    const lat = parseFloat(item.latitude);
    const lon = parseFloat(item.longitude);
    if (!isNaN(lat) && !isNaN(lon)) {
      onCoordinatesChange(lat, lon, item.county, item.state);
      if (mapRef.current) {
        mapRef.current.flyTo([lat, lon], 9, { duration: 0.8 });
      }
    }
    setShowSearchResults(false);
    setSearchQuery('');
  };

  // Initialize Map Once on Mount
  useEffect(() => {
    const container = mapContainerRef.current;
    if (!container) return;

    if ((container as any)._leaflet_id) {
      delete (container as any)._leaflet_id;
    }

    try {
      const map = L.map(container, {
        center: [validLat, validLon],
        zoom: 7,
        zoomControl: true,
      });

      const osmLayer = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> contributors',
        maxZoom: 19,
      }).addTo(map);

      tileLayerRef.current = osmLayer;

      const customIcon = L.divIcon({
        className: 'custom-map-pin',
        html: `
          <div style="position: relative; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center;">
            <div style="position: absolute; width: 24px; height: 24px; border-radius: 50%; background: rgba(16, 185, 129, 0.35); animation: ping 2s cubic-bezier(0, 0, 0.2, 1) infinite;"></div>
            <div style="width: 15px; height: 15px; border-radius: 50%; background: #10B981; border: 2.5px solid #FFFFFF; box-shadow: 0 0 12px rgba(16, 185, 129, 1);"></div>
          </div>
        `,
        iconSize: [24, 24],
        iconAnchor: [12, 12],
      });

      const marker = L.marker([validLat, validLon], {
        icon: customIcon,
        draggable: true,
      }).addTo(map);

      marker.on('dragend', () => {
        const pos = marker.getLatLng();
        const safeLat = parseFloat(Math.max(-90, Math.min(90, pos.lat)).toFixed(5));
        const safeLon = parseFloat(Math.max(-180, Math.min(180, pos.lng)).toFixed(5));
        onCoordinatesChange(safeLat, safeLon);
      });

      map.on('click', (e) => {
        const safeLat = parseFloat(Math.max(-90, Math.min(90, e.latlng.lat)).toFixed(5));
        const safeLon = parseFloat(Math.max(-180, Math.min(180, e.latlng.lng)).toFixed(5));
        marker.setLatLng([safeLat, safeLon]);
        onCoordinatesChange(safeLat, safeLon);
      });

      mapRef.current = map;
      markerRef.current = marker;

      setTimeout(() => {
        map.invalidateSize();
      }, 250);
    } catch (err) {
      console.warn('Leaflet map init warning:', err);
    }

    return () => {
      if (mapRef.current) {
        try {
          mapRef.current.remove();
        } catch {}
        mapRef.current = null;
      }
      if (container && (container as any)._leaflet_id) {
        delete (container as any)._leaflet_id;
      }
      markerRef.current = null;
    };
  }, []);

  // Switch Tile Layer
  useEffect(() => {
    if (!mapRef.current) return;
    try {
      if (tileLayerRef.current) {
        mapRef.current.removeLayer(tileLayerRef.current);
      }

      if (activeLayer === 'satellite') {
        tileLayerRef.current = L.tileLayer(
          'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
          {
            attribution: '&copy; Esri &mdash; USDA, USGS, Planet, Earthstar Geographics',
            maxZoom: 18,
          }
        ).addTo(mapRef.current);
      } else {
        tileLayerRef.current = L.tileLayer(
          'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
          {
            attribution: '&copy; OpenStreetMap contributors',
            maxZoom: 19,
          }
        ).addTo(mapRef.current);
      }
    } catch (err) {
      console.warn('Tile layer switch error:', err);
    }
  }, [activeLayer]);

  // Synchronize Map View on Coordinate Change
  useEffect(() => {
    if (mapRef.current && markerRef.current) {
      try {
        const currentPos = markerRef.current.getLatLng();
        if (
          Math.abs(currentPos.lat - validLat) > 0.0001 ||
          Math.abs(currentPos.lng - validLon) > 0.0001
        ) {
          mapRef.current.setView([validLat, validLon], mapRef.current.getZoom());
          markerRef.current.setLatLng([validLat, validLon]);
        }
      } catch {}
    }
  }, [validLat, validLon]);

  // Formatted hemisphere coordinates
  const latStr = validLat >= 0 ? `${validLat.toFixed(4)}° N` : `${Math.abs(validLat).toFixed(4)}° S`;
  const lonStr = validLon >= 0 ? `${validLon.toFixed(4)}° E` : `${Math.abs(validLon).toFixed(4)}° W`;

  return (
    <div className="bg-[#0E1526] rounded-2xl border border-[#1B253D] p-5 flex flex-col justify-between shadow-xl h-full">
      <div className="space-y-3.5">
        {/* Top Header & Layer Switcher */}
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
              <MapPin className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
                Geospatial Field Workspace
                <span className="text-[11px] font-mono font-medium px-2 py-0.5 rounded-full bg-cyan-500/15 text-cyan-300 border border-cyan-500/30">
                  {geocodedLocation || localGeocode || 'United States'}
                </span>
              </h3>
              <p className="text-xs text-slate-400">
                Click map, drag the marker, or search any US county to set the authoritative field
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2 bg-[#090D18] p-1 rounded-xl border border-[#1B253D]">
            <button
              onClick={() => setActiveLayer('standard')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeLayer === 'standard'
                  ? 'bg-emerald-500 text-slate-950 shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <Globe className="w-3.5 h-3.5" />
              <span>Standard Map</span>
            </button>

            <button
              onClick={() => setActiveLayer('satellite')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeLayer === 'satellite'
                  ? 'bg-cyan-500 text-slate-950 shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <Layers className="w-3.5 h-3.5" />
              <span>Satellite Imagery</span>
            </button>
          </div>
        </div>

        {/* Search Bar for Locations Worldwide */}
        <div className="relative">
          <form onSubmit={handleSearch} className="flex gap-2">
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search any farm, county, state, or country worldwide (e.g. 'Punjab, India', 'Mato Grosso', 'France', 'Finney Co, KS')..."
                className="w-full bg-[#141C30] border border-[#1B253D] rounded-xl pl-9 pr-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
              />
            </div>
            <button
              type="submit"
              disabled={isSearching}
              className="px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-bold text-xs flex items-center gap-1.5 transition-all shadow-sm disabled:opacity-50"
            >
              {isSearching ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Navigation className="w-3.5 h-3.5" />}
              <span>Find</span>
            </button>
          </form>

          {/* Search Dropdown Results */}
          {showSearchResults && searchResults.length > 0 && (
            <div className="absolute top-full left-0 right-0 mt-1 bg-[#0E1526] border border-cyan-500/50 rounded-xl shadow-2xl z-20 max-h-48 overflow-y-auto">
              {searchResults.map((item, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => selectSearchResult(item)}
                  className="w-full text-left px-3.5 py-2.5 hover:bg-[#141C30] text-xs text-slate-200 border-b border-[#1B253D] last:border-none flex items-center justify-between"
                >
                  <span className="font-medium truncate">{item.display_name}</span>
                  <span className="text-[11px] font-mono text-cyan-400 ml-2 whitespace-nowrap">
                    ({item.latitude}°, {item.longitude}°)
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Preset Region Buttons */}
        <div>
          <div className="text-xs font-semibold text-slate-400 mb-1.5 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-slate-300">Agricultural Breadbaskets:</span>
              <button
                type="button"
                onClick={() => setPresetTab('us')}
                className={`px-2 py-0.5 rounded text-[11px] font-bold transition-colors ${
                  presetTab === 'us'
                    ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                    : 'bg-[#141C30] text-slate-400 hover:text-white border border-[#1B253D]'
                }`}
              >
                🇺🇸 US Belts
              </button>
              <button
                type="button"
                onClick={() => setPresetTab('global')}
                className={`px-2 py-0.5 rounded text-[11px] font-bold transition-colors ${
                  presetTab === 'global'
                    ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40'
                    : 'bg-[#141C30] text-slate-400 hover:text-white border border-[#1B253D]'
                }`}
              >
                🌍 Global Breadbaskets
              </button>
            </div>
            <span className="text-[11px] font-mono text-slate-500 hidden sm:inline">
              {presetTab === 'us' ? 'CONUS High-Yield Hubs' : 'International Grain Belts'}
            </span>
          </div>

          <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none">
            {(presetTab === 'us' ? US_PRESETS : GLOBAL_PRESETS).map((preset) => {
              const isSelected =
                Math.abs(validLat - preset.lat) < 0.05 && Math.abs(validLon - preset.lon) < 0.05;
              return (
                <button
                  key={preset.name}
                  onClick={() => {
                    onCoordinatesChange(preset.lat, preset.lon, preset.county, preset.state);
                    if (mapRef.current) {
                      mapRef.current.flyTo([preset.lat, preset.lon], presetTab === 'us' ? 8 : 6, { duration: 0.8 });
                    }
                  }}
                  className={`text-xs px-3 py-1.5 rounded-lg border whitespace-nowrap transition-all flex items-center space-x-1.5 font-medium ${
                    isSelected
                      ? presetTab === 'us'
                        ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/60 font-bold shadow-sm ring-1 ring-emerald-500/30'
                        : 'bg-cyan-500/20 text-cyan-300 border-cyan-500/60 font-bold shadow-sm ring-1 ring-cyan-500/30'
                      : 'bg-[#141C30] text-slate-300 border-[#1B253D] hover:border-slate-500 hover:text-white'
                  }`}
                >
                  <span>{preset.name}</span>
                  <span className="text-[10px] text-slate-400 font-mono">({preset.desc})</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* The Leaflet Map Viewport */}
        <div className={`w-full ${heightClass} rounded-xl overflow-hidden border border-[#1B253D] shadow-inner relative`}>
          <div ref={mapContainerRef} className="w-full h-full z-0" />
        </div>
      </div>

      {/* Footer Bar with Coordinates & Survey Status */}
      <div className="mt-3.5 pt-3 border-t border-[#1B253D] flex flex-wrap items-center justify-between text-xs text-slate-300 gap-2">
        <div className="flex items-center space-x-3">
          <span className="font-mono text-emerald-400 font-bold bg-[#090D18] px-3 py-1.5 rounded-lg border border-[#1B253D] text-xs">
            {latStr}, {lonStr}
          </span>

          {isOutsideConus ? (
            <span className="flex items-center gap-1.5 text-xs text-cyan-300 font-medium bg-cyan-500/10 px-3 py-1.5 rounded-lg border border-cyan-500/30">
              <Globe className="w-3.5 h-3.5 text-cyan-400 flex-shrink-0" />
              Global Field Active ({geocodedLocation || localGeocode || 'International Region'}) • Live Global NASA POWER & ERA5 Observations
            </span>
          ) : (
            <span className="flex items-center gap-1.5 text-xs text-emerald-300 bg-emerald-500/10 px-3 py-1.5 rounded-lg border border-emerald-500/30">
              ✓ Domestic CONUS SSURGO Footprint ({geocodedLocation || localGeocode || 'Domestic CONUS'})
            </span>
          )}
        </div>

        {isOutsideConus && (
          <button
            onClick={() => {
              onCoordinatesChange(42.0308, -93.6319, 'Story County', 'Iowa');
              if (mapRef.current) {
                mapRef.current.flyTo([42.0308, -93.6319], 8, { duration: 0.8 });
              }
            }}
            className="flex items-center gap-1.5 text-xs text-cyan-400 hover:text-cyan-300 underline font-semibold"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            Reset to Ames, Iowa
          </button>
        )}
      </div>
    </div>
  );
};
