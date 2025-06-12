import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import svgr from 'vite-plugin-svgr';  // Import the plugin for SVG support
import EnvironmentPlugin from 'vite-plugin-environment';  // Import the environment plugin

export default defineConfig({
  plugins: [
    react(),  // Keeps the React plugin functionality
    svgr(),   // Keeps the SVG handling plugin
    EnvironmentPlugin("all")  // Adds the environment variables plugin
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),  // Aliasing '@' to './src'
    },
  },
  css: {
    // No additional configuration needed for CSS
  },
});