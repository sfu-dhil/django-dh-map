<script setup>
import { ImgComparisonSlider } from '@img-comparison-slider/vue'
const props = defineProps({
  object: { type: Object, required: true },
})
</script>

<template>
  <figure class="figure w-100">
    <ImgComparisonSlider class="w-100">
      <img
        slot="first"
        class="w-100 object-fit-contain m-0" loading="lazy" fetchpriority="low"
        :src="object.before_web_resolution" :alt="object.before_description"
      >
      <img
        slot="second"
        class="w-100 object-fit-contain m-0" loading="lazy" fetchpriority="low"
        :src="object.after_web_resolution" :alt="object.after_description"
      >
    </ImgComparisonSlider>
    <figcaption class="figure-caption text-center" v-bind="object.caption">{{ object.caption }}</figcaption>
  </figure>
</template>

<style lang="scss" scoped>
</style>