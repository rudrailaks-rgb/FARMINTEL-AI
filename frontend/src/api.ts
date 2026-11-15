// FARMINTEL AI — API Client Service
import {
  OfficialDataSource,
  FieldAnalysisResponse,
  CropKnowledge,
  RotationDecisionEngineResponse,
  SoilProfileResponse
} from './types';

const API_BASE = '/api';

/**
 * Safely extracts and formats human-readable error messages from API responses.
 * Completely eliminates "[object Object]" errors when Pydantic or FastAPI validation fails.
 */
function formatApiError(err: any, fallback: string = 'An unexpected error occurred'): string {
  if (!err) return fallback;
  if (typeof err === 'string') return err;
  if (typeof err.detail === 'string') return err.detail;
  if (Array.isArray(err.detail)) {
    return err.detail
      .map((d: any) => {
        if (typeof d === 'string') return d;
        const loc = Array.isArray(d.loc) ? d.loc.filter((l: any) => l !== 'body').join('.') : '';
        const msg = d.msg || JSON.stringify(d);
        return loc ? `${loc}: ${msg}` : msg;
      })
      .join('; ');
  }
  if (err.message && typeof err.message === 'string') return err.message;
  try {
    return JSON.stringify(err);
  } catch {
    return fallback;
  }
}

export const api = {
  async getHealth(): Promise<{ status: string; project: string; tagline: string; version: string }> {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error(`Health check failed: ${res.statusText}`);
    return res.json();
  },

  async getOfficialRegistry(): Promise<{ success: boolean; count: number; datasets: OfficialDataSource[] }> {
    const res = await fetch(`${API_BASE}/datasets/registry`);
    if (!res.ok) throw new Error(`Failed to fetch data source registry: ${res.statusText}`);
    return res.json();
  },

  async getDatasetStatus(): Promise<any> {
    const res = await fetch(`${API_BASE}/datasets/status`);
    if (!res.ok) throw new Error(`Failed to fetch dataset statuses: ${res.statusText}`);
    return res.json();
  },

  async getCrops(): Promise<{ success: boolean; count: number; crops: CropKnowledge[] }> {
    const res = await fetch(`${API_BASE}/crops`);
    if (!res.ok) throw new Error(`Failed to fetch crop catalog: ${res.statusText}`);
    return res.json();
  },

  async reverseGeocode(latitude: number, longitude: number): Promise<{
    success: boolean;
    county?: string;
    state?: string;
    state_code?: string;
    country?: string;
    display_name?: string;
    source?: string;
  }> {
    const res = await fetch(`${API_BASE}/field/reverse-geocode?latitude=${latitude}&longitude=${longitude}`);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(formatApiError(err, 'Reverse geocoding failed'));
    }
    return res.json();
  },

  async searchLocations(query: string): Promise<{ results: any[] }> {
    const res = await fetch(`${API_BASE}/field/search?q=${encodeURIComponent(query)}`);
    if (!res.ok) return { results: [] };
    return res.json();
  },

  async getDataAvailability(latitude: number, longitude: number, startDate?: string, endDate?: string): Promise<any> {
    const s = startDate || '2024-04-01';
    const e = endDate || '2024-09-30';
    const res = await fetch(`${API_BASE}/field/availability?latitude=${latitude}&longitude=${longitude}&start_date=${s}&end_date=${e}`);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(formatApiError(err, 'Failed to fetch dataset availability'));
    }
    return res.json();
  },

  async analyzeField(payload: {
    field_name?: string;
    latitude: number;
    longitude: number;
    country?: string;
    state?: string;
    county?: string;
    farmer_priority?: string;
    previous_crop?: string;
    analysis_year?: number;
    start_date?: string;
    end_date?: string;
  }): Promise<FieldAnalysisResponse> {
    const res = await fetch(`${API_BASE}/field/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(formatApiError(err, 'Field analysis failed'));
    }
    return res.json();
  },

  async getSoilProfile(latitude: number, longitude: number): Promise<SoilProfileResponse> {
    const res = await fetch(`${API_BASE}/soil/profile?latitude=${latitude}&longitude=${longitude}`);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(formatApiError(err, 'Soil profile retrieval failed'));
    }
    return res.json();
  },

  async evaluateRotation(payload: any): Promise<RotationDecisionEngineResponse> {
    const res = await fetch(`${API_BASE}/rotation/evaluate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(formatApiError(err, 'Rotation evaluation failed'));
    }
    return res.json();
  },

  async getMlModels(): Promise<any> {
    const res = await fetch(`${API_BASE}/ml/models`);
    if (!res.ok) throw new Error(`Failed to fetch ML models metadata: ${res.statusText}`);
    return res.json();
  },

  async predictMlFeatures(payload: any): Promise<any> {
    const res = await fetch(`${API_BASE}/ml/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(formatApiError(err, 'ML prediction failed'));
    }
    return res.json();
  },

  async getCandidateCrops(): Promise<any> {
    const res = await fetch(`${API_BASE}/ml/crops`);
    if (!res.ok) throw new Error(`Failed to fetch candidate crops: ${res.statusText}`);
    return res.json();
  }
};
