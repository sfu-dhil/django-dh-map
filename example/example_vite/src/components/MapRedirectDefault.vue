<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { _stopAllMedia } from '../_utils.js'
import { useMapsStore, useFeaturesStore } from '../stores/data.js'

// make sure features and maps are loaded
const maps = await useMapsStore().getAll()
const features = await useFeaturesStore().getAll()
const router = useRouter()

onMounted(() => {
  if (maps.length > 0) {
    router.replace({ name: 'map', params: { id: maps[0].id } })
  }
})
</script>

<template>
  <div></div>
</template>

<style lang="scss" scoped>
</style>