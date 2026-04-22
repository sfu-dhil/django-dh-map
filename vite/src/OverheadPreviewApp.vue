<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import OverheadMap from './components/OverheadMap.vue'
import { getCenter } from 'ol/extent'
import { TileGrid } from 'ol/tilegrid'

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
  width: {
    type: String,
    required: true,
  },
  height: {
    type: String,
    required: true,
  },
  minZoom: {
    type: String,
    required: true,
  },
  maxZoom: {
    type: String,
    required: true,
  },
})

const imageExtent = [0, -Number(props.height), Number(props.width), 0]
const minZoom = ref(Number(props.minZoom))
const maxZoom = ref(Number(props.maxZoom))
const zoom = ref((1.0 * maxZoom.value - minZoom.value) / 2)
const rotation = ref(0)
const center = ref(getCenter(imageExtent))
const points = ref([])
const projection = {
  units: "pixels",
  extent: imageExtent,
}
const resolutions = []
for (let index = maxZoom.value; index >= minZoom.value; --index) {
  resolutions.push(2 ** (index))
}
const tileGrid = new TileGrid({
  extent: imageExtent,
  origin: [0, 0],
  resolutions: resolutions,
  tileSize: [Number(props.tileSize), Number(props.tileSize)],
})
</script>

<template>
  <div class="overhead-preview-wrapper">
    <OverheadMap
      v-model:minZoom="minZoom" v-model:maxZoom="maxZoom" v-model:zoom="zoom"
      v-model:rotation="rotation" v-model:center="center"
      v-model:points="points"
      :tileGrid="tileGrid" :projection="projection"
      :tilesDir="tilesDir" :tileFormat="tileFormat"
    ></OverheadMap>
  </div>
</template>

<style lang="scss" scoped>
.overhead-preview-wrapper {
  position: relative;
  height: 400px;
  min-width: 400px;
  width: 100%;
}
</style>