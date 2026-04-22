import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createWebHashHistory, createRouter } from 'vue-router'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import VideoPlayer from '@videojs-player/vue'
import OpenLayersMap from 'vue3-openlayers'
import MapRedirectDefault from './components/MapRedirectDefault.vue'
import MapView from './components/MapView.vue'
import ExampleApp from './ExampleApp.vue'
import ContentBlockApp from './ContentBlockApp.vue'

import './assets/example.scss'

// import 'videojs-contrib-quality-levels' // included in videojs-hls-quality-selector
import 'videojs-hls-quality-selector/src/plugin'
import 'videojs-theme-kit/videojs-skin.min.js'
import './_videojs-vtt-thumbnails.js'

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

const routes = [
  {
    path: '/',
    name: 'default',
    component: MapRedirectDefault,
  },
  {
    path: '/maps/:id',
    name: 'map',
    component: MapView,
  },
]
const router = createRouter({
  linkActiveClass: 'active',
  history: createWebHashHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    // always scroll to top
    return { top: 0 }
  },
})

const ready = (fn) => document.readyState !== 'loading' ? fn() : document.addEventListener('DOMContentLoaded', fn)
ready(() => {
  document.querySelectorAll('.example-app').forEach((mountEl) => {
    const app = createApp(ExampleApp, { ...mountEl.dataset })
    app.use(pinia)
    app.use(OpenLayersMap)
    app.use(VideoPlayer)
    app.use(router)
    app.mount(mountEl)
  })

  document.querySelectorAll('.content-blocks-app').forEach((mountEl) => {
    const app = createApp(ContentBlockApp, {
      ...mountEl.dataset,
      contentBlocks: JSON.parse(mountEl.dataset.contentBlocksJson),
    })
    app.use(pinia)
    app.use(VideoPlayer)
    app.mount(mountEl)
  })
})