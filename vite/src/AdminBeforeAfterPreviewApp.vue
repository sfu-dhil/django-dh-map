<script setup>
import { computed } from 'vue'
import { ImgComparisonSlider } from '@img-comparison-slider/vue'

const props = defineProps({
  before: {
    type: String,
    required: true,
  },
  after: {
    type: String,
    required: true,
  },
})

const websiteOrigin = window.location.origin
const beforeUrl = computed(() => `${websiteOrigin}${props.before}`)
const afterUrl = computed(() => `${websiteOrigin}${props.after}`)
</script>

<template>
  <div>
    <figure class="figure">
      <ImgComparisonSlider>
        <img slot="first" class="preview-image" :src="beforeUrl" />
        <img slot="second" class="preview-image" :src="afterUrl" />
      </ImgComparisonSlider>
      <figcaption class="figure-caption text-center"></figcaption>
    </figure>
  </div>
</template>

<style lang="scss" scoped>

  .preview-image {
    max-width: 400px;
    max-height: 100px;
  }
</style>