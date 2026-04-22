<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useFeaturesStore } from '../stores/data.js'
import { useDisplayStore } from '../stores/display.js'
import { _stopAllMedia, toggleOffcanvas } from '../_utils.js'
import ContentBlock from './ContentBlock.vue'
import { IconResourceTypes } from '../_resourceTypes.js'

const {
  featureIdShown: shownId,
} = storeToRefs(useDisplayStore())

const object = await useFeaturesStore().getById(shownId.value)
const shown = computed(() => !!shownId.value)
const title = computed(() => {
  let str = object.title
  if (object.icon && object.icon.resourcetype === IconResourceTypes.numbered) {
    str = `${object.icon.number}. ${str}`
  }
  return str
})

const offCanvasRef = ref(null)
watch(shownId, (newValue, oldValue) => {
  if (newValue !== oldValue) {
    _stopAllMedia()
    toggleOffcanvas(offCanvasRef.value, newValue)
  }
})
onMounted(() => {
  _stopAllMedia()
  toggleOffcanvas(offCanvasRef.value, shown.value)
  offCanvasRef.value.addEventListener('hidden.bs.offcanvas', () => shownId.value = null)
})
</script>

<template>
  <div ref="offCanvasRef" class="offcanvas offcanvas-start" data-bs-scroll="true" data-bs-backdrop="false" tabindex="-1">
    <div class="offcanvas-header">
      <h1 class="offcanvas-title h1" v-html="title" />
      <button type="button" class="btn-close" data-bs-dismiss="offcanvas" aria-label="Close"></button>
    </div>
    <div class="offcanvas-body">
      <div v-if="object.content_blocks && object.content_blocks.length > 0">
        <ContentBlock v-for="contentBlock in object.content_blocks" :contentBlock="contentBlock" />
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.offcanvas {
  width: 50vmax !important;
}
</style>