<template>
  <div class="home">
    <h1>Deep Research</h1>
    <div class="description markdown-content" v-html="renderedDescription"></div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'
import homeDescriptionMarkdown from '@/content/home-description.md?raw'

const renderedDescription = computed(() => marked(homeDescriptionMarkdown))
</script>

<style scoped>
.home {
  text-align: center;
  padding: 2rem;
  max-width: 1000px;
  margin: 0 auto;
}

h1 {
  color: var(--color-text-primary);
  margin-bottom: 1rem;
}

.description {
  text-align: left;
  color: var(--color-text-primary);
  background: var(--color-surface, transparent);
  border: 1px solid var(--color-border);
  border-radius: var(--size-border-radius);
  padding: 1.25rem;
}

:deep(.description h2) {
  color: var(--color-text-primary);
}

:deep(.description p),
:deep(.description li) {
  color: var(--color-text-secondary, var(--color-text-primary));
}
</style>
