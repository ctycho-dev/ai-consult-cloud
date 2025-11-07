import {defineConfig, loadEnv} from 'vite'
// import react from '@vitejs/plugin-react'
import path from "path";
import tailwindcss from '@tailwindcss/vite'

export default defineConfig(({ command, mode, isSsrBuild, isPreview }) => {
  const env = loadEnv(mode, process.cwd())

  return {
    base: '/',
    server: {
      proxy: {
        "/api": {
          target: `http://${env.VITE_HOST}/api`,
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, '')
        },
        "/ws": {
          target: `ws://${env.VITE_HOST}`,
          ws: true,
          changeOrigin: true,
          // secure: isSecure,
          rewrite: (path) => path.replace(/^\/ws/, '/ws')
        },
      },
    },
    plugins: [
      // react(),
      tailwindcss()
    ],
    resolve: {
      alias: {
        '@tabler/icons-react': '@tabler/icons-react/dist/esm/icons/index.mjs',
        "@": path.resolve(__dirname, "./src"),
      },
    },
  }
})
