<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
    class="lucide-icon"
  >
    <path v-if="name === 'play'" d="M5 3l14 9-14 9V3z" />
    <path v-else-if="name === 'pause'" d="M6 4h4v16H6zm8 0h4v16h-4z" />
    <path v-else-if="name === 'stop'" d="M5 5h14v14H5z" />
    <path v-else-if="name === 'refresh'" d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67" />
    <path v-else-if="name === 'save'" d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2zM17 21v-8H7v8M7 3v5h8" />
    <path v-else-if="name === 'folder'" d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
    <path v-else-if="name === 'sliders'" d="M4 21v-7M4 10V3M12 21v-9M12 8V3M20 21v-5M20 12V3M1 14h6M9 8h6M17 16h6" />
    <path v-else-if="name === 'layers'" d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
    <path v-else-if="name === 'shield'" d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
    <path v-else-if="name === 'activity'" d="M22 12h-4l-3 9L9 3l-3 9H2" />
    <path v-else-if="name === 'cpu'" d="M18 4H6a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2zM9 9h6v6H9zM15 2v2M9 2v2M15 20v2M9 20v2M20 15h2M20 9h2M2 15h2M2 9h2" />
    <path v-else-if="name === 'trash'" d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
    <path v-else-if="name === 'download'" d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3" />
    <path v-else-if="name === 'check'" d="M20 6L9 17l-5-5" />
    <path v-else-if="name === 'chevron-left'" d="M15 18l-6-6 6-6" />
    <path v-else-if="name === 'chevron-right'" d="M9 18l6-6-6-6" />
    <path v-else-if="name === 'chevrons-left'" d="M11 17l-5-5 5-5M18 17l-5-5 5-5" />
    <path v-else-if="name === 'chevrons-right'" d="M13 17l5-5-5-5M6 17l5-5-5-5" />
    <path v-else-if="name === 'sidebar'" d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2zm5 0v16" />
  </svg>

</template>

<script setup lang="ts">
withDefaults(defineProps<{
  name: string
  size?: number
}>(), {
  size: 18
})
</script>

<style scoped>
.lucide-icon {
  display: inline-block;
  vertical-align: middle;
}
</style>
