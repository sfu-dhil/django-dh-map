<script setup>
import { useDisplayImageModalStore } from '../../stores/display.js'

const props = defineProps({
  object: { type: Object, required: true },
})
</script>

<template>
  <figure class="figure w-100">
    <img
      class="figure-img w-100 object-fit-contain m-0"
      :src="object.web_resolution"
      :alt="object.description || ''"
      loading="lazy" fetchpriority="low"
      @click="() => useDisplayImageModalStore().showImage(object)"
    >
    <figcaption class="figure-caption text-center" v-if="object.name" v-html="object.name" />
  </figure>
</template>

<style lang="scss" scoped>
figure img {
  cursor: pointer;
  max-height: 1080px;
}
</style>