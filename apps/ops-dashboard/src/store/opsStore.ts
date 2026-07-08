import { create } from 'zustand';
import type {
  CrowdZone,
  Incident,
  InventoryItem,
  AIRecommendation,
} from '../services/dashboard';

export type CrowdMetrics = CrowdZone;
export type EmergencyIncident = Incident;
export type VendorInventoryLevel = InventoryItem;
export type { AIRecommendation };

export interface OpsState {
  crowdMetrics: CrowdMetrics[];
  incidents: EmergencyIncident[];
  recommendations: AIRecommendation[];
  inventories: VendorInventoryLevel[];
  wsConnected: boolean;
  setWsConnected: (connected: boolean) => void;
  setCrowdMetrics: (metrics: CrowdMetrics[]) => void;
  updateCrowdMetrics: (metrics: CrowdMetrics[]) => void;
  setIncidents: (incidents: EmergencyIncident[]) => void;
  addIncident: (incident: EmergencyIncident) => void;
  updateIncidentStatus: (id: string, status: string) => void;
  addRecommendation: (rec: AIRecommendation) => void;
  setInventories: (invs: VendorInventoryLevel[]) => void;
  updateInventories: (invs: VendorInventoryLevel[]) => void;
}

export const useOpsStore = create<OpsState>((set) => ({
  crowdMetrics: [],
  incidents: [],
  recommendations: [],
  inventories: [],
  wsConnected: false,
  setWsConnected: (connected) => set({ wsConnected: connected }),
  setCrowdMetrics: (metrics) => set({ crowdMetrics: metrics }),
  updateCrowdMetrics: (metrics) =>
    set((state) => {
      const merged = [...state.crowdMetrics];
      metrics.forEach((m) => {
        const idx = merged.findIndex((z) => z.zone_id === m.zone_id);
        if (idx >= 0) merged[idx] = m;
        else merged.push(m);
      });
      return { crowdMetrics: merged };
    }),
  setIncidents: (incidents) => set({ incidents }),
  addIncident: (incident) =>
    set((state) => ({
      incidents: state.incidents.some((i) => i.id === incident.id)
        ? state.incidents
        : [incident, ...state.incidents],
    })),
  updateIncidentStatus: (id, status) =>
    set((state) => ({
      incidents: state.incidents.map((inc) => (inc.id === id ? { ...inc, status } : inc)),
    })),
  addRecommendation: (rec) =>
    set((state) => ({ recommendations: [rec, ...state.recommendations] })),
  setInventories: (invs) => set({ inventories: invs }),
  updateInventories: (invs) => set({ inventories: invs }),
}));
