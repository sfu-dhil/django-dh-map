<script setup>
import Openlayers from './components/Openlayers.vue'
import LoadingDots from './components/LoadingDots.vue'

const props = defineProps({
  mapId: {
    type: String,
    required: true,
  },
})

const mapId = parseInt(props.mapId)
</script>

<template>
  <div class="openlayers-preview-wrapper">
    <Suspense>
      <Openlayers :mapId="mapId" />
      <template #fallback><LoadingDots /></template>
    </Suspense>
  </div>
</template>

<style lang="scss" scoped>
.openlayers-preview-wrapper {
  position: relative;
  height: 400px;
  min-width: 400px;
  width: 100%;
}
</style>