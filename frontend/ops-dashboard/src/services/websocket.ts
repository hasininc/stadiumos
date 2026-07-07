import { useOpsStore } from '../store/opsStore';

class DashboardWebSocketClient {
  private sockets: Map<string, WebSocket> = new Map();

  connectAll() {
    const store = useOpsStore.getState();
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;

    // 1. Crowd WebSockets connection channel
    const crowdSocket = new WebSocket(`${wsProtocol}//${host}/api/v1/crowd/ws`);
    crowdSocket.onopen = () => store.setWsConnected(true);
    crowdSocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.event === "crowd_updated") {
        // Fetch fresh heatmap values on changes
        store.updateCrowdMetrics([
          {
            zone_id: data.zone_id,
            zone_name: `Zone ${data.zone_id.split('_').pop()}`,
            occupancy_pct: data.occupancy_pct,
            headcount: data.headcount,
            status: data.status
          }
        ]);
      }
    };
    crowdSocket.onclose = () => store.setWsConnected(false);
    this.sockets.set('crowd', crowdSocket);

    // 2. Incident Emergencies WebSockets connection channel
    const emergencySocket = new WebSocket(`${wsProtocol}//${host}/api/v1/emergencies/ws`);
    emergencySocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.incident_id) {
        store.addIncident({
          id: data.incident_id,
          title: data.title || "Emergency Event",
          description: data.description || "Alert details",
          type: data.type || "Medical Emergency",
          severity: data.severity || "High",
          status: data.status || "Reported",
          reported_at: new Date().toISOString()
        });
      }
    };
    this.sockets.set('emergency', emergencySocket);

    // 3. AI Gateway recommendations WebSockets connection channel
    const aiSocket = new WebSocket(`${wsProtocol}//${host}/api/v1/ai/ws?session_id=global_ops_session`);
    aiSocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.agent_name) {
        store.addRecommendation({
          agent_name: data.agent_name,
          response_text: data.response_text,
          citations: data.citations,
          recommended_actions: data.recommended_actions
        });
      }
    };
    this.sockets.set('ai', aiSocket);
  }

  disconnectAll() {
    this.sockets.forEach((socket) => {
      socket.close();
    });
    this.sockets.clear();
  }
}

export const wsClient = new DashboardWebSocketClient();
export default wsClient;
