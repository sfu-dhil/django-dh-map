<script setup>
import { ref, onMounted, onUnmounted, computed, watch, nextTick } from 'vue'
import { storeToRefs } from 'pinia'
import { UseMouseInElement } from '@vueuse/components'
import { useRouter } from 'vue-router'
import { _getApiResource } from '../../_utils.js'
import { useMapsStore, useFeaturesStore } from '../../stores/data.js'
import { useDisplayStore, useDisplayPannellumStore } from '../../stores/display.js'
import { MapGeojsonResourceTypes, IconResourceTypes } from '../../_resourceTypes.js'

const router = useRouter()
const {
  objectMap: mapsObjectMap,
} = storeToRefs(useMapsStore())
const {
  objectMap: featuresObjectMap,
} = storeToRefs(useFeaturesStore())
const {
  featureIdHover,
} = storeToRefs(useDisplayStore())
const {
  hfov,
  yaw,
  pitch,
} = storeToRefs(useDisplayPannellumStore())

const props = defineProps({
  mapId: { type: Number, required: true },
})
const map = await useMapsStore().getById(props.mapId)
useDisplayPannellumStore().init(map)
const websiteOrigin = window.location.origin
const viewer = ref(null)

const pannellumRef = ref(null)
const animationFrameId = ref(null)
const hoverFeatureTooltipLabel = ref(null)

const hotSpotsGeoJson = await _getApiResource(`${websiteOrigin}/api/maps/${map.id}/geojson`)
const hotSpotTooltip = (hotSpotDiv, { id, properties }) => {
  if (properties.resourcetype === MapGeojsonResourceTypes.feature) {
    return hotSpotFeatureTooltip(hotSpotDiv, { properties })
  } else if (properties.resourcetype === MapGeojsonResourceTypes.transition) {
    return hotSpotMapTransitionTooltip(hotSpotDiv, { properties })
  } else if (properties.resourcetype === MapGeojsonResourceTypes.label) {
    return hotSpotLabelTooltip(hotSpotDiv, { properties })
  } else {
    // default
    hotSpotDiv.innerHTML = ''
  }
}
const showFeature = (event, { featureId })  => {
  const feature = featuresObjectMap.value.get(featureId)
  useDisplayStore().showFeature(feature)
}
const showMap = (event, { mapId })  => {
  router.push({ name: 'map', params: { id: mapId } })
}
const hotSpots = hotSpotsGeoJson.features.reduce((results, feature) => {
  let coordinates = []
  if (feature.geometry && feature.geometry.type === 'MultiPoint') {
    coordinates = feature.geometry.coordinates
  } else if (feature.geometry && feature.geometry.type === 'Point') {
    coordinates.push(feature.geometry.coordinates)
  }
  // concat results with new coordinates
  return [...results, ...coordinates.map((coords) => {
    const properties = feature.properties
    const hotSpot = {
      pitch: coords[0],
      yaw: coords[1],
      createTooltipFunc: hotSpotTooltip,
      createTooltipArgs: { properties },
      draggable: false,
      cssClass: 'view-hot-spot',
    }
    if (properties.resourcetype === MapGeojsonResourceTypes.feature) {
      hotSpot.clickHandlerFunc = showFeature
      hotSpot.clickHandlerArgs = { featureId: properties.feature }
    } else if (properties.resourcetype === MapGeojsonResourceTypes.transition) {
      hotSpot.clickHandlerFunc = showMap
      hotSpot.clickHandlerArgs = { mapId: properties.map }
    }
    return hotSpot
  })]
}, [])
const hotSpotFeatureTooltip = (hotSpotDiv, { properties }) => {
  const feature = featuresObjectMap.value.get(properties.feature)
  const icon = feature?.icon
  if (icon && icon.resourcetype === IconResourceTypes.image) {
    hotSpotDiv.innerHTML = `
      <div class="hot-spot-wrapper hot-spot hot-spot-icon-image border border-white border-2 rounded-circle" data-feature-id="${feature.id}">
        <img class="rounded-circle m-1" draggable="false" src="${icon.icon_thumbnail}" />
      </div>
    `
  } else if (icon && icon.resourcetype === IconResourceTypes.numbered) {
    hotSpotDiv.innerHTML = `
      <div class="hot-spot-wrapper hot-spot hot-spot-icon-numbered" data-feature-id="${feature.id}">
        <i class="fa-solid fa-location-pin"></i>
        <span class="number-label">${icon.number}</span>
      </div>
    `
  } else {
    hotSpotDiv.innerHTML = `
      <div class="hot-spot-wrapper hot-spot hot-spot-icon-default" data-feature-id="${feature.id}">
        <i class="bi bi-circle-fill"></i>
      </div>
    `
  }
  hotSpotDiv.addEventListener('mouseover', () => {
    hoverFeatureTooltipLabel.value = feature.title
    featureIdHover.value = feature.id
  })
  hotSpotDiv.addEventListener('mouseout', () => {
    hoverFeatureTooltipLabel.value = null
    featureIdHover.value = null
  })
}
const hotSpotMapTransitionTooltip = (hotSpotDiv, { properties }) => {
  const map = mapsObjectMap.value.get(properties.map)
  hotSpotDiv.innerHTML = `
    <div class="hot-spot-wrapper hot-spot hot-spot-map-transition border border-white border-2 rounded-circle" data-map-id="${map.id}">
      <i class="p-1 fa fa-chevron-circle-down"></i>
    </div>
  `
  hotSpotDiv.addEventListener('mouseover', () => hoverFeatureTooltipLabel.value = map.label)
  hotSpotDiv.addEventListener('mouseout', () => hoverFeatureTooltipLabel.value = null)
}
const hotSpotLabelTooltip = (hotSpotDiv, { properties }) => {
  hotSpotDiv.innerHTML = `
    <div class="hot-spot-wrapper hot-spot hot-spot-label">
      ${properties.label}
    </div>
  `
}

watch(featureIdHover, (newValue, oldValue) => {
  if (newValue != oldValue) {
    document.querySelectorAll('.hot-spot').forEach( (domEl) => {
      domEl.dataset.featureId && domEl.dataset.featureId === `${newValue}` ? domEl.classList.add('highlight') : domEl.classList.remove('highlight')
    })
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
const animationFrameLoop = () => {
  animationFrameId.value = window.requestAnimationFrame(animationFrameLoop)
  if (viewer.value) {
    const hfovUpdate = viewer.value.getHfov()
    if (hfovUpdate != hfov.value) { hfov.value = hfovUpdate}
    const yawUpdate = viewer.value.getYaw()
    if (yawUpdate != yaw.value) { yaw.value = yawUpdate}
    const pitchUpdate = viewer.value.getPitch()
    if (pitchUpdate != pitch.value) { pitch.value = pitchUpdate}
  }
}
const panUp = () => pitch.value += 10
const panDown = () => pitch.value -= 10
const panLeft = () => yaw.value -= 10
const panRight = () => yaw.value += 10
const zoomIn = () => hfov.value -= 10
const zoomOut = () => hfov.value += 10
defineExpose({ panUp, panDown, panLeft, panRight, zoomIn, zoomOut })

const loadPannellum = () => {
  if (viewer.value) { viewer.value.destroy() }
  const options = {
    hfov: hfov.value,
    yaw: yaw.value,
    pitch: pitch.value,
    preview: null,
    autoLoad: true,
    draggable: true,
    mouseZoom: true,
    doubleClickZoom: true,
    showControls: false,
    compass: false,
    crossOrigin: 'anonymous',
    type: 'multires',
    multiRes: {
      basePath: `${websiteOrigin}${map.tiles_dir}`,
      path: '/%l/%s_%y_%x',
      fallbackPath: '/fallback/%s',
      extension: map.tile_format,
      tileResolution: map.tile_size,
      maxLevel: map.max_zoom,
      cubeResolution: map.cube_size,
    },
    hotSpots,
  }
  viewer.value = window.pannellum.viewer(pannellumRef.value, options)
}
onMounted(() => {
  loadPannellum()
  animationFrameId.value = window.requestAnimationFrame(animationFrameLoop)
})
onUnmounted(() => {
  if (viewer.value) {
    viewer.value.destroy()
    viewer.value = undefined
  }
  if (animationFrameId.value) { window.cancelAnimationFrame(animationFrameId.value) }
})
</script>

<template>
  <UseMouseInElement v-slot="{ elementX, elementY }">
    <div class="z-0 position-absolute top-0 bottom-0 start-0 end-0">
      <span
        v-if="hoverFeatureTooltipLabel"
        class="z-2 position-absolute badge text-bg-primary"
        :style="{ left: `${elementX+10}px`, top: `${elementY+5}px` }"
        v-html="hoverFeatureTooltipLabel"
      />
      <div
        ref="pannellumRef"
        class="z-1 vue-pannellum"
        @mouseup="onMouseUp"
        @touchmove="onTouchMove"
        @touchend="onTouchEnd"
      ></div>
    </div>
  </UseMouseInElement>
</template>

<style lang="scss" scoped>
/* pannellum */
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
      font-size: 1em;
      font-weight: bold;
      position: relative;


      &.hot-spot-icon-numbered {
        margin-top: -2em;
        i {
          font-size: 2em;
          z-index: 1000;
          color: #6495ED;
          -webkit-text-stroke-width: 2px;
          -webkit-text-stroke-color: white;
        }
        .number-label {
          color: white;
          font-size: 0.8em;
          z-index: 1001;
          position: absolute;
          left: 0;
          right: 0;
          bottom: calc(50% - 0.5em);
          text-align: center;
        }
        &.highlight i  {
          -webkit-text-stroke-color: rgba(13, 110, 353, 1) !important;
        }
      }
      &.hot-spot-icon-default {
        i {
          font-size: 0.8em;
          color: #6495ED;
          -webkit-text-stroke-width: 2px;
          -webkit-text-stroke-color: white;
        }
        &.highlight i  {
          -webkit-text-stroke-color: rgba(13, 110, 353, 1) !important;
        }
      }
      &.hot-spot-icon-image {
        border-color: white;
        img {
          width: 40px;
          height: 40px;
        }
        &.highlight  {
          border-color: rgba(13, 110, 353, 1) !important;
        }
      }
      &.hot-spot-map-transition {
        border-color: white;
        i {
          padding: 2px;
          font-size: 1.6em;
          color: white;
          width: auto;
          /* height: fit-content; */
          /* aspect-ratio: 1; */
        }
      }
      &.hot-spot-label {
        font-size: 1em;
        font-family: sans-serif;
        font-weight: bold;
        color: white;
        text-shadow:  -1px -1px 0 #000,  1px -1px 0 #000, -1px  1px 0 #000, 1px  1px 0 #000;
      }
    }
  }
}
</style>
