<template>
  <div id="app">
    <header>
      <div class="header-content">
        <nav>
          <RouterLink to="/">Home</RouterLink>
          <RouterLink to="/research">Research</RouterLink>
        </nav>

        <button
          class="settings-button"
          title="Open settings"
          aria-label="Open settings"
          @click="isSettingsModalOpen = true"
        >
          <Settings :size="18" />
        </button>
      </div>
    </header>

    <main>
      <RouterView />
    </main>

    <ToastList :toasts="toasts" />

    <SettingsModal
      :is-open="isSettingsModalOpen"
      :response-mode="responseMode"
      @close="isSettingsModalOpen = false"
      @update:response-mode="setResponseMode"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink, RouterView } from 'vue-router'
import { Settings } from 'lucide-vue-next'

import ToastList from '@/components/ToastList.vue'
import SettingsModal from '@/components/modals/SettingsModal.vue'
import { useAppSettings } from '@/composables/useAppSettings'
import { useToasts } from '@/composables/useToasts'

const { toasts } = useToasts()
const { responseMode, setResponseMode } = useAppSettings()

const isSettingsModalOpen = ref(false)
</script>

<style scoped>
header {
  background-color: var(--color-bg-1);
  border-bottom: 1px solid var(--color-border);
  padding: 1rem 2rem;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

nav {
  display: flex;
  gap: 2rem;
}

.settings-button {
  border: 1px solid var(--color-border);
  background: var(--color-bg-2);
  color: var(--color-text-secondary);
  border-radius: var(--size-border-radius-sm);
  width: 2.2rem;
  height: 2.2rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all var(--transition-base);
}

.settings-button:hover {
  color: var(--color-text-primary);
  border-color: var(--color-primary);
  background: var(--color-surface-hover);
}

nav a {
  color: var(--color-text-secondary);
  text-decoration: none;
  font-weight: 500;
  transition: color var(--transition-base);
  position: relative;
}

nav a:hover {
  color: var(--color-primary);
}

nav a.router-link-active {
  color: var(--color-primary);
}

nav a.router-link-active::after {
  content: '';
  position: absolute;
  bottom: -1rem;
  left: 0;
  right: 0;
  height: 2px;
  background-color: var(--color-primary);
}

main {
  padding: 0;
  padding-top: 4rem;  
  width: 100%;
  height: calc(100vh - 2rem);
  overflow: hidden;
}
</style>
