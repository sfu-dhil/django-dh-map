

<script setup>
import Pannellum from './components/Pannellum.vue'
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
  <div class="pannellum-preview-wrapper">
    <Suspense>
      <Pannellum :mapId="mapId" />
      <template #fallback><LoadingDots /></template>
    </Suspense>
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