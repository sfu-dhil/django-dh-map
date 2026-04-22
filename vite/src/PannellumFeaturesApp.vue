

<script setup>
import Pannellum from './components/Pannellum.vue'
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
const handleUpdatedHotSpotsGeoJson = (hotSpotsGeoJson) => document.getElementById(props.formJsonInputId).value = JSON.stringify(hotSpotsGeoJson)
const handleUpdatedMapProperties = (properties) => document.getElementById(props.formPropertiesInputId).value = JSON.stringify(properties)
</script>

<template>
  <div class="pannellum-preview-wrapper">
    <Suspense>
      <Pannellum
        :mapId="mapId" :editMode="true"
        @updatedHotSpotsGeoJson="handleUpdatedHotSpotsGeoJson"
        @updatedMapProperties="handleUpdatedMapProperties"
      />
      <template #fallback><LoadingDots /></template>
    </Suspense>
  </div>
</template>

<style lang="scss" scoped>
.pannellum-preview-wrapper {
  position: relative;
  height: 600px;
  width: 1000px;
}
</style>