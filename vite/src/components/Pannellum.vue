<!-- based on https://github.com/jarvisniu/vue-pannellum but modified to work better for my needs -->
<script setup>
import { ref, onMounted, onUnmounted, computed, watch, nextTick } from 'vue'
import { UseFullscreen } from '@vueuse/components'
import 'pannellum'


const viewer = defineModel('viewer')
const src = defineModel('src', { required: true })
const hfov = defineModel('hfov', { default: 75 })
const yaw = defineModel('yaw', { default: 0 })
const pitch = defineModel('pitch', { default: 0 })

const props = defineProps({
  preview: { type: String },
  autoLoad: { type: Boolean, default: true },
  draggable: { type: Boolean, default: true },
  mouseZoom: { type: Boolean, default: true },
  doubleClickZoom: { type: Boolean, default: true },
  showControls: { type: Boolean, default: true },
  compass: { type: Boolean, default: false },
  hotSpots: { type: Array, default: [] },
  minHfov: { type: Number, default: 50 },
  maxHfov: { type: Number, default: 120 },
  crossOrigin: {type: String, default: 'anonymous' },
})

const pannellumRef = ref(null)
const animationFrameId = ref(null)

const srcOption = computed(() => {
  if (typeof src.value === 'string') {
    return {
      type: 'equirectangular',
      panorama: src.value,
      hotSpots: props.hotSpots,
    }
  } else if (typeof src.value === 'object') {
    if (src.value.px && src.value.ny) {
      return {
        type: 'cubemap',
        cubeMap: [
          src.value.pz,
          src.value.px,
          src.value.nz,
          src.value.nx,
          src.value.py,
          src.value.ny,
        ],
        hotSpots: props.hotSpots,
      }
    } else if (src.value.scenes) {
      return {
        default: src.value.default,
        scenes: src.value.scenes,
      }
    } else {
      console.error('[vue-pannellum] Unknown src type')
    }
  } else {
    console.error('[vue-pannellum] Unknown src type: ' + typeof src.value)
  }
})

watch(src, (newValue, oldValue) => {
  if (newValue !== oldValue) {
    if (viewer.value) { viewer.value.destroy() }
    nextTick(() => loadPannellum())
  }
})
watch(hfov, (newValue, oldValue) => {
  if (newValue !== oldValue) {
    if (viewer.value) { viewer.value.setHfov(newValue, false) }
  }
})
watch(yaw, (newValue, oldValue) => {
  if (newValue !== oldValue) {
    if (viewer.value) { viewer.value.setYaw(newValue, false) }
  }
})
watch(pitch, (newValue, oldValue) => {
  if (newValue !== oldValue) {
    if (viewer.value) { viewer.value.setPitch(newValue, false) }
  }
})

const loadPannellum = () => {
  const options = {
    hfov: hfov.value,
    yaw: yaw.value,
    pitch: pitch.value,
    preview: props.preview,
    autoLoad: props.autoLoad,
    draggable: props.draggable,
    mouseZoom: props.mouseZoom,
    doubleClickZoom: props.doubleClickZoom,
    showControls: props.showControls,
    compass: props.compass,
    minHfov: props.minHfov,
    maxHfov: props.maxHfov,
    crossOrigin: props.crossOrigin,
    ...srcOption.value,
  }
  viewer.value = window.pannellum.viewer(pannellumRef.value, options)
}
const animationFrameLoop = () => {
  animationFrameId.value = window.requestAnimationFrame(animationFrameLoop)

  if (viewer.value) {
    const hfovUpdate = viewer.value.getHfov()
    const yawUpdate = viewer.value.getYaw()
    const pitchUpdate = viewer.value.getPitch()
    if (hfovUpdate != hfov.value) { hfov.value = hfovUpdate}
    if (yawUpdate != yaw.value) { yaw.value = yawUpdate}
    if (pitchUpdate != pitch.value) { pitch.value = pitchUpdate}
  }
}

const panUp = () => pitch.value += 10
const panDown = () => pitch.value -= 10
const panLeft = () => yaw.value -= 10
const panRight = () => yaw.value += 10
const zoomIn = () => hfov.value -= 10
const zoomOut = () => hfov.value += 10
onMounted(() => {
  loadPannellum()
  animationFrameId.value = window.requestAnimationFrame(animationFrameLoop)
})
onUnmounted(() => {
  if (viewer.value) {
    viewer.value.destroy()
    viewer.value = null
  }
  if (animationFrameId.value) { window.cancelAnimationFrame(animationFrameId.value) }
})
</script>

<template>
  <UseFullscreen v-slot="{ isFullscreen, toggle: toggleFullscreen }">
    <div class="z-0 position-absolute top-0 bottom-0 start-0 end-0">
      <div class="z-3 position-absolute bottom-0 start-50 translate-middle-x btn-group">
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
      <div class="z-3 position-absolute top-0 end-0 btn-group-vertical">
        <button @click="toggleFullscreen" type="button" class="btn btn-link text-light link-underline-opacity-0">
          <i v-if="!isFullscreen" class="bi bi-fullscreen"></i>
          <i v-if="isFullscreen" class="bi bi-fullscreen-exit"></i>
        </button>
      </div>
      <div
        ref="pannellumRef"
        class="z-1 vue-pannellum"
        @mouseup="onMouseUp"
        @touchmove="onTouchMove"
        @touchend="onTouchEnd"
      ></div>
    </div>
  </UseFullscreen>
</template>

<style lang="scss" scoped>
button.btn {
  font-size: 1.5em;
  text-shadow: -1px -1px 0 black, 1px -1px 0 black, -1px 1px 0 black, 1px 1px 0 black;
}
// pannellum
.vue-pannellum {
  &:deep() {
    /* these do not hide properly in tour mode */
    .pnlm-panorama-info,
    .pnlm-zoom-controls,
    .pnlm-fullscreen-toggle-button {
      display: none;
      visibility: hidden;
    }
    .pnlm-ui .pnlm-about-msg {
      display: none !important;
    }

    .hot-spot-wrapper {
      font-size: 16pm;
      font-weight: bold;
      position: relative;
    }
    .hot-spot-wrapper .number-label {
      color: white;
      font-size: 1em;
      z-index: 1001;
      position: absolute;
      left: 0;
      right: 0;
      bottom: calc(50% - 0.5em);
      text-align: center;
    }

    .hot-spot-wrapper i {
      font-size: 2em;
      z-index: 1000;
    }
    .view-hotspot .hot-spot-wrapper.hover i  {
        --bs-border-opacity: 1;
        -webkit-text-stroke-color: rgba(var(--bs-primary-rgb),var(--bs-border-opacity)) !important;
    }

    .view-hotspot .hot-spot-wrapper i,
    .edit-hotspot .hot-spot-wrapper i {
      -webkit-text-stroke-width: 2px;
      -webkit-text-stroke-color: white;
    }

    .view-hotspot .hot-spot-wrapper.hover i  {
        --bs-border-opacity: 1;
        -webkit-text-stroke-color: rgba(var(--bs-primary-rgb),var(--bs-border-opacity)) !important;
    }

    .edit-hotspot .hot-spot-wrapper {
        cursor: pointer;
        color: red;
    }

    .edit-hotspot .hot-spot-wrapper:hover::after {
        content: "\F287";
        font-family: bootstrap-icons !important;
        font-size: 0.6em;
        position: absolute;
        bottom: -0.3em;
        left: 0;
        right: 0;
        text-align: center;
        color: rgb(0, 153, 255);
        -webkit-text-stroke-width: 1px;
        -webkit-text-stroke-color: black;
    }
  }
}
</style>
