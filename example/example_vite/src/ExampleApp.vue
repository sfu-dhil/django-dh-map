<script setup>
import { storeToRefs } from 'pinia'
import { useRoute } from 'vue-router'
import { useDisplayStore, useDisplayImageModalStore, useDisplayImageGalleryModalStore } from './stores/display.js'
import WelcomeMessageModal from './components/WelcomeMessageModal.vue'
import LoadingDots from './components/LoadingDots.vue'
import MapSelectOffSidebar from './components/MapSelectOffSidebar.vue'
import FeatureSelectSidebar from './components/FeatureSelectSidebar.vue'
import FeatureSidebar from './components/FeatureSidebar.vue'
import InfoPageSelectSidebar from './components/InfoPageSelectSidebar.vue'
import InfoPageSidebar from './components/InfoPageSidebar.vue'
import ImageModal from './components/content_blocks/ImageModal.vue'
import ImageGalleryModal from './components/content_blocks/ImageGalleryModal.vue'

const route = useRoute()
const {
  featureIdShown,
  infoPageIdShown,
} = storeToRefs(useDisplayStore())
const {
  shown: imageModalShown,
  object: imageModalObject,
} = storeToRefs(useDisplayImageModalStore())
const {
  shown: galleryImageModalShown,
  objects: galleryImageModalObjects,
} = storeToRefs(useDisplayImageGalleryModalStore())
</script>

<template>
  <div class="position-relative w-100 h-100">
    <RouterView v-slot="{ Component }">
      <template v-if="Component">
        <Transition name="fade" mode="out-in">
          <Suspense>
            <component :is="Component" :key="route.fullPath" />
            <template #fallback><LoadingDots /></template>
          </Suspense>
        </Transition>
      </template>
    </RouterView>
    <Suspense>
      <MapSelectOffSidebar />
      <template #fallback><LoadingDots /></template>
    </Suspense>
    <Suspense>
      <InfoPageSelectSidebar />
      <template #fallback><LoadingDots /></template>
    </Suspense>
    <Suspense>
      <FeatureSelectSidebar />
      <template #fallback><LoadingDots /></template>
    </Suspense>
    <Suspense>
      <WelcomeMessageModal />
    </Suspense>
    <Suspense v-if="infoPageIdShown">
      <InfoPageSidebar :key="infoPageIdShown" />
    </Suspense>
    <Suspense v-if="featureIdShown">
      <FeatureSidebar :key="featureIdShown" />
    </Suspense>
    <ImageModal v-if="imageModalShown && imageModalObject" />
    <ImageGalleryModal v-if="galleryImageModalShown && galleryImageModalObjects && galleryImageModalObjects.length > 0" />
  </div>
</template>

<style lang="scss" scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>