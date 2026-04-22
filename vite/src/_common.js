import './assets/pannellum/pannellum.js'
// make sure videojs plugins are working
import 'video.js'
// import 'videojs-contrib-quality-levels' // included in videojs-hls-quality-selector
import 'videojs-hls-quality-selector/src/plugin'
import 'videojs-theme-kit/videojs-skin.min.js'
import './_videojs-vtt-thumbnails.js'

// bootbox (jquery + global bootstrap)
import jquery from 'jquery'
window.jQuery = jquery
window.$ = jquery

import * as bootstrap from 'bootstrap'
window.bootstrap = bootstrap

import bootbox from 'bootbox'
window.bootbox = bootbox