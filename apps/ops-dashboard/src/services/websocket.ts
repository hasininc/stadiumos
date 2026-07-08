import { useOpsStore } from '../store/opsStore';
import { dashboardService } from './dashboard';

class DashboardWebSocketClient {
  private sockets: Map<string, WebSocket> = new Map();

  connectAll() {
    const store = useOpsStore.getState();
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;

    const crowdSocket = new WebSocket(`${wsProtocol}//${host}/api/v1/crowd/ws`);
    crowdSocket.onopen = () => store.setWsConnected(true);
    crowdSocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.event === 'crowd_updated' && data.zone_id) {
        store.updateCrowdMetrics([
          {
            zone_id: data.zone_id,
            zone_name: data.zone_name || data.zone_id,
            occupancy_pct: data.occupancy_pct ?? 0,
            headcount: data.headcount ?? 0,
            status: data.status || 'Normal',
          },
        ]);
      }
    };
    crowdSocket.onclose = () => store.setWsConnected(false);
    this.sockets.set('crowd', crowdSocket);

    const emergencySocket = new WebSocket(`${wsProtocol}//${host}/api/v1/emergencies/ws`);
    emergencySocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.incident_id || data.id) {
        store.addIncident({
          id: data.incident_id || data.id,
          title: data.title,
          description: data.description,
          type: data.type,
          severity: data.severity,
          status: data.status,
          zone_id: data.zone_id,
          reported_at: data.reported_at || new Date().toISOString(),
        });
      }
    };
    this.sockets.set('emergency', emergencySocket);
  }

  disconnectAll() {
    this.sockets.forEach((socket) => socket.close());
    this.sockets.clear();
  }
}

export const wsClient = new DashboardWebSocketClient();
export default wsClient;
