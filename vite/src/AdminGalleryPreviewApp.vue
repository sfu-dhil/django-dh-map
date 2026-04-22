<script setup>
import { computed } from 'vue'

const props = defineProps({
  galleryImagesJson: {
    type: String,
    required: true,
  },
})

const images = computed(() => JSON.parse(props.galleryImagesJson))
</script>

<template>
  <div class="row row-cols-4 g-2">
    <div
      class="col p-0 m-0 gallery-image-thumbnail"
      v-for="image in images"
      :title="image.description"
    >
      <button
        type="button"
        class="btn p-0 m-0 position-relative w-100 h-100 text-primary"
      >
        <img :src="image.thumbnail" class="object-fit-cover" :alt="image.description || ''" />
        <div class="position-absolute top-0 bottom-0 start-0 end-0 overlay"></div>
        <i class="bi bi-search position-absolute top-50 start-50 translate-middle"></i>
      </button>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.gallery-image-thumbnail {
  .btn {
    overflow: hidden;
  }
  img {
    max-height: 110px;
    width: 100%;
    transition: all 0.6s;
  }
  i {
    visibility: hidden;
    color: #6495ED;
    font-size: 1em;
    transition: all .6s;
  }
  .overlay {
    background-color: rgba(var(--bs-body-bg-rgb), 0.5);
    display: none;
  }
  &:hover {
    img {
      transform: scale(1.15);
    }
    i {
      visibility: visible;
      font-size: 2em;
    }
    .overlay {
      display: inline-block !important;
      font-size: 2em;
    }
  }
}
</style>