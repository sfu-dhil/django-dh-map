<script setup>
import { ref, onMounted, watch, computed, nextTick } from 'vue'
import { storeToRefs } from 'pinia'
import { useRoute } from 'vue-router'
import { useMapsStore } from '../stores/data.js'
import { useDisplayStore } from '../stores/display.js'
import { MapResourceTypes } from '../_resourceTypes.js'
import { toggleOffcanvas } from '../_utils.js'

const {
  mapSelectSidebarShown: shown,
} = storeToRefs(useDisplayStore())

// make sure features and maps are loaded
const objects = await useMapsStore().getAll()
const offCanvasRef = ref(null)

watch(shown, (newValue, oldValue) => {
  if (newValue !== oldValue) { toggleOffcanvas(offCanvasRef.value, newValue) }
})
onMounted(() => {
  toggleOffcanvas(offCanvasRef.value, shown.value)
  offCanvasRef.value.addEventListener('hidden.bs.offcanvas', () => shown.value = false)
  offCanvasRef.value.addEventListener('shown.bs.offcanvas', () => shown.value = true)
})
</script>

<template>
  <div ref="offCanvasRef" class="offcanvas offcanvas-start" data-bs-scroll="true" data-bs-backdrop="false" tabindex="-1">
    <div class="offcanvas-header">
      <h2 class="offcanvas-title h5">Maps</h2>
      <button type="button" class="btn-close" data-bs-dismiss="offcanvas" aria-label="Close"></button>
    </div>
    <div class="offcanvas-body" v-if="shown">
      <div class="list-group">
        <RouterLink
          v-for="object in objects"
          :key="object.id"
          class="list-group-item list-group-item-action"
          :to="{ name: 'map', params: { id: object.id } }"
        >
          <i v-if="[MapResourceTypes.xyzMap, MapResourceTypes.overheadImageMap].includes(object.resourcetype)" class="bi bi-pin-map-fill"></i>
          <i v-if="object.resourcetype === MapResourceTypes.panoramaImageMap" class="fa-solid fa-street-view"></i>
          {{ object.label }}
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
</style>


