<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import { storeToRefs } from 'pinia'
import { _stopAllMedia, toggleModal } from '../../_utils.js'
import { useDisplayImageGalleryModalStore } from '../../stores/display.js'
import { Tooltip, Carousel } from 'bootstrap'

const {
  objects,
  shown,
  galleryIndex,
} = storeToRefs(useDisplayImageGalleryModalStore())

const modalRef = ref(null)
const carouselRef = ref(null)

const carouselTo = (to) => {
  const bsCarousel = Carousel.getOrCreateInstance(carouselRef.value)
  bsCarousel.to(to)
}
const carouselPrevious = () => {
  const bsCarousel = Carousel.getOrCreateInstance(carouselRef.value)
  bsCarousel.prev()
}
const carouselNext = () => {
  const bsCarousel = Carousel.getOrCreateInstance(carouselRef.value)
  bsCarousel.next()
}
const setupCarousel = () => {
  if (carouselRef.value) {
    const bsCarousel = Carousel.getOrCreateInstance(carouselRef.value)
    carouselRef.value.addEventListener('slid.bs.carousel', event => {
      galleryIndex.value = event.to
    })
  }
}
watch(shown, (newValue, oldValue) => {
  if (newValue !== oldValue) {
    _stopAllMedia()
    toggleModal(modalRef.value, newValue)
    if (newValue) { nextTick(setupCarousel) }
  }
})
watch(galleryIndex, (newValue, oldValue) => {
  if (newValue !== oldValue) { nextTick(setupCarousel) }
})
onMounted(() => {
  toggleModal(modalRef.value, shown.value)
  modalRef.value.addEventListener('hidden.bs.modal', () => shown.value = false)
  modalRef.value.addEventListener('shown.bs.modal', () => shown.value = true)
  // setup carousel
  nextTick(setupCarousel)
  // setup tooltips (if needed)
  modalRef.value.querySelectorAll('carousel-caption i').forEach(
    (iconEl) => Tooltip.getOrCreateInstance(iconEl).hide()
  )
})
</script>

<template>
  <div ref="modalRef" class="modal fade" tabindex="-1" data-bs-backdrop="static">
    <div class="modal-dialog modal-fullscreen">
      <div class="modal-content">
        <div class="modal-body p-0">
          <button type="button" class="btn-close bg-white position-fixed top-0 end-0 m-3 p-2" data-bs-dismiss="modal" aria-label="Close"></button>
          <div ref="carouselRef" class="carousel slide h-100" data-bs-ride="false">
            <div class="carousel-inner h-100">
              <div
                v-for="(object, index) in objects" :key="object.id"
                class="carousel-item text-center h-100"
                 :class="{ 'active': index === galleryIndex }"
              >
                <img
                  class="img-fluid h-100 object-fit-contain mx-auto"
                  :src="object.original"
                  :alt="object.description || ''"
                />
                <div class="carousel-caption">
                  <h5 class="d-inline-block px-3 py-2">
                    {{ index+1 }} of {{ objects.length }} <br />
                    {{ object.name || '' }} <i v-if="object.license"
                      class="bi bi-info-circle" :title="object.license"
                      data-bs-toggle="tooltip" data-bs-html="true" data-bs-placement="top"
                    ></i>
                  </h5>
                </div>
              </div>
            </div>
            <div class="carousel-indicators">
              <button
                v-for="(object, index) in objects" type="button"
                data-bs-target="" :data-bs-slide-to="index"
                :class="{ 'active': index === galleryIndex }"
                @click="() => carouselTo(index)"
              ></button>
            </div>
            <button type="button" class="carousel-control-prev" @click="carouselPrevious" data-bs-target="" data-bs-slide="prev">
              <span class="carousel-control-prev-icon" aria-hidden="true"></span>
              <span class="visually-hidden">Previous</span>
            </button>
            <button type="button" class="carousel-control-next" @click="carouselNext" data-bs-target="" data-bs-slide="next">
              <span class="carousel-control-next-icon" aria-hidden="true"></span>
              <span class="visually-hidden">Next</span>
            </button>
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

  .carousel-control-next-icon,
  .carousel-control-prev-icon {
    background-color: rgba(0,0,0,0.5);
    height: 4rem;
    width: 4rem;
    filter: none;
  }
  .carousel-indicators [data-bs-target] {
    background-color: #fff !important;
  }
}
</style>