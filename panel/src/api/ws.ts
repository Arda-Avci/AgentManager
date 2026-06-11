const WS_BASE = `ws://${window.location.hostname}:3010/api/v1`;

export function connectLogStream(
  agentId: string,
  onMessage: (event: string, data: unknown) => void,
  onError?: (err: Event) => void
): WebSocket {
  const ws = new WebSocket(`${WS_BASE}/ws/logs/${agentId}`);

  ws.onmessage = (event) => {
    try {
      const parsed = JSON.parse(event.data);
      onMessage(parsed.event || "message", parsed.data || parsed);
    } catch {
      onMessage("message", event.data);
    }
  };

  ws.onerror = (err) => onError?.(err);

  return ws;
}
