<script setup>
import { ContentBlockResourceTypes } from '../_resourceTypes.js'
import Image from './content_blocks/Image.vue'
import ImageGallery from './content_blocks/ImageGallery.vue'
import BeforeAndAfterImage from './content_blocks/BeforeAndAfterImage.vue'
import VideoPlayerWrapper from './content_blocks/VideoPlayerWrapper.vue'

const props = defineProps({
  contentBlock: { type: Object, required: true },
})
</script>

<template>
  <div class="content-block mb-2">
    <div v-if="contentBlock.resourcetype === ContentBlockResourceTypes.richText && contentBlock.content" v-html="contentBlock.content" />
    <Image v-if="contentBlock.resourcetype === ContentBlockResourceTypes.image && contentBlock.original && contentBlock.web_resolution" :object="contentBlock" />
    <ImageGallery v-if="contentBlock.resourcetype === ContentBlockResourceTypes.imageGallery && contentBlock.images.length > 0" :object="contentBlock" />
    <BeforeAndAfterImage v-if="contentBlock.resourcetype === ContentBlockResourceTypes.beforeAndAfterImage && contentBlock.before_web_resolution && contentBlock.after_web_resolution" :object="contentBlock" />
    <VideoPlayerWrapper
      v-if="contentBlock.resourcetype === ContentBlockResourceTypes.video && contentBlock.video"
      :video="contentBlock.video"
      :title="contentBlock.name"
      :thumbnail="contentBlock.thumbnail"
      :thumbnails_vtt="contentBlock.thumbnails_vtt"
    />
    <audio
      v-if="contentBlock.resourcetype === ContentBlockResourceTypes.audio && contentBlock.audio"
      :src="contentBlock.audio" controls preload="metadata" class="w-100"
    />
  </div>
</template>

<style lang="scss" scoped>
</style>