<script setup>
import { ref, onMounted, watch, computed, nextTick } from 'vue'
import { storeToRefs } from 'pinia'
import { useInfoPageStore } from '../stores/data.js'
import { useDisplayStore } from '../stores/display.js'
import { toggleOffcanvas } from '../_utils.js'

const {
  infoPageSelectionSidebarShown: shown,
  infoPageIdShown: shownId,
} = storeToRefs(useDisplayStore())

const objects = await useInfoPageStore().getAll()
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
      <h2 class="offcanvas-title h5">Info Pages</h2>
      <button type="button" class="btn-close" data-bs-dismiss="offcanvas" aria-label="Close"></button>
    </div>
    <div class="offcanvas-body" v-if="shown">
      <div
        v-for="object in objects" :key="object.id"
        class="card mb-3"
        @click="() => object.id !== shownId ? useDisplayStore().showInfoPage(object) : null"
      >
        <div class="d-flex justify-content-between align-items-start">
          <div class="card-body d-flex justify-content-between align-items-start">
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
}
</style>


