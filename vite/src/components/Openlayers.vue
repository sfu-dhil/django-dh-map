<script setup>
import { ref, inject, onMounted, nextTick, computed, watch, toRaw } from 'vue'
import { UseFullscreen } from '@vueuse/components'
import { Tooltip } from 'bootstrap'
import { Style, Text, Fill, Stroke, Circle, Icon } from 'ol/style'
import { getCenter, getSize, boundingExtent } from 'ol/extent'
import { toLonLat } from 'ol/proj'
import { fromExtent } from 'ol/geom/Polygon'
import { TileGrid } from 'ol/tilegrid'
import { easeOut } from 'ol/easing'
import { Point } from 'ol/geom'
import { GeoJSON } from 'ol/format'
import { _getPaginatedApiResources } from '../_utils.js'
import { EditModeActionTypes, EditModeAddActionTypes, EditModeBoundingBoxActionTypes } from './_editActions.js'
import { MapGeojsonResourceTypes, IconResourceTypes, MapResourceTypes } from '../_resourceTypes.js'

const emit = defineEmits(['updatedGeoJsonObject', 'updatedMapProperties'])
const props = defineProps({
  mapId: { type: Number, required: true },
  editMode: { type: Boolean, default: false },
})
const websiteOrigin = window.location.origin
const iconCanvasMap = new Map()
const features = await _getPaginatedApiResources(`${websiteOrigin}/api/admin/features`)
const featuresObjectMap = features.reduce((result, o) => result.set(o.id, o), new Map())
const maps = await _getPaginatedApiResources(`${websiteOrigin}/api/admin/maps`)
const mapsObjectMap = maps.reduce((result, o) => result.set(o.id, o), new Map())
const map = mapsObjectMap.get(props.mapId)

// base extent is generally unbound but still limited to image dimensions for overhead image maps
const baseUnboundExtent = computed(() => {
  if (map.resourcetype === MapResourceTypes.overheadImageMap) { return [0, -map.height, map.width, 0] }
  return undefined
})
const initial = ref(map.properties?.initial || null)
const boundingBox = ref(map.properties?.bounding_box || null)
const extent = computed(() => {
  if(boundingBox.value) {
    return boundingExtent(boundingBox.value.flat())
  }
  return baseUnboundExtent.value
})
const zoom = ref(1)
const rotation = ref(0)
const center = ref([0,0])
const geoJson = computed(() => new GeoJSON({
  dataProjection: `EPSG:${map.data_srid}`,
  featureProjection: `EPSG:${map.feature_srid}`,
}))
const projection = computed(() => {
  if ([MapResourceTypes.xyzMap].includes(map.resourcetype)) {
    return `EPSG:${map.feature_srid}`
  } else if (map.resourcetype === MapResourceTypes.overheadImageMap) {
    return {
      code: `EPSG:${map.feature_srid}`,
      units: 'pixels',
      extent: baseUnboundExtent.value,
    }
  }
})
const overheadMapTileGrid = computed(() => {
  if (map.resourcetype === MapResourceTypes.overheadImageMap) {
    const resolutions = []
    for (let index = map.max_zoom; index >= map.min_zoom; --index) {
      resolutions.push(2 ** (index))
    }
    return new TileGrid({
      extent: baseUnboundExtent.value,
      origin: [0, 0],
      resolutions: resolutions,
      tileSize: [map.tile_size, map.tile_size],
    })
  }
})

const mapRef = ref(null)
const sourceVectorRef = ref(null)
const hoverFeatureTooltipParams = ref(null)

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
const zoomIn = () => mapRef.value.map.getView().animate({ zoom: mapRef.value.map.getView().getZoom() + 1, easing: easeOut })
const zoomOut = () => mapRef.value.map.getView().animate({ zoom: mapRef.value.map.getView().getZoom() - 1, easing: easeOut })
const resetRotation = () => mapRef.value.map.getView().animate({ rotation: (initial.value?.rotation || 0), easing: easeOut })
const updateCenter = (event) => center.value = event.target.getCenter()
const updateZoom = (event) => zoom.value = event.target.getZoom()
const updateRotation = (event) => rotation.value = event.target.getRotation()
const featureStyle = (openLayersFeature) => {
  const feature = featuresObjectMap.get(openLayersFeature.get('feature'))
  const icon = feature?.icon
  if (icon && icon.resourcetype === IconResourceTypes.image) {
    if (!iconCanvasMap.has(icon.id)) {
      const size = icon.size
      const canvas = document.createElement('canvas')
      const ctx = canvas.getContext('2d')
      canvas.width = size
      canvas.height = size
      iconCanvasMap.set(icon.id, canvas)

      const img = new Image()
      img.src = icon.icon_thumbnail
      img.onload = () => {
        ctx.beginPath()
        ctx.roundRect(0, 0, size, size, size/ 2)
        ctx.clip()
        ctx.drawImage(img, 0, 0, size, size)
        sourceVectorRef.value?.source.changed()
      }
    }
    return [
      new Style({
        image: new Circle({
          radius: icon.size/2+4,
          fill: new Fill({ color: 'rgba(0, 0, 0, 0.0)' }),
          stroke: new Stroke({ color: 'white', width: 3 })
        }),
        zIndex: 0
      }),
      new Style({
        image: new Icon({
          img: iconCanvasMap.get(icon.id),
          imgSize: [icon.size, icon.size]
        }),
        zIndex: 1
      }),
    ]
  } else if (icon && icon.resourcetype === IconResourceTypes.numbered) {
    return [
      new Style({
        text: new Text({
          text: '\uf041',
          scale: 2,
          textBaseline: 'bottom',
          font: 'bold 1em "Font Awesome 7 Free"',
          fill: new Fill({ color: '#6495ED' }),
          stroke: new Stroke({ color: 'white', width: 3 }),
        }),
      }),
      new Style({
        text: new Text({
          text: `${icon.number}`,
          scale: 1,
          textBaseline: 'bottom',
          font: 'bold 1em "BC Sans"',
          // offsetX: `${number}`.length - 1,
          offsetY: -9,
          fill: new Fill({ color: 'white' }),
        }),
      }),
    ]
  } else {
    // default icon
    return new Style({
      image: new Circle({
        radius: 6,
        fill: new Fill({ color: '#6495ED' }),
        stroke: new Stroke({ color: 'white', width: 1.25 }),
      }),
    })
  }
}
const mapTransitionStyle = (openLayersFeature) => {
  const map = mapsObjectMap.get(openLayersFeature.get('map'))
  return [
    new Style({
      image: new Circle({
        radius: 17,
        fill: new Fill({ color: 'rgba(0, 0, 0, 0.0)' }),
        stroke: new Stroke({ color: 'white', width: 2 })
      }),
      zIndex: 0
    }),
    new Style({
      text: new Text({
        text: '\uf13a',
        scale: 2,
        textBaseline: 'middle',
        font: 'bold 1em "Font Awesome 7 Free"',
        fill: new Fill({ color: 'white' }),
        stroke: new Stroke({ color: 'rgba(0, 0, 0, 0.0)', width: 3 }),
      }),
      zIndex: 1
    }),
  ]
}
const labelStyle = (openLayersFeature) => {
  return [
    new Style({
      text: new Text({
        text: openLayersFeature.get('label'),
        textBaseline: 'middle',
        textAlign: 'center',
        font: 'bold 1.5em sans-serif',
        fill: new Fill({ color: 'white' }),
        stroke: new Stroke({ color: 'black', width: 2 }),
      }),
    }),
  ]
}
const overrideOpenLayersFeatureStyle = (openLayersFeature) => {
  if (openLayersFeature.get('resourcetype') === MapGeojsonResourceTypes.feature) {
    return featureStyle(openLayersFeature)
  } else if (openLayersFeature.get('resourcetype') === MapGeojsonResourceTypes.transition) {
    return mapTransitionStyle(openLayersFeature)
  } else if (openLayersFeature.get('resourcetype') === MapGeojsonResourceTypes.label) {
    return labelStyle(openLayersFeature)
  } else {
    // default icon
    return null
  }
}

// edit actions
const mouseCoords = ref(null)
const editModeAction = ref(null)
const editModeAddAction = ref(null)
const selectedAddFeature = ref(null)
const listedMaps = maps.filter((map) => map.id != props.mapId)
const selectedAddMap = ref(null)
const editModeBoundingBoxAction = ref(null)
const toggleEditModeAction = (value) => editModeAction.value = editModeAction.value === value ? null : value
const toggleEditModeAddAction = (value) => editModeAddAction.value = editModeAddAction.value === value ? null : value
const toggleEditBoundingBoxAction = (value) => editModeBoundingBoxAction.value = editModeBoundingBoxAction.value === value ? null : value
const isMoveAction = computed(() => props.editMode && editModeAction.value === EditModeActionTypes.move)
const isAddAction = computed(() => props.editMode && editModeAction.value === EditModeActionTypes.add)
const isAddFeatureAction = computed(() => isAddAction.value && editModeAddAction.value === EditModeAddActionTypes.feature)
const isAddMapAction = computed(() => isAddAction.value && editModeAddAction.value === EditModeAddActionTypes.map)
const isAddLabelAction = computed(() => isAddAction.value && editModeAddAction.value === EditModeAddActionTypes.label)
const isBoundingBoxAction = computed(() => props.editMode && editModeAction.value === EditModeActionTypes.boundingBox)
const isBoundingBoxAddAction = computed(() => isBoundingBoxAction.value && editModeBoundingBoxAction.value === EditModeBoundingBoxActionTypes.add)
const isBoundingBoxMoveAction = computed(() => isBoundingBoxAction.value && editModeBoundingBoxAction.value === EditModeBoundingBoxActionTypes.move)
const isInitialViewAction = computed(() => props.editMode && editModeAction.value === EditModeActionTypes.initialView)
const isRemoveAction = computed(() => props.editMode && editModeAction.value === EditModeActionTypes.remove)
const emitUpdatedGeoJsonObject = () => {
  const features = sourceVectorRef.value?.source.getFeatures()
  emit('updatedGeoJsonObject', geoJson.value.writeFeaturesObject(features))
}
const emitUpdatedMapProperties = () => {
  emit('updatedMapProperties', structuredClone(map.properties))
}
const modifyMoveExistingPointEnd = (event) => {
  emitUpdatedGeoJsonObject()
}
const drawNewFeatureEnd = (event) => {
  const featureId = selectedAddFeature.value.id
  const drawOpenLayersFeature = event.feature
  const existingOpenLayersFeature = sourceVectorRef.value?.source.getFeatures()
    .find((feature) => feature.get('resourcetype') == MapGeojsonResourceTypes.feature && feature.get('feature') === featureId)
  // add point to existing MultiPoint if applicable (cleanup drawn feature)
  if (existingOpenLayersFeature) {
    existingOpenLayersFeature.getGeometry().appendPoint(new Point(drawOpenLayersFeature.getGeometry().getCoordinates()[0]))
    nextTick(() => sourceVectorRef.value.source.removeFeature(drawOpenLayersFeature))
  // setup allow new drawn MultiPoint
  } else {
    drawOpenLayersFeature.set('feature', featureId)
    drawOpenLayersFeature.set('resourcetype', MapGeojsonResourceTypes.feature)
  }
  // make sure all the features are updated via using nextTick (for adding new MultiPoint)
  nextTick(() => emitUpdatedGeoJsonObject())
}
const drawNewMapEnd = (event) => {
  const mapId = selectedAddMap.value.id
  const drawOpenLayersFeature = event.feature
  const existingOpenLayersFeature = sourceVectorRef.value?.source.getFeatures()
    .find((feature) => feature.get('resourcetype') == MapGeojsonResourceTypes.transition && feature.get('map') === mapId)
  // add point to existing MultiPoint if applicable (cleanup drawn feature)
  if (existingOpenLayersFeature) {
    existingOpenLayersFeature.getGeometry().appendPoint(new Point(drawOpenLayersFeature.getGeometry().getCoordinates()[0]))
    nextTick(() => sourceVectorRef.value.source.removeFeature(drawOpenLayersFeature))
  // setup allow new drawn MultiPoint
  } else {
    drawOpenLayersFeature.set('map', mapId)
    drawOpenLayersFeature.set('resourcetype', MapGeojsonResourceTypes.transition)
  }
  // make sure all the features are updated via using nextTick (for adding new MultiPoint)
  nextTick(() => emitUpdatedGeoJsonObject())
}
const drawNewLabelEnd = (event) => {
  const drawOpenLayersFeature = event.feature
  const label = prompt("Enter the new map label...")
  if (label !== null && label.trim() !== '') {
    drawOpenLayersFeature.set('label', label)
    drawOpenLayersFeature.set('resourcetype', MapGeojsonResourceTypes.label)
    nextTick(() => emitUpdatedGeoJsonObject())
  } else {
    // remove the feature since it doesn't have a label
    nextTick(() => sourceVectorRef.value.source.removeFeature(drawOpenLayersFeature))
  }
}
const createBoundingBoxEnd = (event) => {
  const boundingBoxPolygon = fromExtent(event.target.getGeometry().getExtent())
  map.properties.bounding_box = boundingBoxPolygon.getCoordinates()
  boundingBox.value = structuredClone(map.properties.bounding_box)
  emitUpdatedMapProperties()
  editModeBoundingBoxAction.value = null
}
const transformBoundingBoxEnd = (event) => {
  const transformOpenLayersFeature = event.feature
  map.properties.bounding_box = transformOpenLayersFeature.getGeometry().getCoordinates()
  boundingBox.value = structuredClone(map.properties.bounding_box)
  emitUpdatedMapProperties()
}
const removeBoundingBox = () => {
  if (confirm('Are you sure you want to remove the bounding box?')) {
    if (map.properties.bounding_box) {
      delete map.properties.bounding_box
    }
    boundingBox.value = undefined
    emitUpdatedMapProperties()
  }
}
const setInitialViewToDefault = () => {
  if (confirm('Are you sure you want set the initial view to default values?')) {
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
      zoom: toRaw(zoom.value),
      rotation: toRaw(rotation.value),
      center: toRaw(center.value),
    }
    initial.value = structuredClone(map.properties.initial)
    emitUpdatedMapProperties()
    resetViewToInitial()
  }
}
const resetViewToInitial = () => {
  if (initial.value) {
    mapRef.value.map.getView().setZoom(initial.value.zoom)
    mapRef.value.map.getView().setRotation(initial.value.rotation)
    mapRef.value.map.getView().setCenter(initial.value.center)
  } else if (extent.value) {
    // hacky method to get the fit function to fit within the extent (instead of the extent within the map)
    const extentSize = getSize(extent.value)
    const extentAspectRatio = extentSize[0] / extentSize[1]
    const mapSize = mapRef.value.map.getSize()
    const mapAspectRatio = mapSize[0] / mapSize[1]
    if (extentAspectRatio < mapAspectRatio) {
      mapRef.value.map.getView().fit([extent.value[0], getCenter(extent.value)[1], extent.value[2], getCenter(extent.value)[1]], { constrainResolution: false })
    } else {
      mapRef.value.map.getView().fit([getCenter(extent.value)[0], extent.value[1], getCenter(extent.value)[0], extent.value[3]], { constrainResolution: false })
    }
    mapRef.value.map.getView().setRotation(0)
    mapRef.value.map.getView().setCenter(getCenter(extent.value))
  } else {
    mapRef.value.map.getView().setZoom(map.min_zoom && map.max_zoom ? (1.0 * map.max_zoom - map.min_zoom) / 2 : 0)
    mapRef.value.map.getView().setRotation(0)
    mapRef.value.map.getView().setCenter([0,0])
  }
}
const removedSelectedFeaturePoint = (event) => {
  if (confirm('Are you sure you want to remove this item?')) {
    const clickCoords = event.mapBrowserEvent.coordinate
    const removeOpenLayersFeature = event.selected[0]
    if (removeOpenLayersFeature.get('resourcetype') === MapGeojsonResourceTypes.label) {
      sourceVectorRef.value.source.removeFeature(removeOpenLayersFeature)
    } else {
      const coords = removeOpenLayersFeature.getGeometry().getCoordinates()
      if (coords.length >= 1) {
        const removeIndex = coords.reduce((result_index, current, current_index) => {
          const resultCoords = coords[result_index]
          const currentCoords = coords[current_index]
          const resultDist = Math.sqrt(Math.pow(clickCoords[0] - resultCoords[0], 2) + Math.pow(clickCoords[1] - resultCoords[1], 2))
          const currentDist = Math.sqrt(Math.pow(clickCoords[0] - currentCoords[0], 2) + Math.pow(clickCoords[1] - currentCoords[1], 2))
          return resultDist < currentDist ? result_index : current_index
        }, 0)
        coords.splice(removeIndex, 1)
        removeOpenLayersFeature.getGeometry().setCoordinates(coords)
      }
    }
    // make sure all the features are updated via using nextTick (for adding new MultiPoint)
    nextTick(() => emitUpdatedGeoJsonObject())
  }
  event.target.getFeatures().clear() // clear out the selection
}
const isMapFeatureFilter = (feature) => !!feature.get('resourcetype')
const isBoundingBoxFeatureFilter = (feature) => !feature.get('resourcetype')
const featuresLoadend = (event) => emitUpdatedGeoJsonObject()
// end edit actions
const {
  click: clickCondition,
} = inject('ol-selectconditions')
const resetTooltips = () => {
  nextTick(() => {
    mapRef.value.map.getTargetElement().querySelectorAll('[data-bs-toggle="tooltip"]').forEach(
      (tooltipTriggerEl) => Tooltip.getOrCreateInstance(tooltipTriggerEl, {container: mapRef.value.map.getTargetElement()}).hide()
    )
  })
}
watch(editModeAction, (oldValue, newValue) => {
  if (newValue != oldValue) { resetTooltips() }
})
onMounted(() => {
  resetViewToInitial()
  resetTooltips()
  mapRef.value.map.on('pointermove', (event) => {
    const openLayersFeature = mapRef.value.map.forEachFeatureAtPixel(event.pixel, (f) => f)
    if (openLayersFeature) {
      let label = ''
      if (openLayersFeature.get('resourcetype') === MapGeojsonResourceTypes.feature) {
        label = featuresObjectMap.get(openLayersFeature.get('feature')).title
      } else if (openLayersFeature.get('resourcetype') === MapGeojsonResourceTypes.transition) {
        label = mapsObjectMap.get(openLayersFeature.get('map')).label
      } else if (openLayersFeature.get('resourcetype') === MapGeojsonResourceTypes.label) {
        label = openLayersFeature.get('label')
      }
      hoverFeatureTooltipParams.value = {
        coords: event.coordinate,
        label,
      }
    } else {
      hoverFeatureTooltipParams.value = undefined
    }
    mouseCoords.value = event.coordinate
  })
})
</script>

<template>
  <UseFullscreen v-slot="{ isFullscreen, toggle: toggleFullscreen }">
    <div class="z-0 position-absolute top-0 bottom-0 start-0 end-0 overflow-hidden">
      <ol-map
        ref="mapRef"
        class="openlayers-map z-1 w-100 h-100 position-absolute"
        :loadTilesWhileAnimating="true"
        :loadTilesWhileInteracting="true"
        :controls="[]"
      >

        <ol-view
          :minZoom="map.min_zoom"
          :maxZoom="map.max_zoom"
          :projection="projection"
          :extent="editMode ? baseUnboundExtent : extent"
          :constrainOnlyCenter="false"
          :smoothExtentConstraint="true"
          @change:center="updateCenter"
          @change:resolution="updateZoom"
          @change:rotation="updateRotation"
        />

        <ol-tile-layer v-if="map.resourcetype === MapResourceTypes.xyzMap">
          <ol-source-xyz :url="map.url" :attributions="!!map.attributions ? map.attributions : undefined" />
        </ol-tile-layer>
        <ol-tile-layer v-if="map.resourcetype === MapResourceTypes.overheadImageMap">
          <ol-source-xyz :url="`${websiteOrigin}${map.tiles_dir}/{z}/{x}/{y}.${map.tile_format}`" :tileGrid="overheadMapTileGrid" :projection="projection" />
        </ol-tile-layer>

        <ol-vector-layer>
          <ol-source-vector
            ref="sourceVectorRef"
            :url="`${websiteOrigin}/api/admin/maps/${mapId}/geojson`" :format="geoJson"
            @featuresloadend="featuresLoadend"
          >
            <ol-interaction-modify v-if="isMoveAction"
              :filter="isMapFeatureFilter" @modifyend="modifyMoveExistingPointEnd"
            />
            <ol-interaction-draw v-if="isAddFeatureAction && selectedAddFeature"
              type="MultiPoint" @drawend="drawNewFeatureEnd"
            />
            <ol-interaction-draw v-if="isAddMapAction && selectedAddMap"
              type="MultiPoint" @drawend="drawNewMapEnd"
            />
            <ol-interaction-draw v-if="isAddLabelAction"
              type="Point" @drawend="drawNewLabelEnd"
            />
            <ol-interaction-select v-if="isRemoveAction"
              :condition="clickCondition" :filter="isMapFeatureFilter" @select="removedSelectedFeaturePoint"
            />
            <ol-style :overrideStyleFunction="overrideOpenLayersFeatureStyle"></ol-style>
          </ol-source-vector>
        </ol-vector-layer>
        <ol-vector-layer v-if="editMode">
          <ol-source-vector>
            <ol-feature v-if="boundingBox">
              <ol-geom-polygon :coordinates="boundingBox"/>
              <ol-style>
                <ol-style-stroke color="red" :width="2"></ol-style-stroke>
              </ol-style>
            </ol-feature>
            <ol-interaction-transform v-if="isBoundingBoxMoveAction"
              :filter="isBoundingBoxFeatureFilter"
              :scale="true" :rotate="true" :translate="true" :stretch="true" :keepAspectRatio="false"
              @rotateend="transformBoundingBoxEnd"
              @translateend="transformBoundingBoxEnd"
              @scaleend="transformBoundingBoxEnd"
            />
            <ol-interaction-drag-box v-if="isBoundingBoxAddAction"
              @boxend="createBoundingBoxEnd"
            />
          </ol-source-vector>
        </ol-vector-layer>

        <ol-overlay
          v-if="hoverFeatureTooltipParams"
          :position="hoverFeatureTooltipParams.coords"
          :positioning="bottom-center"
          :stopEvent="false"
          :insertFirst="false"
          :offset="[10, 0]"
        >
          <span class="badge text-bg-primary" v-html="hoverFeatureTooltipParams.label" />
        </ol-overlay>

        <ol-interaction-drag-rotate-and-zoom />
        <div class="z-3 position-absolute bottom-0 start-50 translate-middle-x btn-group text-center">
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
        <div class="z-3 position-absolute top-0 end-0 btn-group-vertical text-center">
          <button @click="() => { toggleFullscreen(); resetTooltips() }"
            type="button" class="btn btn-link text-light link-underline-opacity-0"
            data-bs-toggle="tooltip" data-bs-trigger="hover" data-bs-title="Toggle Fullscreen Mode"
          >
            <i v-if="!isFullscreen" class="bi bi-fullscreen"></i>
            <i v-if="isFullscreen" class="bi bi-fullscreen-exit"></i>
          </button>
          <button @click="resetRotation"
            type="button" class="rotation-btn btn btn-link text-light link-underline-opacity-0"
            :class="{'d-none': rotation === (initial?.rotation || 0) }"
            data-bs-toggle="tooltip" data-bs-trigger="hover" data-bs-title="Reset Rotation"
          >
            <i
              class="rotation-correction fa-solid fa-compass"
              :style="{
                'transform': `rotate(${(315 + (rotation - (initial?.rotation || 0)) * (180 / Math.PI)) % 360}deg)`
              }"
            ></i>
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
              data-bs-toggle="tooltip" data-bs-trigger="hover" data-bs-title="Modify Bounding Box"
              :class="{ active: isBoundingBoxAction }"
              @click="() => toggleEditModeAction(EditModeActionTypes.boundingBox)"
            >
              <i class="bi bi-bounding-box"></i>
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
          <div class="btn-group edit-actions" role="group" v-if="isBoundingBoxAction">
            <button type="button" class="btn btn-dark"
              data-bs-toggle="tooltip" data-bs-trigger="hover" data-bs-title="Add/Replace Bounding Box"
              :class="{ active: isBoundingBoxAddAction }"
              @click="() => toggleEditBoundingBoxAction(EditModeBoundingBoxActionTypes.add)"
            >
              <i class="bi bi-plus-lg"></i>
            </button>
            <button type="button" class="btn btn-dark"
              data-bs-toggle="tooltip" data-bs-trigger="hover" data-bs-title="Move Bounding Box"
              :class="{ active: isBoundingBoxMoveAction }"
              :disabled="!boundingBox"
              @click="() => toggleEditBoundingBoxAction(EditModeBoundingBoxActionTypes.move)"
            >
              <i class="bi bi-arrows-move"></i>
            </button>
            <button type="button" class="btn btn-danger"
              :disabled="!boundingBox"
              data-bs-toggle="tooltip" data-bs-trigger="hover" data-bs-title="Remove Bounding Box"
              @click="removeBoundingBox"
            >
              <i class="bi bi-trash"></i>
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
        <div class="z-3 position-absolute bottom-0 start-0" v-if="editMode && !!mouseCoords">
          <div class="ms-1 mb-1" v-if="map.feature_srid === 0">
            <div class="badge text-bg-light mb-1" v-html="`X: ${mouseCoords[0].toFixed(10)}`" /><br />
            <div class="badge text-bg-light mb-1" v-html="`Y: ${mouseCoords[1].toFixed(10)}`" /><br />
            <div class="badge text-bg-light" v-html="`Zoom: ${zoom.toFixed(10)}`" />
          </div>
          <div class="ms-1 mb-1" v-if="map.feature_srid === 4326">
            <div class="badge text-bg-light mb-1" v-html="`Lat: ${mouseCoords[1].toFixed(10)}`" /><br />
            <div class="badge text-bg-light mb-1" v-html="`Long: ${mouseCoords[0].toFixed(10)}`" /><br />
            <div class="badge text-bg-light" v-html="`Zoom: ${zoom.toFixed(10)}`" />
          </div>
          <div class="ms-1 mb-1" v-if="map.feature_srid === 3857">
            <div class="badge text-bg-light mb-1" v-html="`Lat: ${toLonLat(mouseCoords)[1].toFixed(10)}`" /><br />
            <div class="badge text-bg-light mb-1" v-html="`Long: ${toLonLat(mouseCoords)[0].toFixed(10)}`" /><br />
            <div class="badge text-bg-light" v-html="`Zoom: ${zoom.toFixed(10)}`" />
          </div>
        </div>
        <div class="z-3 position-absolute bottom-0 end-0 d-flex flex-column">
          <span class="badge text-bg-light ms-auto me-1 mb-1" v-if="!!map.attributions" v-html="map.attributions" />
          <span class="badge text-bg-light ms-auto me-1 mb-1" v-if="!!map.date_taken" v-html="`Taken on ${new Date(map.date_taken).toLocaleDateString()}`" />
        </div>
      </ol-map>
    </div>
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
}
.openlayers-map {
  cursor: grab;
  font-size: 0.8125rem;

  &:active {
    cursor: grabbing;
  }
}
</style>