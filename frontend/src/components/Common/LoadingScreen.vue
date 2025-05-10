<template>
    <div class="fixed inset-0 flex items-center justify-center bg-white">
      <div class="text-center">
        <div class="w-12 h-12 border-4 border-gray-300 border-t-blue-500 rounded-full animate-spin" :style="spinnerStyle"></div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { computed } from 'vue'
  import { sessionStore } from '@/stores/session'
  
  const { branding } = sessionStore()
    
  // Use a contrasting color for the spinner if needed, or use the primary color
  const spinnerColor = computed(() => branding.data?.primary_color || '#2563eb')
  
  const spinnerStyle = computed(() => ({
    borderColor: `${spinnerColor.value} transparent ${spinnerColor.value} transparent`
  }))
  </script>