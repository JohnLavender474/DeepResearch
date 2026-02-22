<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen" class="modal-overlay" @click="closeModal">
        <div class="modal-container" @click.stop>
          <div class="modal-header">
            <h3 class="modal-title">Settings</h3>
            <button class="close-button" @click="closeModal" title="Close">
              <X :size="20" />
            </button>
          </div>

          <div class="modal-body">
            <div class="setting-row">
              <div class="setting-text">
                <div class="setting-title">AI Response View</div>
                <div class="setting-description">
                  Choose how assistant responses are displayed in chat.
                </div>
              </div>

              <div class="toggle-group" role="radiogroup" aria-label="AI response view">
                <button
                  class="toggle-option"
                  :class="{ active: responseMode === 'decomposed' }"
                  @click="onModeChange('decomposed')"
                  role="radio"
                  :aria-checked="responseMode === 'decomposed'"
                >
                  Decomposed
                </button>
                <button
                  class="toggle-option"
                  :class="{ active: responseMode === 'simple' }"
                  @click="onModeChange('simple')"
                  role="radio"
                  :aria-checked="responseMode === 'simple'"
                >
                  Simple
                </button>
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <button class="close-button-text" @click="closeModal">
              Close
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { watch } from 'vue'
import { X } from 'lucide-vue-next'

import type { ResponseMode } from '@/composables/useAppSettings'


interface SettingsModalProps {
  isOpen: boolean
  responseMode: ResponseMode
}

const props = defineProps<SettingsModalProps>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'update:responseMode', mode: ResponseMode): void
}>()

const closeModal = () => {
  emit('close')
}

const onModeChange = (mode: ResponseMode) => {
  emit('update:responseMode', mode)
}

watch(() => props.isOpen, (newValue) => {
  if (newValue) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(15, 23, 42, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-container {
  background: var(--color-bg-1);
  border: 1px solid var(--color-border);
  border-radius: var(--size-border-radius);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
  max-width: 560px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--color-border);
}

.modal-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.close-button {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  color: var(--color-text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--size-border-radius-sm);
  transition: all var(--transition-base);
}

.close-button:hover {
  background: var(--color-surface-hover);
  color: var(--color-text-primary);
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.setting-row {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.setting-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.setting-description {
  margin-top: 0.25rem;
  font-size: 0.85rem;
  color: var(--color-text-secondary);
}

.toggle-group {
  display: inline-flex;
  border: 1px solid var(--color-border);
  border-radius: var(--size-border-radius-sm);
  overflow: hidden;
  width: fit-content;
}

.toggle-option {
  border: none;
  background: var(--color-bg-2);
  color: var(--color-text-secondary);
  padding: 0.45rem 0.85rem;
  cursor: pointer;
  transition: all var(--transition-base);
  font-size: 0.85rem;
  font-weight: 500;
}

.toggle-option:hover {
  background: var(--color-surface-hover);
  color: var(--color-text-primary);
}

.toggle-option.active {
  background: var(--color-primary);
  color: white;
}

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--color-border);
}

.close-button-text {
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: var(--size-border-radius);
  padding: 0.5rem 1rem;
  cursor: pointer;
  color: var(--color-text-primary);
  transition: all var(--transition-base);
  font-size: 0.875rem;
  font-weight: 500;
}

.close-button-text:hover {
  background: var(--color-surface-hover);
  color: var(--color-text-primary);
  border-color: var(--color-border-light);
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity var(--transition-base);
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>
