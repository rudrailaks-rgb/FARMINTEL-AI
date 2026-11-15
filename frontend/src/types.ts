// FARMINTEL AI — TypeScript Domain Models

export interface OfficialDataSource {
  dataset_id: string;
  dataset_name: string;
  official_provider: string;
  official_access_url: string;
  api_documentation_url: string;
  access_method: string;
  authentication_requirement: string;
  supported_output_format: string;
  spatial_resolution: string;
  temporal_resolution: string;
  available_dates?: string;
  geographic_coverage?: string;
  intended_agricultural_use: string;
  integration_status: 'USED_IN_ANALYSIS' | 'OBSERVATION_RETRIEVED' | 'METADATA_RETRIEVED' | 'SOURCE_DISCOVERED' | 'DATA_FEED_ACTIVE' | 'METADATA_ONLY' | 'AUTH_REQUIRED' | 'CONNECTED' | 'PENDING' | 'FAILED' | 'PARTIAL' | string;
  stages?: {
    source_discovered?: boolean;
    metadata_retrieved?: boolean;
    observation_retrieved?: boolean;
    data_parsed?: boolean;
    indicators_processed?: boolean;
    used_by_decision_engine?: boolean;
    displayed_in_frontend?: boolean;
  };
  data_retrieval_nature?: string;
  last_successful_test: string;
  known_limitations: string;
}

export interface ClimateIndicator {
  indicator_id: string;
  name: string;
  category: string;
  value: number;
  units: string;
  metric_value?: number;
  metric_units?: string;
  secondary_value?: number;
  secondary_units?: string;
  formula?: string;
  definition?: string;
  source?: string;
  risk_rating?: string;
  limitations?: string;
}

export interface MonthlyRecord {
  month: string;
  avg_temp_c: number;
  avg_temp_f: number;
  max_temp_c: number;
  min_temp_c: number;
  rainfall_mm: number;
  rainfall_in: number;
  solar_radiation: number;
}

export interface SoilIndicator {
  indicator_id: string;
  name: string;
  value: any;
  units: string;
  score: number;
  rating: string;
  definition: string;
}

export interface SoilProfileResponse {
  composite_soil_health_score: number;
  soil_health_tier: string;
  mapunit_name: string;
  dominant_series: string;
  texture: string;
  trafficability: string;
  indicators: SoilIndicator[];
  limitations: string[];
  is_fallback?: boolean;
}

export interface CropKnowledge {
  id: string;
  name: string;
  category: string;
  min_gdd_f: number;
  optimal_gdd_f: number;
  base_temp_c: number;
  water_requirement_mm: number;
  heat_stress_threshold_c: number;
  frost_tolerant: boolean;
  min_ph: number;
  max_ph: number;
  optimal_ph_min: number;
  optimal_ph_max: number;
  nitrogen_fixer: boolean;
  root_depth_cm: number;
  biomass_potential: string;
  erosion_protection: string;
  typical_market_price_usd: number;
  average_yield: number;
  yield_units: string;
  gross_revenue_usd_acre: number;
}

export interface StrategyMetrics {
  overall_score: number;
  suitability_score?: number;
  data_confidence_score?: number;
  water_demand_rating: string;
  water_demand_index: number;
  soil_improvement_potential: string;
  soil_improvement_index: number;
  nitrogen_balance: string;
  nitrogen_credit_lb_ac: number;
  erosion_reduction_potential: string;
  erosion_score: number;
  pest_cycle_interruption: string;
  climate_suitability: string;
  growing_season_compatibility: string;
  market_liquidity: string;
}

export interface StrategyExplainability {
  why_suggested: string;
  supporting_observations: string[];
  expected_benefits: string[];
  inherent_risks: string[];
  missing_information: string[];
  confidence_score: number;
  validation_checklist: string[];
}

export interface RotationSequenceItem {
  year: number;
  crop_id: string;
  crop_name: string;
  season?: string;
}

export type RotationSequenceEntry = string | RotationSequenceItem;

export interface RotationStrategy {
  strategy_id: string;
  name: string;
  provenance_tier?: string;
  rotation_sequence: RotationSequenceEntry[];
  focus: string;
  metrics: StrategyMetrics;
  explainability: StrategyExplainability;
}

export interface RotationDecisionEngineResponse {
  field_name: string;
  state: string;
  latitude?: number;
  longitude?: number;
  analysis_year?: number;
  farmer_priority: string;
  evaluation_timestamp: string;
  primary_recommendation: string;
  recommendation_rationale: string;
  overall_data_confidence?: number;
  strategies: {
    strategy_a: RotationStrategy;
    strategy_b: RotationStrategy;
    strategy_c: RotationStrategy;
  };
  comparison_matrix: any[];
  environmental_context: Record<string, any>;
}

export interface GeospatialContext {
  requested_coordinates: {
    latitude: number;
    longitude: number;
  };
  validated_coordinates: {
    latitude: number;
    longitude: number;
  };
  location_identifier: string;
  field_id?: string;
  geospatial_hash?: string;
  is_conus_covered?: boolean;
  data_sources_queried: string[];
  successful_sources: string[];
  failed_sources: string[];
  boundary_type: string;
  analysis_timestamp: string;
}

export interface MLSuitabilityScore {
  suitability_score: number;
  suitability_pct: number;
  status: 'HIGHLY_SUITABLE' | 'MODERATELY_SUITABLE' | 'CONSTRAINED' | string;
}

export interface MLClimateRisk {
  risk_class: number;
  risk_label: string;
  probabilities: {
    low: number;
    moderate: number;
    high: number;
  };
}

export interface MLInferences {
  features_used: Record<string, number>;
  crop_suitability: Record<string, MLSuitabilityScore>;
  climate_risk: MLClimateRisk;
  yield_performance_factor: number;
  models_metadata?: {
    suitability_model?: string;
    suitability_r2?: number;
    climate_risk_model?: string;
    climate_risk_accuracy?: number;
    yield_performance_model?: string;
    yield_r2?: number;
  };
}

export interface ModelMetricData {
  model_name: string;
  model_type: string;
  training_timestamp: string;
  n_samples_train?: number;
  n_samples_test?: number;
  overall_metrics?: {
    r2_score: number;
    mae: number;
    rmse: number;
  };
  metrics?: {
    accuracy?: number;
    weighted_f1?: number;
    f1_score?: number;
    precision?: number;
    recall?: number;
    r2_score?: number;
    mae?: number;
    rmse?: number;
  };
  per_crop_metrics?: Record<string, { r2?: number; r2_score?: number; mae?: number; rmse?: number; [key: string]: any }>;
  top_features?: Array<{ feature: string; importance: number }>;
  feature_importances?: Record<string, number>;
  confusion_matrix?: number[][];
}

export interface MLModelsReport {
  success: boolean;
  pipeline_version: string;
  dataset_summary: {
    total_records: number;
    agricultural_production_zones: number;
    temporal_range: string;
    features_count: number;
    target_crops_count: number;
  };
  models: {
    crop_suitability?: ModelMetricData;
    climate_risk?: ModelMetricData;
    yield_performance?: ModelMetricData;
  };
}

export interface FieldAnalysisResponse {
  success: boolean;
  geospatial_context?: GeospatialContext;
  field_profile: {
    field_id?: string;
    name?: string;
    state?: string;
    latitude: number;
    longitude: number;
    previous_crop?: string;
    farmer_priority?: string;
    analysis_year?: number;
    geospatial_hash?: string;
  };
  climate_summary: any;
  climate_indicators: ClimateIndicator[];
  monthly_chart_data: MonthlyRecord[];
  soil_profile: SoilProfileResponse;
  era5_reanalysis?: any;
  watershed_hydrology?: any;
  satellite_feeds?: Record<string, any>;
  rotation_decision_engine: RotationDecisionEngineResponse;
  ml_inferences?: MLInferences;
  provenance: {
    climate_source: string;
    soil_source: string;
    satellite_metadata?: string;
    processing_engine: string;
    ml_models?: string;
    optimizer?: string;
  };
}

export function formatConfidence(score?: number): string {
  if (score === undefined || score === null || isNaN(score)) return '90%';
  const val = score <= 1.0 && score > 0 ? score * 100 : score;
  const bounded = Math.max(0, Math.min(100, val));
  return `${Math.round(bounded)}%`;
}
