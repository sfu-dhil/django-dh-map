<script setup>
import { ref, onMounted, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useStaticContentStore } from '../stores/data.js'
import { useDisplayStore } from '../stores/display.js'
import ContentBlock from './ContentBlock.vue'
import { _stopAllMedia, toggleModal } from '../_utils.js'

const {
  welcomeModalShown: shown,
} = storeToRefs(useDisplayStore())

const staticContent = await useStaticContentStore().get()
const welcomeModalContent = staticContent.welcome

const modalRef = ref(null)

watch(shown, (newValue, oldValue) => {
  if (newValue !== oldValue) { toggleModal(modalRef.value, welcomeModalContent.display && newValue) }
})
onMounted(() => {
  useDisplayStore().forceShowInitialWelcomeMessage()
  toggleModal(modalRef.value, welcomeModalContent.display && shown.value)
  modalRef.value.addEventListener('hidden.bs.modal', () => {
    _stopAllMedia()
    shown.value = false
  })
  modalRef.value.addEventListener('shown.bs.modal', () => shown.value = true)
})
</script>

<template>
  <div ref="modalRef" class="modal fade" data-bs-backdrop="static" tabindex="-1">
    <div class="modal-dialog modal-fullscreen-lg-down modal-lg modal-dialog-centered modal-dialog-scrollable">
      <div class="modal-content">
        <div class="modal-header align-items-start">
          <div class=w-100>
            <h1 class="modal-title text-center" v-html="welcomeModalContent.title || 'Welcome'" />
          </div>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <div v-if="welcomeModalContent.content_item && welcomeModalContent.content_item.content_blocks && welcomeModalContent.content_item.content_blocks.length > 0">
            <ContentBlock v-for="contentBlock in welcomeModalContent.content_item.content_blocks" :contentBlock="contentBlock" />
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-primary mx-auto" data-bs-dismiss="modal">{{ welcomeModalContent.close_button_label || 'Close' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
</style>