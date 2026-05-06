import { useEffect, useRef, useState } from "react";

export function useWebSocket({ url, onMessage, enabled = true }) {
  const [status, setStatus] = useState("disconnected");
  const socketRef = useRef(null);
  const retryRef = useRef(0);
  const timerRef = useRef(null);

  useEffect(() => {
    if (!enabled) {
      return undefined;
    }

    let cancelled = false;

    const connect = () => {
      if (cancelled) {
        return;
      }

      setStatus("connecting");
      const socket = new WebSocket(url);
      socketRef.current = socket;

      socket.onopen = () => {
        retryRef.current = 0;
        setStatus("connected");
      };

      socket.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data);
          if (onMessage) {
            onMessage(parsed);
          }
        } catch (error) {
          // Ignore malformed payloads
        }
      };

      socket.onclose = () => {
        setStatus("disconnected");
        const backoff = Math.min(10000, 500 * Math.pow(2, retryRef.current));
        retryRef.current += 1;
        timerRef.current = window.setTimeout(connect, backoff);
      };

      socket.onerror = () => {
        socket.close();
      };
    };

    connect();

    return () => {
      cancelled = true;
      if (timerRef.current) {
        window.clearTimeout(timerRef.current);
      }
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [enabled, onMessage, url]);

  return { status };
}
