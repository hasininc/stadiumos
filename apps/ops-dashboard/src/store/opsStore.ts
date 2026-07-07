import { create } from 'zustand';

export interface CrowdMetrics {
  zone_id: string;
  zone_name: string;
  occupancy_pct: number;
  headcount: number;
  status: string;
}

export interface EmergencyIncident {
  id: string;
  title: string;
  description: string;
  type: string;
  severity: string;
  status: string;
  reported_at: string;
}

export interface AIRecommendation {
  agent_name: string;
  response_text: string;
  citations?: string[];
  recommended_actions?: string[];
}

export interface VendorInventoryLevel {
  id: string;
  vendor_id: string;
  product_id: string;
  current_stock: number;
  min_threshold: number;
}

export interface OpsState {
  crowdMetrics: CrowdMetrics[];
  incidents: EmergencyIncident[];
  recommendations: AIRecommendation[];
  inventories: VendorInventoryLevel[];
  wsConnected: boolean;
  setWsConnected: (connected: boolean) => void;
  updateCrowdMetrics: (metrics: CrowdMetrics[]) => void;
  addIncident: (incident: EmergencyIncident) => void;
  updateIncidentStatus: (id: string, status: string) => void;
  addRecommendation: (rec: AIRecommendation) => void;
  updateInventories: (invs: VendorInventoryLevel[]) => void;
}

export const useOpsStore = create<OpsState>((set) => ({
  crowdMetrics: [],
  incidents: [],
  recommendations: [],
  inventories: [],
  wsConnected: false,
  setWsConnected: (connected) => set({ wsConnected: connected }),
  updateCrowdMetrics: (metrics) => set({ crowdMetrics: metrics }),
  addIncident: (incident) => set((state) => ({ incidents: [incident, ...state.incidents] })),
  updateIncidentStatus: (id, status) => set((state) => ({
    incidents: state.incidents.map((inc) => inc.id === id ? { ...inc, status } : inc)
  })),
  addRecommendation: (rec) => set((state) => ({ recommendations: [rec, ...state.recommendations] })),
  updateInventories: (invs) => set({ inventories: invs })
}));
