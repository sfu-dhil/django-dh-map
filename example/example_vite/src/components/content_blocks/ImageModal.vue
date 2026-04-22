<script setup>
import { ref, onMounted, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { _stopAllMedia, toggleModal } from '../../_utils.js'
import { useDisplayImageModalStore } from '../../stores/display.js'
import { Tooltip } from 'bootstrap'

const {
  object,
  shown,
} = storeToRefs(useDisplayImageModalStore())

const modalRef = ref(null)

watch(shown, (newValue, oldValue) => {
  if (newValue !== oldValue) {
    _stopAllMedia()
    toggleModal(modalRef.value, newValue)
  }
})
onMounted(() => {
  toggleModal(modalRef.value, shown.value)
  modalRef.value.addEventListener('hidden.bs.modal', () => shown.value = false)
  modalRef.value.addEventListener('shown.bs.modal', () => shown.value = true)
  // setup tooltip (if needed)
  modalRef.value.querySelectorAll('carousel-caption i').forEach(
    (iconEl) => Tooltip.getOrCreateInstance(iconEl)
  )
})
</script>

<template>
  <div ref="modalRef" class="modal fade" tabindex="-1" data-bs-backdrop="static">
    <div class="modal-dialog modal-fullscreen">
      <div class="modal-content">
        <div class="modal-body p-0">
          <button type="button" class="btn-close bg-white position-fixed top-0 end-0 m-3 p-2" data-bs-dismiss="modal" aria-label="Close"></button>
          <div class="carousel h-100">
            <div class="text-center h-100">
              <img
                class="img-fluid h-100 object-fit-contain mx-auto"
                :src="object.original"
                :alt="object.description || ''"
              />
              <div class="carousel-caption" v-if="object.name || object.license">
                <h5 class="d-inline-block px-3 py-2">
                  {{ object.name || '' }} <i v-if="object.license" class="bi bi-info-circle" :title="object.license"
                    data-bs-toggle="tooltip" data-bs-html="true" data-bs-placement="top"></i>
                </h5>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.modal {
  --bs-modal-bg: transparent;
  .btn-close {
    --bs-btn-close-opacity: 1;
    z-index: calc(var(--bs-modal-zindex) + 5);
  }
}

.carousel {
  .carousel-item img {
    height: 100vmin;
  }
  .carousel-caption h5 {
    background-color: rgba(0,0,0,0.5);
    color: #fff !important;
  }
}
</style>