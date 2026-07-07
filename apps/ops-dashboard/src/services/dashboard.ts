import api from './api';

export const dashboardService = {
  async getCrowdHeatmap() {
    const res = await api.get('/api/v1/crowd/heatmap');
    return res.data;
  },

  async getIncidents() {
    const res = await api.get('/api/v1/emergencies');
    return res.data;
  },

  async getIncidentDashboard() {
    const res = await api.get('/api/v1/emergencies/dashboard');
    return res.data;
  },

  async getMLPredictionsSummary() {
    const res = await api.get('/api/v1/predictions/latest');
    return res.data;
  },

  async getMLModels() {
    const res = await api.get('/api/v1/predictions/models');
    return res.data;
  },

  async getVendorInventory() {
    const res = await api.get('/api/v1/vendors/inventory');
    return res.data;
  },

  async getLowStockInventory() {
    const res = await api.get('/api/v1/vendors/inventory/low-stock');
    return res.data;
  },

  async getCamerasList() {
    const res = await api.get('/api/v1/cv/cameras');
    return res.data;
  },

  async getShuttleStatus() {
    const res = await api.get('/api/v1/predictions/transport', {
      data: { bus_loop_id: "LOOP_EAST", active_buses: 4, traffic_index: 3.5 }
    });
    return res.data;
  }
};
