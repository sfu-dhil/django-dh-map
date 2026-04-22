

<script setup>
</script>

<template>
  <div class="position-absolute top-0 start-0 bottom-0 end-0 bg-black bg-opacity-75">
    <div class="position-absolute top-50 start-50 translate-middle text-center">
      <div class="spinner-border"></div>
      <div class="fw-bold loading-dots" role="status">Loading...</div>
    </div>
  </div>
</template>

<style scoped>
.loading-dots {
  font-family: monospace;
  clip-path: inset(0 3ch 0 0);
  animation: loading_dots 1s steps(4, jump-none) infinite;
}
@keyframes loading_dots {
  to {
    clip-path: inset(0)
  }
}
</style>