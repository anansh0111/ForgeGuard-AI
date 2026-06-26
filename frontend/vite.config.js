import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// BUG 4 FIX: Use ESM defineConfig properly, avoid CJS deprecation
export default defineConfig(({ mode }) => {
  return {
    plugins: [react()],
    build: {
      // Silence the chunk size warning — recharts + d3 are large but expected
      chunkSizeWarningLimit: 800,
      rollupOptions: {
        output: {
          manualChunks: {
            'react-vendor': ['react', 'react-dom', 'react-router-dom'],
            'chart-vendor': ['recharts'],
          },
        },
      },
    },
    server: {
      port: 3000,
      proxy: {
        '/api': {
          target: process.env.VITE_API_URL || 'http://localhost:8000',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ''),
        },
      },
    },
  }
})
