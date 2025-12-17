import { reactRouter } from "@react-router/dev/vite";
import tailwindcss from "@tailwindcss/vite";
import { defineConfig } from "vite";
import tsconfigPaths from "vite-tsconfig-paths";

export default defineConfig({
  // Spread multi-plugin factories so the React Router CLI can detect them.
  plugins: [...reactRouter(), ...tailwindcss(), tsconfigPaths()],
  server: {
    port: 3000,
  },
});
