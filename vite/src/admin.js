import { createApp } from 'vue'
import VideoPlayer from '@videojs-player/vue'
import OpenLayersMap from 'vue3-openlayers'
import VueSelect from "vue-select";
import AdminVideoPreviewApp from './AdminVideoPreviewApp.vue'
import AdminBeforeAfterPreviewApp from './AdminBeforeAfterPreviewApp.vue'
import AdminGalleryPreviewApp from './AdminGalleryPreviewApp.vue'
import OpenlayersPreviewApp from './OpenlayersPreviewApp.vue'
import OpenlayersFeaturesApp from './OpenlayersFeaturesApp.vue'
import PannellumPreviewApp from './PannellumPreviewApp.vue'
import PannellumFeaturesApp from './PannellumFeaturesApp.vue'

import './assets/admin.scss'
import './_common.js'

const ready = (fn) => document.readyState !== 'loading' ? fn() : document.addEventListener('DOMContentLoaded', fn)
ready(() => {
  document.querySelectorAll('.admin-video-preview-app').forEach((mountEl) => {
    const app = createApp(AdminVideoPreviewApp, { ...mountEl.dataset })
    app.use(VideoPlayer)
    app.mount(mountEl)
  })

  document.querySelectorAll('.admin-before-after-preview-app').forEach((mountEl) => {
    const app = createApp(AdminBeforeAfterPreviewApp, { ...mountEl.dataset })
    app.mount(mountEl)
  })

  document.querySelectorAll('.admin-gallery-preview-app').forEach((mountEl) => {
    const app = createApp(AdminGalleryPreviewApp, { ...mountEl.dataset })
    app.mount(mountEl)
  })

  document.querySelectorAll('.openlayers-preview-app').forEach((mountEl) => {
    const app = createApp(OpenlayersPreviewApp, { ...mountEl.dataset })
    app.use(OpenLayersMap)
    app.mount(mountEl)
  })

  document.querySelectorAll('.openlayers-features-app').forEach((mountEl) => {
    const app = createApp(OpenlayersFeaturesApp, { ...mountEl.dataset })
    app.use(OpenLayersMap)
    app.component("v-select", VueSelect)
    app.mount(mountEl)
  })

  document.querySelectorAll('.pannellum-preview-app').forEach((mountEl) => {
    const app = createApp(PannellumPreviewApp, { ...mountEl.dataset })
    app.mount(mountEl)
  })

  document.querySelectorAll('.pannellum-features-app').forEach((mountEl) => {
    const app = createApp(PannellumFeaturesApp, { ...mountEl.dataset })
    app.component("v-select", VueSelect)
    app.mount(mountEl)
  })
})