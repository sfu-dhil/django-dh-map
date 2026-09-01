<script setup>
import { ref, inject, onMounted, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import { Style, Text, Fill, Stroke, Circle, Icon } from 'ol/style'
import { TileGrid } from 'ol/tilegrid'
import { easeOut } from 'ol/easing'
import { GeoJSON } from 'ol/format'
import { useMapsStore, useFeaturesStore } from '../../stores/data.js'
import { useDisplayStore, useDisplayOpenlayersStore } from '../../stores/display.js'
import { _getPaginatedApiResources } from '../../_utils.js'
import { MapGeojsonResourceTypes, IconResourceTypes, MapResourceTypes } from '../../_resourceTypes.js'

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
  baseUnboundExtent,
  extent,
  center,
  zoom,
  rotation,
} = storeToRefs(useDisplayOpenlayersStore())

const props = defineProps({
  mapId: { type: Number, required: true },
})
const map = await useMapsStore().getById(props.mapId)
useDisplayOpenlayersStore().init(map)
const websiteOrigin = window.location.origin
const iconCanvasMap = new Map()
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
const resetRotation = () => mapRef.value.map.getView().animate({ rotation: (map.properties?.initial?.rotation || 0), easing: easeOut })
defineExpose({ panUp, panDown, panLeft, panRight, zoomIn, zoomOut, resetRotation })
const updateCenter = (event) => center.value = event.target.getCenter()
const updateZoom = (event) => zoom.value = event.target.getZoom()
const updateRotation = (event) => rotation.value = event.target.getRotation()
const featureStyle = (openLayersFeature) => {
  const feature = featuresObjectMap.value.get(openLayersFeature.get('feature'))
  const isHighlighted = featureIdHover.value === feature.id
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
          stroke: new Stroke({ color: isHighlighted ? 'rgba(13, 110, 353, 1)' : 'white', width: 3 })
        }),
        zIndex: isHighlighted ? Infinity - 1 : 0
      }),
      new Style({
        image: new Icon({
          img: iconCanvasMap.get(icon.id),
          imgSize: [icon.size, icon.size]
        }),
        zIndex: isHighlighted ? Infinity : 1
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
          stroke: new Stroke({ color: isHighlighted ? 'rgba(13, 110, 353, 1)' : 'white', width: 3 }),
        }),
        zIndex: isHighlighted ? Infinity - 1 : 0
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
        zIndex: isHighlighted ? Infinity : 1
      }),
    ]
  } else {
    // default icon
    return new Style({
      image: new Circle({
        radius: 6,
        fill: new Fill({ color: '#6495ED' }),
        stroke: new Stroke({ color: isHighlighted ? 'rgba(13, 110, 353, 1)' : 'white', width: 1.25 }),
      }),
      zIndex: isHighlighted ? Infinity : 0
    })
  }
}
const mapTransitionStyle = (openLayersFeature) => {
  const map = mapsObjectMap.value.get(openLayersFeature.get('map'))
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
const isMapFeatureFilter = (feature) => !!feature.get('resourcetype')
const hoverFeature = (event) => {
  const openLayersFeature = event.selected.length > 0 ? event.selected[0] : null
  if (openLayersFeature && openLayersFeature.get('resourcetype') === MapGeojsonResourceTypes.feature) {
    const feature = featuresObjectMap.value.get(openLayersFeature.get('feature'))
    featureIdHover.value = feature.id
  } else {
    featureIdHover.value = null
  }
}
const clickFeature = (event) => {
  const openLayersFeature = event.selected.length > 0 ? event.selected[0] : null
  if (openLayersFeature) {
    if (openLayersFeature.get('resourcetype') === MapGeojsonResourceTypes.feature) {
      const feature = featuresObjectMap.value.get(openLayersFeature.get('feature'))
      useDisplayStore().showFeature(feature)
    } else if (openLayersFeature.get('resourcetype') === MapGeojsonResourceTypes.transition) {
      router.push({ name: 'map', params: { id: openLayersFeature.get('map') } })
    } else if (openLayersFeature.get('resourcetype') === MapGeojsonResourceTypes.label) {
      // do nothing
    }
    event.target.getFeatures().clear()
  }
}
const {
  pointerMove: pointerMoveCondition,
  click: clickCondition,
} = inject('ol-selectconditions')
onMounted(() => {
  mapRef.value.map.getView().setZoom(zoom.value)
  mapRef.value.map.getView().setRotation(rotation.value)
  mapRef.value.map.getView().setCenter(center.value)
  mapRef.value.map.on('pointermove', (event) => {
    const openLayersFeature = mapRef.value.map.forEachFeatureAtPixel(event.pixel, (f) => f)
    if (openLayersFeature) {
      let label = ''
      if (openLayersFeature.get('resourcetype') === MapGeojsonResourceTypes.feature) {
        label = featuresObjectMap.value.get(openLayersFeature.get('feature')).title
      } else if (openLayersFeature.get('resourcetype') === MapGeojsonResourceTypes.transition) {
        label = mapsObjectMap.value.get(openLayersFeature.get('map')).label
      } else if (openLayersFeature.get('resourcetype') === MapGeojsonResourceTypes.label) {
        // no label
      }
      hoverFeatureTooltipParams.value = {
        coords: event.coordinate,
        label,
      }
    } else {
      hoverFeatureTooltipParams.value = undefined
    }
  })
})
</script>

<template>
  <ol-map
    ref="mapRef"
    class="openlayers-map z-1 w-100 h-100 position-absolute"
    :class="{ 'feature-hover': !!hoverFeatureTooltipParams && !!hoverFeatureTooltipParams.label }"
    :loadTilesWhileAnimating="true"
    :loadTilesWhileInteracting="true"
    :controls="[]"
  >

    <ol-view
      :minZoom="map.min_zoom"
      :maxZoom="map.max_zoom"
      :projection="projection"
      :extent="extent"
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
        :url="`${websiteOrigin}/api/maps/${map.id}/geojson`" :format="geoJson"
      >
        <ol-style :overrideStyleFunction="overrideOpenLayersFeatureStyle"></ol-style>
        <ol-interaction-select :filter="isMapFeatureFilter" @select="hoverFeature" :condition="pointerMoveCondition">
          <ol-style :overrideStyleFunction="overrideOpenLayersFeatureStyle"></ol-style>
        </ol-interaction-select>
        <ol-interaction-select :filter="isMapFeatureFilter" @select="clickFeature" :condition="clickCondition">
          <ol-style :overrideStyleFunction="overrideOpenLayersFeatureStyle"></ol-style>
        </ol-interaction-select>
      </ol-source-vector>
    </ol-vector-layer>

    <ol-overlay
      v-if="hoverFeatureTooltipParams"
      :position="hoverFeatureTooltipParams.coords"
      :stopEvent="false"
      :insertFirst="false"
      :offset="[10, 0]"
    >
      <span class="badge text-bg-primary" v-html="hoverFeatureTooltipParams.label" />
    </ol-overlay>

    <ol-interaction-drag-rotate-and-zoom />
  </ol-map>
</template>

<style lang="scss" scoped>
.openlayers-map {
  cursor: grab;

  &:active {
    cursor: grabbing;
  }
  &.feature-hover {
    cursor: pointer;
  }
}
</style>