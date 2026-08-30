import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Set VITE_API_TARGET if the backend isn't on the default port (e.g. something
// else already owns 8000 on this machine).
const target = process.env.VITE_API_TARGET || "http://127.0.0.1:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // Forward /api calls to the FastAPI backend so there's no CORS dance in dev.
    proxy: { "/api": target },
  },
});
