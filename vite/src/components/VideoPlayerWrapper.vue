<script setup>
import { computed } from 'vue'

const video = defineModel('video')
const title = defineModel('title')
const thumbnail = defineModel('thumbnail')
const thumbnails_vtt = defineModel('thumbnails_vtt')

const isSafari = () => {
  const userAgent = navigator.userAgent;
  return userAgent.indexOf('Safari') > -1 && userAgent.indexOf('Chrome') === -1;
}

const videoSources = computed(() => {
  if (!video.value) {
    return []
  }
  const sources = [{
    src: video.value,
    type: 'application/dash+xml',
  }, {
    // we get a HLS playlist for free when generating the mpeg-dash with ffmpeg
    src: video.value.replace(/\/[^\/]+$/, '/master.m3u8'),
    type: 'application/x-mpegURL',
  }]
  return isSafari() ? sources.reverse() : sources
})
const videoPluginOptions = computed(() => {
  const pluginOptions = {
    qualityLevels: {},
    theme: { skin: 'slate' },
  }
  if (!isSafari()) {
    pluginOptions.hlsQualitySelector = { displayCurrentQuality: true }
  }
  if (thumbnails_vtt.value) {
    pluginOptions.vttThumbnails = { url: thumbnails_vtt.value }
  }
  return pluginOptions
})
const videoHtml5Options = computed(() => {
  const html5Options = {}
  if (isSafari()) {
    html5Options.nativeTextTracks = false
    html5Options.nativeAudioTracks = false
    // html5Options.nativeVideoTracks = false
  }
  return html5Options
})
</script>

<template>
  <video-player
    :sources="videoSources"
    :poster="thumbnail"
    :controls="true" :fluid="true" :aspectRatio="'16:9'"
    :disablePictureInPicture="true"
    :plugins="videoPluginOptions"
    :html5="videoHtml5Options"
  >
    <template v-slot="{ player, state }">
      <div class="vjs-title-bar" v-if="title">
        <div class="vjs-title-bar-title">
          {{ title }}
        </div>
      </div>
    </template>
  </video-player>
</template>

<style lang="scss" scoped>
</style>


