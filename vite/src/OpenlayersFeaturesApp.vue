<script setup>
import Openlayers from './components/Openlayers.vue'
import LoadingDots from './components/LoadingDots.vue'

const props = defineProps({
  formJsonInputId: {
    type: String,
    required: true,
  },
  formPropertiesInputId: {
    type: String,
    required: true,
  },
  mapId: {
    type: String,
    required: true,
  },
})
const mapId = parseInt(props.mapId)
const handleUpdatedGeoJsonObject = (geoJsonObject) => document.getElementById(props.formJsonInputId).value = JSON.stringify(geoJsonObject)
const handleUpdatedMapProperties = (properties) => document.getElementById(props.formPropertiesInputId).value = JSON.stringify(properties)
</script>

<template>
  <div class="openlayers-features-wrapper">
    <Suspense>
      <Openlayers
        :mapId="mapId" :editMode="true"
        @updatedGeoJsonObject="handleUpdatedGeoJsonObject"
        @updatedMapProperties="handleUpdatedMapProperties"
      />
      <template #fallback><LoadingDots /></template>
    </Suspense>
  </div>
</template>

<style lang="scss" scoped>
.openlayers-features-wrapper {
  position: relative;
  height: 600px;
  min-width: 500px;
  max-width: 1000px;
  width: 100%;
}
</style>