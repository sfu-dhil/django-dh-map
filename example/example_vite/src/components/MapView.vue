<script setup>
import { ref, watch, computed, nextTick, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { Tooltip } from 'bootstrap'
import { useFullscreen } from '@vueuse/core'
import { _stopAllMedia } from '../_utils.js'
import LoadingDots from './LoadingDots.vue'
import { useMapsStore, useFeaturesStore } from '../stores/data.js'
import { useDisplayStore, useDisplayOpenlayersStore, useDisplayPannellumStore } from '../stores/display.js'
import { MapResourceTypes } from '../_resourceTypes.js'
import Openlayers from './maps/Openlayers.vue'
import Pannellum from './maps/Pannellum.vue'

// make sure features and maps are loaded
const maps = await useMapsStore().getAll()
const features = await useFeaturesStore().getAll()

const {
  objectMap: mapObjectMap,
} = storeToRefs(useMapsStore())
const {
  rotation,
} = storeToRefs(useDisplayOpenlayersStore())

const route = useRoute()
const objectId = computed(() => route.params.id ? Number(route.params.id) : undefined )
const map = computed(() => objectId.value && mapObjectMap.value.has(objectId.value) ? mapObjectMap.value.get(objectId.value) : undefined)

const mapWrapperRef = ref(null)
const { isFullscreen, toggle: toggleFullscreen } = useFullscreen(mapWrapperRef)
const mapRef = ref(null)
const resetTooltips = () => {
  nextTick(() => {
    mapWrapperRef.value.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(
      (tooltipTriggerEl) => Tooltip.getOrCreateInstance(tooltipTriggerEl, {container: mapWrapperRef.value}).hide()
    )
  })
}
watch(isFullscreen, (oldValue, newValue) => {
  if (newValue != oldValue) { resetTooltips() }
})
watch(mapRef, (oldValue, newValue) => {
  if (newValue != oldValue) { resetTooltips() }
})
watch(() => route.params.id, (newValue, oldValue) => {
  if (newValue !== oldValue) { _stopAllMedia() }
})
</script>

<template>
  <div class="position-relative w-100 h-100">
    <nav class="navbar navbar-expand-lg position-absolute z-3 top-0 start-0 end-0 bg-body-tertiary bg-opacity-50">
      <div class="container-fluid d-flex justify-content-between">
        <a class="navbar-brand" href="/">Example App</a>
        <span class="navbar-text" v-if="map">{{ map.label }}</span>
        <span class="navbar-text"></span>
      </div>
    </nav>
    <div ref="mapWrapperRef" class="position-absolute z-1 w-100 h-100">
      <Suspense v-if="map && [MapResourceTypes.overheadImageMap, MapResourceTypes.xyzMap].includes(map.resourcetype)">
        <Openlayers ref="mapRef" :key="map.id" :mapId="map.id" />
        <template #fallback><LoadingDots /></template>
      </Suspense>
      <Suspense v-if="map && map.resourcetype === MapResourceTypes.panoramaImageMap">
        <Pannellum ref="mapRef" :key="map.id" :mapId="map.id" />
        <template #fallback><LoadingDots /></template>
      </Suspense>
      <div v-if="mapRef" class="z-3 position-absolute bottom-0 start-50 translate-middle-x btn-group text-center">
        <button v-if="mapRef.panUp" @click="mapRef.panUp"
          type="button" class="btn btn-link text-light link-underline-opacity-0"
          data-bs-toggle="tooltip" data-bs-trigger="hover" data-bs-title="Pan Up"
        >
          <i class="bi bi-arrow-up"></i>
        </button>
        <button v-if="mapRef.panDown" @click="mapRef.panDown"
          type="button" class="btn btn-link text-light link-underline-opacity-0"
          data-bs-toggle="tooltip" data-bs-trigger="hover" data-bs-title="Pan Down"
        >
          <i class="bi bi-arrow-down"></i>
        </button>
        <button v-if="mapRef.panLeft" @click="mapRef.panLeft"
          type="button" class="btn btn-link text-light link-underline-opacity-0"
          data-bs-toggle="tooltip" data-bs-trigger="hover" data-bs-title="Pan Left"
        >
          <i class="bi bi-arrow-left"></i>
        </button>
        <button v-if="mapRef.panRight" @click="mapRef.panRight"
          type="button" class="btn btn-link text-light link-underline-opacity-0"
          data-bs-toggle="tooltip" data-bs-trigger="hover" data-bs-title="Pan Right"
        >
          <i class="bi bi-arrow-right"></i>
        </button>
        <button v-if="mapRef.zoomIn" @click="mapRef.zoomIn"
          type="button" class="btn btn-link text-light link-underline-opacity-0"
          data-bs-toggle="tooltip" data-bs-trigger="hover" data-bs-title="Zoom In"
        >
          <i class="bi bi-plus-lg"></i>
        </button>
        <button v-if="mapRef.zoomOut" @click="mapRef.zoomOut"
          type="button" class="btn btn-link text-light link-underline-opacity-0"
          data-bs-toggle="tooltip" data-bs-trigger="hover" data-bs-title="Zoom Out"
        >
          <i class="bi bi-dash-lg"></i>
        </button>
      </div>
      <div v-if="mapRef" class="z-3 position-absolute top-0 end-0 btn-group-vertical text-center"
        :class="{ 'top-left-btn-group-offset': !isFullscreen }"
      >
        <button @click="() => { toggleFullscreen(); resetTooltips() }"
          type="button" class="btn btn-link text-light link-underline-opacity-0"
          data-bs-toggle="tooltip" data-bs-trigger="hover" data-bs-title="Toggle Fullscreen Mode"
        >
          <i v-if="!isFullscreen" class="bi bi-fullscreen"></i>
          <i v-if="isFullscreen" class="bi bi-fullscreen-exit"></i>
        </button>
        <button v-if="map && [MapResourceTypes.overheadImageMap, MapResourceTypes.xyzMap].includes(map.resourcetype) && mapRef.resetRotation" @click="mapRef.resetRotation"
          type="button" class="rotation-btn btn btn-link text-light link-underline-opacity-0"
          :class="{'d-none': rotation === (map.properties?.initial?.rotation || 0) }"
          data-bs-toggle="tooltip" data-bs-trigger="hover" data-bs-title="Reset Rotation"
        >
          <i
            class="rotation-correction fa-solid fa-compass"
            :style="{
              'transform': `rotate(${(315 + (rotation - (map.properties?.initial?.rotation || 0)) * (180 / Math.PI)) % 360}deg)`
            }"
          ></i>
        </button>
      </div>
      <div v-if="!isFullscreen" class="z-3 position-absolute bottom-0 start-0 btn-group-vertical text-center">
        <button @click="() => useDisplayStore().showInfoPageSelectionSidebar()"
          type="button" class="btn btn-link text-light link-underline-opacity-0"
          data-bs-toggle="tooltip" data-bs-trigger="hover" data-bs-title="Show Info Pages"
        >
          <i class="bi bi-chat-left-text-fill"></i>
        </button>
        <button @click="() => useDisplayStore().showFeatureSelectionSidebar()"
          type="button" class="btn btn-link text-light link-underline-opacity-0"
          data-bs-toggle="tooltip" data-bs-trigger="hover" data-bs-title="Show Features"
        >
          <i class="bi bi-card-list"></i>
        </button>
        <button @click="() => useDisplayStore().showMapSelectSidebar()"
          type="button" class="btn btn-link text-light link-underline-opacity-0"
          data-bs-toggle="tooltip" data-bs-trigger="hover" data-bs-title="Show Maps"
        >
          <i class="fa-solid fa-map-location-dot"></i>
        </button>
      </div>
      <div class="z-3 position-absolute bottom-0 end-0 d-flex flex-column" v-if="map">
        <span class="badge text-bg-light ms-auto me-1 mb-1" v-if="!!map.attributions" v-html="map.attributions" />
        <span class="badge text-bg-light ms-auto me-1 mb-1" v-if="!!map.date_taken" v-html="`Taken on ${new Date(map.date_taken).toLocaleDateString()}`" />
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.top-left-btn-group-offset {
  margin-top: 4em;
}
button.btn.btn-link {
  font-size: 1.5em;
  text-shadow: -1px -1px 0 black, 1px -1px 0 black, -1px 1px 0 black, 1px 1px 0 black;
}
.rotation-correction {
  transform: rotate(315deg);
}
</style>