<script setup>
import { reactive, ref, onMounted, onUnmounted, computed, watch, nextTick, toRaw } from 'vue'
import { UseFullscreen, UseMouseInElement } from '@vueuse/components'
import { Tooltip } from 'bootstrap'
import { _getPaginatedApiResources, _getApiResource } from '../_utils.js'
import { EditModeActionTypes, EditModeAddActionTypes } from './_editActions.js'
import { MapGeojsonResourceTypes, IconResourceTypes } from '../_resourceTypes.js'

const emit = defineEmits(['updatedHotSpotsGeoJson', 'updatedMapProperties'])
const props = defineProps({
  mapId: { type: Number, required: true },
  editMode: { type: Boolean, default: false },
})

const websiteOrigin = window.location.origin
const features = await _getPaginatedApiResources(`${websiteOrigin}/api/admin/features`)
const featuresMap = features.reduce((result, o) => result.set(o.id, o), new Map())
const maps = await _getPaginatedApiResources(`${websiteOrigin}/api/admin/maps`)
const mapsObjectMap = maps.reduce((result, o) => result.set(o.id, o), new Map())
const map = mapsObjectMap.get(props.mapId)

const initial = ref(map.properties?.initial || null)
const viewer = ref(null)
const hfov = ref(100)
const yaw = ref(0)
const pitch = ref(0)
if (map.properties.initial) {
  hfov.value = map.properties.initial.hfov
  yaw.value = map.properties.initial.yaw
  pitch.value = map.properties.initial.pitch
}

const pannellumWrapperRef = ref(null)
const pannellumRef = ref(null)
const animationFrameId = ref(null)
const hoverFeatureTooltipLabel = ref(null)

const hotSpotsGeoJson = reactive(await _getApiResource(`${websiteOrigin}/api/admin/maps/${map.id}/geojson`))
const hotSpots = ref([])
const hotSpotFeatureTooltip = (hotSpotDiv, { id, properties }) => {
  const feature = featuresMap.get(properties.feature)
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
  hotSpotDiv.addEventListener('mouseover', () => hoverFeatureTooltipLabel.value = feature.title)
  hotSpotDiv.addEventListener('mouseout', () => hoverFeatureTooltipLabel.value = null)
}
const hotSpotMapTransitionTooltip = (hotSpotDiv, { id, properties }) => {
  const map = mapsObjectMap.get(properties.map)
  hotSpotDiv.innerHTML = `
    <div class="hot-spot-wrapper hot-spot hot-spot-map-transition border border-white border-2 rounded-circle" data-map-id="${map.id}">
      <i class="p-1 fa fa-chevron-circle-down"></i>
    </div>
  `
  hotSpotDiv.addEventListener('mouseover', () => hoverFeatureTooltipLabel.value = map.label)
  hotSpotDiv.addEventListener('mouseout', () => hoverFeatureTooltipLabel.value = null)
}
const hotSpotLabelTooltip = (hotSpotDiv, { id, properties }) => {
  hotSpotDiv.innerHTML = `
    <div class="hot-spot-wrapper hot-spot hot-spot-label">
      ${properties.label}
    </div>
  `
  hotSpotDiv.addEventListener('mouseover', () => hoverFeatureTooltipLabel.value = properties.label)
  hotSpotDiv.addEventListener('mouseout', () => hoverFeatureTooltipLabel.value = null)
}
const hotSpotTooltip = (hotSpotDiv, { id, properties }) => {
  if (properties.resourcetype === MapGeojsonResourceTypes.feature) {
    return hotSpotFeatureTooltip(hotSpotDiv, { id, properties })
  } else if (properties.resourcetype === MapGeojsonResourceTypes.transition) {
    return hotSpotMapTransitionTooltip(hotSpotDiv, { id, properties })
  } else if (properties.resourcetype === MapGeojsonResourceTypes.label) {
    return hotSpotLabelTooltip(hotSpotDiv, { id, properties })
  } else {
    // default
    hotSpotDiv.innerHTML = ''
  }
}
const resetHotSpots = () => {
  if (viewer.value) {
    hotSpots.value.forEach((hotSpot) => viewer.value.removeHotSpot(hotSpot.id))
  }
  let hotSpotId = 0
  hotSpots.value = hotSpotsGeoJson.features.reduce((results, feature, hotSpotGeoJsonIndex) => {
    let coordinates = []
    if (feature.geometry && feature.geometry.type === 'MultiPoint') {
      coordinates = feature.geometry.coordinates
    } else if (feature.geometry && feature.geometry.type === 'Point') {
      coordinates.push(feature.geometry.coordinates)
    }
    // concat results with new coordinates
    return [...results, ...coordinates.map((coords, coordinatesIndex) => {
      const hotSpot = {
        id: `hot_spot_id_${hotSpotId++}`,
        pitch: coords[0],
        yaw: coords[1],
        createTooltipFunc: hotSpotTooltip,
        createTooltipArgs: {id: feature.id, properties: feature.properties},
        draggable: false,
        cssClass: props.editMode ? 'edit-hot-spot' : 'view-hot-spot',
      }
      if (isMoveAction.value) {
        hotSpot.draggable = true
        hotSpot.dragHandlerFunc = moveHotSpotDrag
        hotSpot.dragHandlerArgs = {hotSpotGeoJsonIndex, coordinatesIndex}
      } else if (isRemoveAction.value) {
        hotSpot.clickHandlerFunc = removedHotSpotClick
        hotSpot.clickHandlerArgs = {hotSpotGeoJsonIndex, coordinatesIndex}
      }
      return hotSpot
    })]
  }, [])
  if (viewer.value) {
    hotSpots.value.forEach((hotSpot) => viewer.value.addHotSpot(hotSpot))
  }
}

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
const resetPannellumEvents = () => {
  if (viewer.value) {
    viewer.value.off('mouseup')
    if (isAddFeatureAction.value) {
      viewer.value.on('mouseup', addNewFeatureClick)
    } else if (isAddMapAction.value) {
      viewer.value.on('mouseup', addNewMapClick)
    } else if (isAddLabelAction.value) {
      viewer.value.on('mouseup', addNewLabelClick)
    }
  }
}
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
    hotSpots: hotSpots.value,
  }
  viewer.value = window.pannellum.viewer(pannellumRef.value, options)
  nextTick(() => {
    emitUpdatedHotSpotsGeoJson()
    resetPannellumEvents()
    resetHotSpots()
  })
}
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

// edit actions
const mouseCoords = ref(null)
const editModeAction = ref(null)
watch(editModeAction, (newValue, oldValue) => {
  if (newValue !== oldValue) {
    resetPannellumEvents()
    resetHotSpots()
  }
})
const editModeAddAction = ref(null)
watch(editModeAddAction, (newValue, oldValue) => {
  if (newValue !== oldValue) {
    resetPannellumEvents()
    resetHotSpots()
  }
})
const selectedAddFeature = ref(null)
const listedMaps = maps.filter((map) => map.id != props.mapId)
const selectedAddMap = ref(null)
const toggleEditModeAction = (value) => editModeAction.value = editModeAction.value === value ? null : value
const toggleEditModeAddAction = (value) => editModeAddAction.value = editModeAddAction.value === value ? null : value
const isMoveAction = computed(() => props.editMode && editModeAction.value === EditModeActionTypes.move)
const isAddAction = computed(() => props.editMode && editModeAction.value === EditModeActionTypes.add)
const isAddFeatureAction = computed(() => isAddAction.value && editModeAddAction.value === EditModeAddActionTypes.feature)
const isAddMapAction = computed(() => isAddAction.value && editModeAddAction.value === EditModeAddActionTypes.map)
const isAddLabelAction = computed(() => isAddAction.value && editModeAddAction.value === EditModeAddActionTypes.label)
const isInitialViewAction = computed(() => props.editMode && editModeAction.value === EditModeActionTypes.initialView)
const isRemoveAction = computed(() => props.editMode && editModeAction.value === EditModeActionTypes.remove)
const emitUpdatedHotSpotsGeoJson = () => {
  emit('updatedHotSpotsGeoJson', structuredClone(toRaw(hotSpotsGeoJson)))
}
const emitUpdatedMapProperties = () => {
  emit('updatedMapProperties', structuredClone(map.properties))
}
const moveHotSpotDrag = (event, {hotSpotGeoJsonIndex, coordinatesIndex}) => {
  if (["mouseup", "touchend", "pointerup"].includes(event.type)) {
    const [pitch, yaw] = viewer.value.mouseEventToCoords(event)
    const featureGeoJson = hotSpotsGeoJson.features[hotSpotGeoJsonIndex]
    if (featureGeoJson.geometry && featureGeoJson.geometry.type === 'MultiPoint') {
      featureGeoJson.geometry.coordinates[coordinatesIndex] = [pitch, yaw]
    } else if (featureGeoJson.geometry && featureGeoJson.geometry.type === 'Point') {
      featureGeoJson.geometry.coordinates = [pitch, yaw]
    }
    emitUpdatedHotSpotsGeoJson()
    resetHotSpots()
  }
}
const addNewFeatureClick = (event) => {
  if (selectedAddFeature.value && selectedAddFeature.value.id) {
    const coords = viewer.value.mouseEventToCoords(event)
    const featureId = selectedAddFeature.value.id
    const existingGeoJsonFeature = hotSpotsGeoJson.features
      .find((feature) => feature.properties.resourcetype === MapGeojsonResourceTypes.feature && feature.properties.feature === featureId)

    if (existingGeoJsonFeature) {
      existingGeoJsonFeature.geometry.coordinates.push(coords)
    } else {
      hotSpotsGeoJson.features.push({
        type: 'Feature',
        geometry: {
          type: 'MultiPoint',
          coordinates: [coords],
        },
        properties: {
          feature: featureId,
          data: {},
          resourcetype: MapGeojsonResourceTypes.feature,
        },
      })
    }
    emitUpdatedHotSpotsGeoJson()
    resetHotSpots()
  }
}
const addNewMapClick = (event) => {
  if (selectedAddMap.value && selectedAddMap.value.id) {
    const coords = viewer.value.mouseEventToCoords(event)
    const mapId = selectedAddMap.value.id
    const existingGeoJsonFeature = hotSpotsGeoJson.features
      .find((feature) => feature.properties.resourcetype === MapGeojsonResourceTypes.transition && feature.properties.map === mapId)

    if (existingGeoJsonFeature) {
      existingGeoJsonFeature.geometry.coordinates.push(coords)
    } else {
      hotSpotsGeoJson.features.push({
        type: 'Feature',
        geometry: {
          type: 'MultiPoint',
          coordinates: [coords],
        },
        properties: {
          map: mapId,
          data: {},
          resourcetype: MapGeojsonResourceTypes.transition,
        },
      })
    }
    emitUpdatedHotSpotsGeoJson()
    resetHotSpots()
  }
}
const addNewLabelClick = (event) => {
  const coords = viewer.value.mouseEventToCoords(event)
  const label = prompt("Enter the new map label...")

  if (label !== null && label.trim() !== '') {
    hotSpotsGeoJson.features.push({
      type: 'Feature',
      geometry: {
        type: 'Point',
        coordinates: coords,
      },
      properties: {
        label,
        data: {},
        resourcetype: MapGeojsonResourceTypes.label,
      },
    })
    emitUpdatedHotSpotsGeoJson()
    resetHotSpots()
  }
}
const removedHotSpotClick = (event, {hotSpotGeoJsonIndex, coordinatesIndex}) => {
  if (confirm('Are you sure you want to remove this item?')) {
    const featureGeoJson = hotSpotsGeoJson.features[hotSpotGeoJsonIndex]
    if (featureGeoJson.geometry && featureGeoJson.geometry.type === 'MultiPoint') {
      featureGeoJson.geometry.coordinates.splice(coordinatesIndex, 1)
    } else if (featureGeoJson.geometry && featureGeoJson.geometry.type === 'Point') {
      hotSpotsGeoJson.features.splice(hotSpotGeoJsonIndex, 1)
    }
    hoverFeatureTooltipLabel.value = null
    emitUpdatedHotSpotsGeoJson()
    resetHotSpots()
  }
}
const setInitialViewToDefault = () => {
  if (confirm('Are you sure you want reset the initial view to default values?')) {
    if (map.properties.initial) {
      delete map.properties.initial
    }
    initial.value = undefined
    emitUpdatedMapProperties()
    resetViewToInitial()
  }
}
const setInitialView = () => {
  if (confirm('Are you sure you want this view as the initial view?')) {
    map.properties.initial = {
      hfov: toRaw(hfov.value),
      yaw: toRaw(yaw.value),
      pitch: toRaw(pitch.value),
    }
    initial.value = structuredClone(map.properties.initial)
    emitUpdatedMapProperties()
    resetViewToInitial()
  }
}
const resetViewToInitial = () => {
  if (initial.value) {
    hfov.value = initial.value.hfov
    yaw.value = initial.value.yaw
    pitch.value = initial.value.pitch
  } else {
    hfov.value = 100
    yaw.value = 0
    pitch.value = 0
  }
}
// end edit actions
onMounted(() => {
  pannellumWrapperRef.value.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(
    (tooltipTriggerEl) => Tooltip.getOrCreateInstance(tooltipTriggerEl, {container: pannellumWrapperRef.value}).hide()
  )
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
  <UseFullscreen v-slot="{ isFullscreen, toggle: toggleFullscreen }">
    <UseMouseInElement v-slot="{ elementX, elementY }">
      <div ref="pannellumWrapperRef" class="z-0 position-absolute top-0 bottom-0 start-0 end-0">
        <div class="z-3 position-absolute bottom-0 start-50 translate-middle-x btn-group">
          <button @click="panUp"
            type="button" class="btn btn-link text-light link-underline-opacity-0"
            data-bs-toggle="tooltip" data-bs-trigger="hover" data-bs-title="Pan Up"
          >
            <i class="bi bi-arrow-up"></i>
          </button>
          <button @click="panDown"
            type="button" class="btn btn-link text-light link-underline-opacity-0"
            data-bs-toggle="tooltip" data-bs-trigger="hover" data-bs-title="Pan Down"
          >
            <i class="bi bi-arrow-down"></i>
          </button>
          <button @click="panLeft"
            type="button" class="btn btn-link text-light link-underline-opacity-0"
            data-bs-toggle="tooltip" data-bs-trigger="hover" data-bs-title="Pan Left"
          >
            <i class="bi bi-arrow-left"></i>
          </button>
          <button @click="panRight"
            type="button" class="btn btn-link text-light link-underline-opacity-0"
            data-bs-toggle="tooltip" data-bs-trigger="hover" data-bs-title="Pan Right"
          >
            <i class="bi bi-arrow-right"></i>
          </button>
          <button @click="zoomIn"
            type="button" class="btn btn-link text-light link-underline-opacity-0"
            data-bs-toggle="tooltip" data-bs-trigger="hover" data-bs-title="Zoom In"
          >
            <i class="bi bi-plus-lg"></i>
          </button>
          <button @click="zoomOut"
            type="button" class="btn btn-link text-light link-underline-opacity-0"
            data-bs-toggle="tooltip" data-bs-trigger="hover" data-bs-title="Zoom Out"
          >
            <i class="bi bi-dash-lg"></i>
          </button>
        </div>
        <div class="z-3 position-absolute top-0 end-0 btn-group-vertical">
          <button @click="toggleFullscreen"
            type="button" class="btn btn-link text-light link-underline-opacity-0"
            data-bs-toggle="tooltip" data-bs-trigger="hover" data-bs-title="Toggle Fullscreen Mode"
          >
            <i v-if="!isFullscreen" class="bi bi-fullscreen"></i>
            <i v-if="isFullscreen" class="bi bi-fullscreen-exit"></i>
          </button>
        </div>
                <div class="z-3 position-absolute top-0 start-0" v-if="editMode">
          <div class="btn-group edit-actions" role="group">
            <button type="button" class="btn btn-dark"
              data-bs-toggle="tooltip" data-bs-trigger="hover" data-bs-title="Move Feature"
              :class="{ active: isMoveAction }"
              @click="() => toggleEditModeAction(EditModeActionTypes.move)"
            >
              <i class="bi bi-arrows-move"></i>
            </button>
            <button type="button" class="btn btn-dark"
              data-bs-toggle="tooltip" data-bs-trigger="hover" data-bs-title="Add Feature"
              :class="{ active: isAddAction }"
              @click="() => toggleEditModeAction(EditModeActionTypes.add)"
            >
              <i class="bi bi-plus-lg"></i>
            </button>
            <button type="button" class="btn btn-dark"
              data-bs-toggle="tooltip" data-bs-trigger="hover" data-bs-title="Modify Initial View"
              :class="{ active: isInitialViewAction }"
              @click="() => toggleEditModeAction(EditModeActionTypes.initialView)"
            >
              <i class="fa-solid fa-panorama"></i>
            </button>
            <button type="button" class="btn btn-danger"
              data-bs-toggle="tooltip" data-bs-trigger="hover" data-bs-title="Remove Feature"
              :class="{ active: isRemoveAction }"
              @click="() => toggleEditModeAction(EditModeActionTypes.remove)"
            >
              <i class="bi bi-trash"></i>
            </button>
          </div>
          <br />
          <div class="btn-group edit-actions" role="group" v-if="isAddAction">
            <button type="button" class="btn btn-dark"
              data-bs-toggle="tooltip" data-bs-trigger="hover" data-bs-title="Add Feature"
              :class="{ active: isAddFeatureAction }"
              @click="() => toggleEditModeAddAction(EditModeAddActionTypes.feature)"
            >
              <i class="bi bi-pin-map"></i>
            </button>
            <button type="button" class="btn btn-dark"
              data-bs-toggle="tooltip" data-bs-trigger="hover" data-bs-title="Add Map Transition"
              :class="{ active: isAddMapAction }"
              @click="() => toggleEditModeAddAction(EditModeAddActionTypes.map)"
            >
              <i class="fa-solid fa-map-location-dot"></i>
            </button>
            <button type="button" class="btn btn-dark"
              data-bs-toggle="tooltip" data-bs-trigger="hover" data-bs-title="Add Label"
              :class="{ active: isAddLabelAction }"
              @click="() => toggleEditModeAddAction(EditModeAddActionTypes.label)"
            >
              <i class="fa-solid fa-heading"></i>
            </button>
          </div>
          <div class="btn-group edit-actions" role="group" v-if="isInitialViewAction">
            <button type="button" class="btn btn-dark"
              data-bs-toggle="tooltip" data-bs-trigger="hover" data-bs-title="Set Initial View to Current Viewport"
              @click="() => setInitialView()"
            >
              <i class="bi bi-textarea"></i>
            </button>
            <button type="button" class="btn btn-dark"
              data-bs-toggle="tooltip" data-bs-trigger="hover" data-bs-title="Reset Viewport to Initial View"
              @click="() => resetViewToInitial()"
            >
              <i class="fa-solid fa-arrow-rotate-left"></i>
            </button>
            <button type="button" class="btn btn-danger"
              data-bs-toggle="tooltip" data-bs-trigger="hover" data-bs-title="Set Initial View to Default Values"
              @click="() => setInitialViewToDefault()"
            >
              <i class="fa-solid fa-arrows-rotate"></i>
            </button>
          </div>
          <v-select
            v-if="isAddFeatureAction"
            :options="features" label="title" v-model="selectedAddFeature"
            placeholder="Add feature for..." class="select-feature"
            :appendToBody="!isFullscreen"
          ></v-select>
          <v-select
            v-if="isAddMapAction"
            :options="listedMaps" label="label" v-model="selectedAddMap"
            placeholder="Add map transition to..." class="select-map"
            :appendToBody="!isFullscreen"
          ></v-select>
        </div>
        <span
          v-if="hoverFeatureTooltipLabel"
          class="z-2 position-absolute badge text-bg-primary"
          :style="{ left: `${elementX+10}px`, top: `${elementY+5}px` }"
          v-html="hoverFeatureTooltipLabel"
        />
        <div class="z-3 position-absolute bottom-0 start-0" v-if="editMode && !!mouseCoords">
          <div class="ms-1 mb-1">
            <div class="badge text-bg-light mb-1" v-html="`Yaw: ${mouseCoords[1].toFixed(10)}`" /><br />
            <div class="badge text-bg-light mb-1" v-html="`Pitch: ${mouseCoords[0].toFixed(10)}`" /><br />
            <div class="badge text-bg-light" v-html="`HFOV: ${hfov.toFixed(10)}`" />
          </div>
        </div>
        <div class="z-3 position-absolute bottom-0 end-0 d-flex flex-column">
          <span class="badge text-bg-light ms-auto me-1 mb-1" v-if="!!map.attributions" v-html="map.attributions" />
          <span class="badge text-bg-light ms-auto me-1 mb-1" v-if="!!map.date_taken" v-html="`Taken on ${new Date(map.date_taken).toLocaleDateString()}`" />
        </div>
        <div
          ref="pannellumRef"
          class="z-1 vue-pannellum"
          @mousemove="(event) => mouseCoords = viewer.mouseEventToCoords(event)"
          @mouseup="onMouseUp"
          @touchmove="onTouchMove"
          @touchend="onTouchEnd"
        ></div>
      </div>
    </UseMouseInElement>
  </UseFullscreen>
</template>

<style lang="scss" scoped>
button.btn.btn-link {
  font-size: 1.5em;
  text-shadow: -1px -1px 0 black, 1px -1px 0 black, -1px 1px 0 black, 1px 1px 0 black;
}
.select-map,
.select-feature {
  font-size: 1.5em;
  padding: .375rem .75rem;
  width: 300px;
}
.edit-actions {
  margin: .375rem .75rem;

  .btn-check + .btn {
    width: fit-content;
  }
  .btn-check:checked + .btn {
    color: var(--bs-btn-active-color);
    background-color: var(--bs-btn-active-bg);
    border-color: var(--bs-btn-active-border-color);
  }
}
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
      }
      &.hot-spot-icon-default {
        i {
          font-size: 0.8em;
          color: #6495ED;
          -webkit-text-stroke-width: 2px;
          -webkit-text-stroke-color: white;
        }
      }
      &.hot-spot-icon-image {
        border-color: white;
        img {
          width: 40px;
          height: 40px;
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
    .edit-hot-spot .hot-spot-wrapper {
      &:hover::after {
        content: "\F287";
        font-family: bootstrap-icons !important;
        font-size: 0.6em;
        position: absolute;
        text-align: center;
        color: rgb(0, 153, 255);
        -webkit-text-stroke-width: 1px;
        -webkit-text-stroke-color: black;
      }
      &.hot-spot-icon-numbered:hover::after {
        bottom: -0.3em;
        left: 0;
        right: 0;
      }
      &:not(.hot-spot-icon-numbered):hover::after {
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
      }
    }
  }
}
</style>
