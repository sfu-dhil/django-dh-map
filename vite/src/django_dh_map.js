import { createApp } from 'vue'
import VideoPlayer from '@videojs-player/vue'
import OpenLayersMap from 'vue3-openlayers'
import AdminVideoPreviewApp from './AdminVideoPreviewApp.vue'
import AdminBeforeAfterPreviewApp from './AdminBeforeAfterPreviewApp.vue'
import OverheadPreviewApp from './OverheadPreviewApp.vue'
import PanoramaPreviewApp from './PanoramaPreviewApp.vue'


// include global css (boostrap modal backdrops and tooltips are in here)
import './assets/django_dh_map.scss'

// make sure videojs plugins are working
import 'video.js'
// import 'videojs-contrib-quality-levels' // included in videojs-hls-quality-selector
import 'videojs-hls-quality-selector/src/plugin'
import 'videojs-theme-kit/videojs-skin.min.js'
import './videojs-vtt-thumbnails.js'

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

  document.querySelectorAll('.overhead-map-preview-app').forEach((mountEl) => {
    const app = createApp(OverheadPreviewApp, { ...mountEl.dataset })
    app.use(OpenLayersMap)
    app.mount(mountEl)
  })

  document.querySelectorAll('.panorama-map-preview-app').forEach((mountEl) => {
    const app = createApp(PanoramaPreviewApp, { ...mountEl.dataset })
    app.mount(mountEl)
  })
})