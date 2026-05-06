import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const demoMode =
    env.REACT_APP_DEMO_MODE || process.env.REACT_APP_DEMO_MODE || env.VITE_DEMO_MODE || "false";
  const apiUrl =
    env.REACT_APP_API_URL || process.env.REACT_APP_API_URL || env.VITE_API_URL || "http://localhost:8000";
  const wsUrl =
    env.REACT_APP_WS_URL || process.env.REACT_APP_WS_URL || env.VITE_WS_URL || "ws://localhost:8000/ws/alerts";

  return {
    plugins: [react()],
    define: {
      __DEMO_MODE__: JSON.stringify(demoMode),
      __API_URL__: JSON.stringify(apiUrl),
      __WS_URL__: JSON.stringify(wsUrl)
    },
    server: {
      host: true,
      port: 3000
    }
  };
});
