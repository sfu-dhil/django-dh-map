<script setup>
import { ref, onMounted, watch, computed, nextTick } from 'vue'
import { storeToRefs } from 'pinia'
import { useFeaturesStore } from '../stores/data.js'
import { useDisplayStore } from '../stores/display.js'
import { toggleOffcanvas } from '../_utils.js'
import { IconResourceTypes } from '../_resourceTypes.js'

const {
  featureSelectionSidebarShown: shown,
  featureIdShown: shownId,
  featureIdHover: hoverId,
} = storeToRefs(useDisplayStore())

const objects = await useFeaturesStore().getAll()
const offCanvasRef = ref(null)

watch(shown, (newValue, oldValue) => {
  if (newValue !== oldValue) { toggleOffcanvas(offCanvasRef.value, newValue) }
})
onMounted(() => {
  toggleOffcanvas(offCanvasRef.value, shown.value)
  offCanvasRef.value.addEventListener('hidden.bs.offcanvas', () => shown.value = false)
  offCanvasRef.value.addEventListener('shown.bs.offcanvas', () => shown.value = true)
})
</script>

<template>
  <div ref="offCanvasRef" class="offcanvas offcanvas-start" data-bs-scroll="true" data-bs-backdrop="false" tabindex="-1">
    <div class="offcanvas-header">
      <h2 class="offcanvas-title h5">Features</h2>
      <button type="button" class="btn-close" data-bs-dismiss="offcanvas" aria-label="Close"></button>
    </div>
    <div class="offcanvas-body" v-if="shown">
      <div
        v-for="object in objects" :key="object.id"
        class="card mb-3"
        :class="{ 'hover': hoverId === object.id }"
        @click="() => object.id !== shownId ? useDisplayStore().showFeature(object) : null"
        @mouseover="() => hoverId = object.id" @mouseout="() => hoverId = null"
      >
        <div class="d-flex justify-content-between align-items-start">
          <img
            v-if="object.icon && object.icon.resourcetype === IconResourceTypes.image"
            :src="object.icon.thumbnail"
            class="img-fluid rounded-start m-0 p-0"
            :alt="object.title"
          />
          <div class="card-body d-flex justify-content-between align-items-start">
            <span
              v-if="object.icon && object.icon.resourcetype === IconResourceTypes.numbered"
              class="fw-bold me-2"
              v-html="`${object.icon.number}.`" />
            <p class="me-auto card-text" v-html="object.title" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.card {
  cursor: pointer;
  img {
    max-height: 200px;
    max-width: 100px;
  }
  &.hover {
    --bs-border-opacity: 1;
    border-color: rgba(var(--bs-primary-rgb),var(--bs-border-opacity)) !important;
  }
}
</style>


