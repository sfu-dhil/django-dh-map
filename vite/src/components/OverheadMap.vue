<script setup>
import { ref, inject, onMounted, watch, nextTick } from 'vue'
import { UseFullscreen } from '@vueuse/components'
import { Style, Text, Fill, Stroke } from "ol/style"
import { easeOut } from "ol/easing"
import { Collection } from 'ol'
import { transform } from 'ol/proj'

const center = defineModel('center', { default: [0,0] })
const rotation = defineModel('rotation', { default: 0 })
const minZoom = defineModel('minZoom', { default: 1 })
const maxZoom = defineModel('maxZoom', { default: 5 })
const zoom = defineModel('zoom', { default: 2.5 })
const points = defineModel('points', { default: [] })

const props = defineProps({
  tilesDir: { type: String, required: true },
  tileFormat: { type: String, required: true },
  tileGrid: { type: Object, required: true },
  projection: { type: Object, required: true },
})

const mapRef = ref(null)
const resetRotationButtonContentRef = ref(null)

const panUp = () => mapRef.value.map.getView().animate({ center: [
    mapRef.value.map.getView().getCenter()[0],
    mapRef.value.map.getView().getCenter()[1] + (100 * mapRef.value.map.getView().getResolution())
  ], easing: easeOut })
const panDown = () => mapRef.value.map.getView().animate({ center: [
    mapRef.value.map.getView().getCenter()[0],
    mapRef.value.map.getView().getCenter()[1] - (100 * mapRef.value.map.getView().getResolution())
  ], easing: easeOut })
const panLeft = () => mapRef.value.map.getView().animate({ center: [
    mapRef.value.map.getView().getCenter()[0] - (100 * mapRef.value.map.getView().getResolution()),
    mapRef.value.map.getView().getCenter()[1]
  ], easing: easeOut })
const panRight = () => mapRef.value.map.getView().animate({ center: [
    mapRef.value.map.getView().getCenter()[0] + (100 * mapRef.value.map.getView().getResolution()),
    mapRef.value.map.getView().getCenter()[1]
  ], easing: easeOut })
const zoomIn = () => zoom.value += 1
const zoomOut = () => zoom.value -= 1
const resetRotation = () => mapRef.value.map.getView().animate({ rotation: 0, easing: easeOut })
const updateRotation = (event) => {
  console.log('updateRotation', event.target.getRotation())
  resetRotationButtonContentRef.value.style.transform = `rotate(${(315 + (event.target.getRotation() * (180 / Math.PI))) % 360}deg)`
}
const {
  pointerMove: pointerMoveCondition,
  click: clickCondition,
} = inject("ol-selectconditions")
const websiteOrigin = window.location.origin
</script>

<template>
  <UseFullscreen v-slot="{ isFullscreen, toggle: toggleFullscreen }">
    <div class="z-0 position-absolute top-0 bottom-0 start-0 end-0 overflow-hidden">
      <ol-map
        ref="mapRef"
        class="overhead-map z-1 w-100 h-100 position-absolute"
        :loadTilesWhileAnimating="true"
        :loadTilesWhileInteracting="true"
        :controls="[]"
      >
        <ol-view
          :center="center"
          :rotation="rotation"
          :zoom="zoom"
          :minZoom="minZoom"
          :maxZoom="maxZoom"
          :projection="projection"
          @change:rotation="updateRotation"
        />

        <ol-tile-layer>
          <ol-source-xyz
            :url="`${websiteOrigin}${tilesDir}/{z}/{x}/{y}.${tileFormat}`"
            :tileGrid="tileGrid"
            :projection="projection"
          />
        </ol-tile-layer>

        <ol-interaction-drag-rotate-and-zoom />
        <div class="z-3 position-absolute bottom-0 start-50 translate-middle-x btn-group text-center">
          <button @click="panUp" type="button" class="btn btn-link text-light link-underline-opacity-0">
            <i class="bi bi-arrow-up"></i>
          </button>
          <button @click="panDown" type="button" class="btn btn-link text-light link-underline-opacity-0">
            <i class="bi bi-arrow-down"></i>
          </button>
          <button @click="panLeft" type="button" class="btn btn-link text-light link-underline-opacity-0">
            <i class="bi bi-arrow-left"></i>
          </button>
          <button @click="panRight" type="button" class="btn btn-link text-light link-underline-opacity-0">
            <i class="bi bi-arrow-right"></i>
          </button>
          <button @click="zoomIn" type="button" class="btn btn-link text-light link-underline-opacity-0">
            <i class="bi bi-plus-lg"></i>
          </button>
          <button @click="zoomOut" type="button" class="btn btn-link text-light link-underline-opacity-0">
            <i class="bi bi-dash-lg"></i>
          </button>
        </div>
        <div class="z-3 position-absolute top-0 end-0 btn-group-vertical text-center">
          <button @click="toggleFullscreen" type="button" class="btn btn-link text-light link-underline-opacity-0">
            <i v-if="!isFullscreen" class="bi bi-fullscreen"></i>
            <i v-if="isFullscreen" class="bi bi-fullscreen-exit"></i>
          </button>
          <button @click="resetRotation" type="button" class="rotation-btn btn btn-link text-light link-underline-opacity-0">
            <i ref="resetRotationButtonContentRef" class="rotation-correction fa-solid fa-compass"></i>
          </button>
        </div>
      </ol-map>
    </div>
  </UseFullscreen>
</template>

<style lang="scss" scoped>
button.btn {
  font-size: 1.5em;
  text-shadow: -1px -1px 0 black, 1px -1px 0 black, -1px 1px 0 black, 1px 1px 0 black;
}

.overhead-map {
  cursor: grab;

  &:active {
    cursor: grabbing;
  }

  &:deep() {
    .ol-control button {
      font-size: 1.5em;
      pointer-events: auto;
      i {
        cursor: pointer;
      }
    }
    .show-menu-control {
      left: .5em;
      top: 5.0em;
      z-index: 2;
    }
    .show-welcome-control {
      left: .5em;
      top: 7.5em;
      z-index: 2;
    }
    .select-view-control {
      left: .5em;
      top: 10em;
      z-index: 2;
    }
    .show-date-taken {
      bottom: 0.25em;
      right: 0.25em;
      z-index: 2;
      width: fit-content;
    }
    .show-date-taken button {
      font-size: 0.8em;
      font-weight: normal;
      padding-left: 0.5em;
      padding-right: 0.5em;
      width: fit-content;
      border-radius: 0.5em;
    }
    .rotation-correction {
      transform: rotate(315deg);
    }
  }
}
</style>