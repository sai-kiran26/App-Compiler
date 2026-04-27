import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/generate": "http://127.0.0.1:8000",
      "/validate": "http://127.0.0.1:8000",
      "/evaluate": "http://127.0.0.1:8000"
    }
  }
});
