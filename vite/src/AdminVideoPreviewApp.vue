<script setup>
import { computed } from 'vue'
import VideoPlayerWrapper from './components/VideoPlayerWrapper.vue'

const props = defineProps({
  video: {
    type: String,
    required: true,
  },
  title: {
    type: String,
  },
  thumbnail: {
    type: String,
  },
  thumbnailsVtt: {
    type: String,
  },
})

const websiteOrigin = window.location.origin
const videoUrl = computed(() => `${websiteOrigin}${props.video}`)
const thumbnailUrl = computed(() => props.thumbnail ? `${websiteOrigin}${props.thumbnail}` : null)
const thumbnailsVttUrl = computed(() => props.thumbnailsVtt ? `${websiteOrigin}${props.thumbnailsVtt}` : null)
</script>

<template>
  <VideoPlayerWrapper
    :video="videoUrl"
    :title="title"
    :thumbnail="thumbnailUrl"
    :thumbnails_vtt="thumbnailsVttUrl"
  />
</template>

<style scoped>
</style>