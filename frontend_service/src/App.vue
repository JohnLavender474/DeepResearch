<template>
  <div id="app">
    <header>
      <nav>
        <RouterLink to="/">Home</RouterLink>
        <RouterLink to="/research">Research</RouterLink>
      </nav>
    </header>

    <main>
      <RouterView />
    </main>

    <ToastList :toasts="toasts" />
  </div>
</template>

<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import ToastList from '@/components/ToastList.vue'
import { useToasts } from '@/composables/useToasts'

const { toasts } = useToasts()
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

nav {
  display: flex;
  gap: 2rem;
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
