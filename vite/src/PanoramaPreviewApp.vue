

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import Pannellum from './components/Pannellum.vue'

const props = defineProps({
  tilesDir: {
    type: String,
    required: true,
  },
  tileFormat: {
    type: String,
    required: true,
  },
  tileSize: {
    type: String,
    required: true,
  },
  cubeSize: {
    type: String,
    required: true,
  },
  maxZoom: {
    type: String,
    required: true,
  },
})

const viewer = ref(null)
const hfov = ref(100)
const yaw = ref(180)
const pitch = ref(0)
const points = ref([])

// const generateHotSpot = (point) => {
//   const hotSpot = {
//     pitch: point.pitch,
//     yaw: point.yaw,
//     type: 'info',
//     createTooltipFunc: hotSpotTooltip,
//     createTooltipArgs: { featureId: point.featureId, pointId: point.id },
//     draggable: false,
//     cssClass: 'view-hotspot',
//   }
//   if (!isEditMode.value) {
//     hotSpot.clickHandlerArgs = { featureId: point.featureId, pointId: point.id }
//     hotSpot.clickHandlerFunc = (event, { featureId, pointId }) => displayStore.showFeature(featureId, pointId)
//   }
//   return hotSpot
// }
// const hotSpotEditTooltip = (hotSpotDiv) => {
//   hotSpotDiv.innerHTML = `
//     <div class="hot-spot-wrapper hot-spot-edit">
//       <i class="fa-solid fa-location-pin"></i>
//     </div>
//   `
// }
// const hotSpotTooltip = (hotSpotDiv, {featureId, pointId}) => {
//   const feature = useDataStore().getFeature(featureId)
//   const fillColor = feature.feature_type == 'GARDEN_FEATURE' ? '#6495ED' : '#7cb341'
//   hotSpotDiv.innerHTML = `
//     <div class="hot-spot-wrapper hot-spot" data-feature-id="${feature.id}">
//       <i class="fa-solid fa-location-pin" style="color: ${fillColor}"></i>
//       <span class="number-label">${feature.number}</span>
//     </div>
//   `
//   hotSpotDiv.addEventListener('mouseover', () => hoverFeatureId.value = feature.id)
//   hotSpotDiv.addEventListener('mouseout', () => hoverFeatureId.value = null)
// }

const websiteOrigin = window.location.origin
const pannellumSrc = computed(() => ({
  default: { firstScene: 'default' },
  scenes: {
    'default': {
      type: 'multires',
      multiRes: {
        basePath: `${websiteOrigin}${props.tilesDir}`,
        path: '/%l/%s_%y_%x',
        fallbackPath: '/fallback/%s',
        extension: props.tileFormat,
        tileResolution: Number(props.tileSize),
        maxLevel: Number(props.maxZoom),
        cubeResolution: Number(props.cubeSize),
      },
      yaw: 180,
      pitch: 0,
      // hotSpots: points.value.map((point) => generateHotSpot(point)),
    },
  }
}))
</script>

<template>
  <div class="pannellum-preview-wrapper">
    <Pannellum
      v-model:viewer="viewer" v-model:src="pannellumSrc"
      v-model:hfov="hfov" v-model:yaw="yaw" v-model:pitch="pitch"
      preview="" :autoLoad="true"
      :draggable="true" :showControls="false" :compass="false"
    ></Pannellum>
  </div>
</template>

<style lang="scss" scoped>
.pannellum-preview-wrapper {
  position: relative;
  height: 400px;
  min-width: 400px;
  width: 100%;
}
</style>