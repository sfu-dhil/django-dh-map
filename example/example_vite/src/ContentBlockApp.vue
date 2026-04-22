<script setup>
import ContentBlock from './components/ContentBlock.vue'

const props = defineProps({
  contentBlocks: {
    type: Array,
    required: true,
  },
})
</script>

<template>
  <div v-if="contentBlocks.length > 0">
    <ContentBlock v-for="contentBlock in contentBlocks" :contentBlock="contentBlock" />
  </div>
</template>

<style lang="scss" scoped>
</style>