import api from './api';

export interface PredictionInput {
  attendance: number;
  stadium_capacity: number;
  match_minute: number;
  entry_rate_per_min: number;
  exit_rate_per_min: number;
  temperature: number;
  humidity: number;
  rain_probability: number;
  parking_occupancy: number;
  metro_arrivals: number;
  bus_arrivals: number;
  ticket_scan_rate: number;
  security_queue_length: number;
  food_court_density: number;
  restroom_density: number;
  medical_incidents: number;
  previous_congestion: number;
  gate_open_count: number;
  vip_event: boolean;
  special_event: boolean;
  holiday: boolean;
  weekday: string;
  security_staff?: number;
  gate_capacity?: number;
  closed_gates?: string[];
  incident_count?: number;
  incident_type?: string;
  forecast_hours?: number;
}

export interface FactorImpact {
  feature: string;
  impact: number;
}

export interface PredictionOutput {
  predicted_occupancy: number;
  risk_level: string;
  congestion_score: number;
  queue_prediction: number;
  confidence: number;
  top_factors: FactorImpact[];
  timestamp: string;
}

export interface ExplainablePrediction {
  confidence: number;
  top_factors: FactorImpact[];
  explanation: string;
}

export interface ZoneCongestionPrediction extends ExplainablePrediction {
  zone_id: string;
  zone_name: string;
  predicted_occupancy: number;
  congestion_score: number;
}

export interface GateQueuePrediction extends ExplainablePrediction {
  gate_id: string;
  gate_name: string;
  zone_id: string;
  estimated_wait_minutes: number;
}

export interface AttendanceForecastPoint extends ExplainablePrediction {
  hour_offset: number;
  forecast_time: string;
  predicted_attendance: number;
}

export interface ZoneRiskPrediction extends ExplainablePrediction {
  zone_id: string;
  zone_name: string;
  risk_level: 'Safe' | 'Moderate' | 'High' | 'Critical';
}

export interface EmergencySeverityPrediction extends ExplainablePrediction {
  incident_type: string;
  predicted_severity: 'Low' | 'Medium' | 'High' | 'Critical';
}

export interface SecurityRecommendation extends ExplainablePrediction {
  current_personnel: number;
  recommended_total_personnel: number;
  delta: number;
  high_pressure_zones: string[];
  deployments: Array<{
    zone_id: string;
    zone_name: string;
    recommended_personnel: number;
    confidence: number;
    top_factors: FactorImpact[];
    explanation: string;
  }>;
}

export interface MedicalDemandPrediction extends ExplainablePrediction {
  zone_id: string;
  zone_name: string;
  expected_cases: number;
}

export interface VendorDemandPrediction extends ExplainablePrediction {
  vendor_zone_id: string;
  vendor_zone_name: string;
  food_units: number;
  beverage_units: number;
  merchandise_units: number;
  total_units: number;
}

export interface ParkingOccupancyPrediction extends ExplainablePrediction {
  parking_id: string;
  parking_name: string;
  capacity: number;
  predicted_occupancy_pct: number;
  available_spaces: number;
}

export interface TrafficFlowPrediction extends ExplainablePrediction {
  corridor_id: string;
  corridor_name: string;
  incoming_congestion: number;
  outgoing_congestion: number;
  incoming_level: string;
  outgoing_level: string;
}

export interface WeatherImpactPrediction extends ExplainablePrediction {
  attendance_impact_pct: number;
  congestion_impact_pct: number;
  queue_impact_pct: number;
  operational_risk_impact_pct: number;
}

export interface AIRecommendationPrediction {
  title: string;
  priority: string;
  action: string;
  expected_impact: string;
  confidence: number;
  explanation: string;
  top_factors: FactorImpact[];
}

export interface OperationsPredictionOutput {
  status: string;
  source: string;
  generated_at: string;
  model_version: string;
  training_rows: number;
  evaluations: Record<string, { metric: string; value: number }>;
  legacy_crowd: PredictionOutput;
  crowd_congestion: ZoneCongestionPrediction[];
  queue_times: GateQueuePrediction[];
  attendance_forecast: AttendanceForecastPoint[];
  crowd_risk: ZoneRiskPrediction[];
  emergency_severity: EmergencySeverityPrediction;
  security_recommendation: SecurityRecommendation;
  medical_demand: MedicalDemandPrediction[];
  vendor_demand: VendorDemandPrediction[];
  parking_occupancy: ParkingOccupancyPrediction[];
  traffic_flow: TrafficFlowPrediction[];
  weather_impact: WeatherImpactPrediction;
  recommendations: AIRecommendationPrediction[];
}

export const predictionService = {
  predictCrowd: async (input: PredictionInput, signal?: AbortSignal): Promise<PredictionOutput> => {
    // Expose backend prediction call
    const response = await api.post<PredictionOutput>('/api/v1/predict/crowd', input, { signal });
    return response.data;
  },

  predictOperations: async (input: PredictionInput, signal?: AbortSignal): Promise<OperationsPredictionOutput> => {
    const response = await api.post<OperationsPredictionOutput>('/api/v1/predict/operations', input, { signal });
    return response.data;
  }
};
