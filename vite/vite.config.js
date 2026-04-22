import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  server: {
    port: 5173,
    host: true,
    strictPort: true,
    origin: 'http://localhost:5173',
    cors: 'http://localhost:8080',
  },
  root: resolve("./src"),
  base: "/static/django_dh_map/admin/dist/",
  build: {
    manifest: 'manifest.json',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        django_dh_map: resolve('./src/django_dh_map.js'),
      },
      output: {
        dir: resolve("../django_dh_map/static/django_dh_map/admin/dist"),
        entryFileNames: `[name].js`,
        chunkFileNames: `[name].js`,
        assetFileNames: `[name].[ext]`,
      }
    },
  },
  css: {
    preprocessorOptions: {
      scss: {
        api: 'legacy',
        quietDeps: true,
        silenceDeprecations: ['import', 'legacy-js-api', 'color-functions', 'global-builtin'],
      },
    }
  },
  plugins: [
    vue({
      template: {
        compilerOptions: {
          isCustomElement: (tag) => tag.startsWith('media-'),
        },
      },
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})
