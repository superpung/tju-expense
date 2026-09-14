import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// The backend runs on :8000. Proxy /api during development so the frontend can
// call it same-origin without CORS friction.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
