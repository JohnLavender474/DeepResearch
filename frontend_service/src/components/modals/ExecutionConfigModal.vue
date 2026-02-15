<template>
  <div v-if="isOpen" class="modal-overlay" @click="emit('close')">
    <div
      class="modal-content"
      role="dialog"
      aria-modal="true"
      aria-label="Execution Config"
      @click.stop
    >
      <div class="modal-header">
        <h3>Execution Config</h3>
        <button
          type="button"
          class="close-button"
          @click="emit('close')"
          aria-label="Close execution config"
        >
          ✕
        </button>
      </div>

      <div class="modal-body">
        <div class="config-grid">
          <label class="config-field">
            <span>Process Type</span>
            <select
              :value="processType"
              :disabled="disabled"
              class="config-select"
              @change="onProcessTypeChange"
            >
              <option value="">Default Process</option>
              <option
                v-for="pt in processTypes"
                :key="pt"
                :value="pt"
              >
                {{ formatProcessType(pt) }}
              </option>
            </select>
          </label>

          <label class="config-field">
            <span>Model</span>
            <select
              :value="modelType"
              :disabled="disabled"
              class="config-select"
              @change="onModelTypeChange"
            >
              <option value="">Default Model</option>
              <option
                v-for="mt in modelTypes"
                :key="mt"
                :value="mt"
              >
                {{ mt }}
              </option>
            </select>
          </label>

          <div class="config-toggle-row">
            <span>Allow general-knowledge fallback when no RAG docs are found</span>
            <button
              type="button"
              class="toggle-switch"
              :class="{ active: allowGeneralKnowledgeFallback }"
              :disabled="disabled"
              role="switch"
              :aria-checked="allowGeneralKnowledgeFallback"
              @click="emit('update:allowGeneralKnowledgeFallback', !allowGeneralKnowledgeFallback)"
            >
              <span class="toggle-thumb" />
            </button>
          </div>          
        </div>
      </div>

      <div class="modal-actions">
        <button type="button" class="done-button" @click="emit('close')">Done</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface ExecutionConfigModalProps {
  isOpen: boolean
  disabled: boolean
  processTypes: string[]
  modelTypes: string[]
  processType: string
  modelType: string
  allowGeneralKnowledgeFallback: boolean
  allowWebSearch: boolean
}

const props = defineProps<ExecutionConfigModalProps>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'update:processType', value: string): void
  (e: 'update:modelType', value: string): void
  (e: 'update:allowGeneralKnowledgeFallback', value: boolean): void
  (e: 'update:allowWebSearch', value: boolean): void
}>()

const formatProcessType = (pt: string): string => {
  return pt
    .split('_')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ')
}

const onProcessTypeChange = (event: Event) => {
  emit('update:processType', (event.target as HTMLSelectElement).value)
}

const onModelTypeChange = (event: Event) => {
  emit('update:modelType', (event.target as HTMLSelectElement).value)
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(15, 23, 42, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background-color: var(--color-bg-2);
  border-radius: var(--size-border-radius-lg, 0.75rem);
  border: 1px solid var(--color-border);
  width: min(680px, 100%);
  max-height: min(90vh, 820px);
  overflow: auto;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1rem 0.75rem;
  border-bottom: 1px solid var(--color-border);
}

.modal-header h3 {
  margin: 0;
  font-size: 1rem;
  color: var(--color-text-primary);
}

.close-button {
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  font-size: 1rem;
  cursor: pointer;
  padding: 0.25rem;
}

.modal-body {
  padding: 1rem;
}

.config-grid {
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
}

.config-field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  color: var(--color-text-secondary);
  font-size: 0.85rem;
}

.config-select {
  padding: 0.75rem 1rem;
  font-size: 0.95rem;
  border: 1px solid var(--color-border);
  border-radius: var(--size-border-radius-sm);
  background-color: var(--color-bg-3);
  color: var(--color-text-primary);
  cursor: pointer;
  min-height: 44px;
}

.config-select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.1);
}

.config-select:disabled {
  background-color: var(--color-surface-hover);
  color: var(--color-text-tertiary);
  cursor: not-allowed;
}

.config-toggle-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  color: var(--color-text-secondary);
  font-size: 0.9rem;
}

.toggle-switch {
  width: 48px;
  height: 28px;
  border-radius: 999px;
  border: 1px solid var(--color-border);
  background-color: var(--color-surface-hover);
  position: relative;
  cursor: pointer;
  flex-shrink: 0;
  transition: background-color var(--transition-base), border-color var(--transition-base);
}

.toggle-switch.active {
  background-color: var(--color-primary);
  border-color: var(--color-primary);
}

.toggle-switch:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.toggle-thumb {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 22px;
  height: 22px;
  border-radius: 999px;
  background-color: #ffffff;
  transition: transform var(--transition-base);
}

.toggle-switch.active .toggle-thumb {
  transform: translateX(20px);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid var(--color-border);
  padding: 0.75rem 1rem 1rem;
}

.done-button {
  padding: 0.65rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: var(--size-border-radius-sm);
  background-color: var(--color-bg-3);
  color: var(--color-text-primary);
  cursor: pointer;
}

@media (max-width: 640px) {
  .modal-overlay {
    align-items: flex-end;
    padding: 0;
  }

  .modal-content {
    width: 100%;
    max-height: 92vh;
    border-bottom-left-radius: 0;
    border-bottom-right-radius: 0;
  }

  .config-toggle-row {
    font-size: 0.85rem;
  }
}
</style>
