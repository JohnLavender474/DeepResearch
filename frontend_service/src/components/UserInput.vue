<template>
  <div class="user-input">
    <div class="header">
      <button
        type="button"
        class="toggle-button"
        @click="isCollapsed = !isCollapsed"
        :aria-label="isCollapsed ? 'Show input' : 'Hide input'"
      >
        <svg
          :class="{ rotated: !isCollapsed }"
          xmlns="http://www.w3.org/2000/svg"
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <polyline points="18 15 12 9 6 15"></polyline>
        </svg>
      </button>
    </div>

    <form v-show="!isCollapsed" @submit.prevent="onSubmit" class="input-form">
      <textarea
        ref="textareaRef"
        v-model="query"
        placeholder="Enter your research query..."
        rows="4"
        :disabled="isInputDisabled"
        @keydown.meta.enter="onSubmit"
      ></textarea>

      <div class="submit-row">
        <button
          type="button"
          class="config-button"
          :disabled="isInputDisabled"
          @click="isConfigModalOpen = true"
        >
          Edit Execution Config
        </button>

        <div class="submit-actions">
          <button type="submit" :disabled="isInputDisabled || !isValidInput">
            {{ submitButtonText }}
          </button>

          <button
            v-if="props.chatStatus === 'running'"
            type="button"
            class="stop-button"
            @click="onStop"
          >
            Stop
          </button>
        </div>
      </div>

      <ExecutionConfigModal
        :is-open="isConfigModalOpen"
        :disabled="isInputDisabled"
        :process-types="processTypes"
        :model-types="availableModelTypes"
        :process-type="selectedProcessType"
        :model-type="selectedModelType"
        :allow-general-knowledge-fallback="allowGeneralKnowledge"
        :allow-web-search="allowWebSearch"
        @close="isConfigModalOpen = false"
        @update:process-type="selectedProcessType = $event"
        @update:model-type="selectedModelType = $event"
        @update:allow-general-knowledge-fallback="allowGeneralKnowledge = $event"
        @update:allow-web-search="allowWebSearch = $event"
      />
    </form>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

import ExecutionConfigModal from '@/components/modals/ExecutionConfigModal.vue'
import type { ChatStatus } from '@/model/chatStatus'
import type UserQueryRequest from '@/model/userQueryRequest'
import { isDummyAiAllowed } from '@/config'

interface UserInputProps {
  chatStatus: ChatStatus
  processTypes?: string[]
  modelTypes?: string[]
}

const props = withDefaults(defineProps<UserInputProps>(), {
  processTypes: () => [],
  modelTypes: () => [],
})

const emit = defineEmits<{
  (e: 'submit', request: UserQueryRequest): void
  (e: 'stop'): void
}>()

const query = ref('')
const selectedProcessType = ref('')
const selectedModelType = ref('')
const allowGeneralKnowledge = ref(true)
const allowWebSearch = ref(false)
const isConfigModalOpen = ref(false)
const isCollapsed = ref(false)
const textareaRef = ref<HTMLTextAreaElement | null>(null)

const isInputDisabled = computed(() => props.chatStatus !== 'idle')
const isValidInput = computed(() => query.value.trim().length > 0)

const availableModelTypes = computed(() => {
  if (isDummyAiAllowed()) {
    return props.modelTypes
  }

  return props.modelTypes.filter((modelType) => modelType !== 'dummy')
})

const submitButtonText = computed(() => {
  if (!query.value.trim()) {
    return 'Type in a prompt...'
  }
  if (props.chatStatus === 'loading') {
    return 'Loading...'
  }
  if (props.chatStatus === 'running') {
    return 'Processing...'
  }
  return 'Submit Query'
})

const onSubmit = () => {
  if (query.value.trim() && !isInputDisabled.value) {
    const modelSelection =
      selectedModelType.value === 'dummy' && !isDummyAiAllowed()
        ? undefined
        : selectedModelType.value || undefined

    emit('submit', {
      query: query.value,
      executionConfig: {
        processOverride: selectedProcessType.value || undefined,
        modelSelection,
        allowGeneralKnowledgeFallback: allowGeneralKnowledge.value,
        allowWebSearch: allowWebSearch.value,
      },
    })
    query.value = ''
  }
}

const onStop = () => {
  emit('stop')
}

const focus = () => {
  isCollapsed.value = false
  textareaRef.value?.focus()
}

const clear = () => {
  query.value = ''
}

const resetExecutionConfig = () => {
  selectedProcessType.value = ''
  selectedModelType.value = ''
  allowGeneralKnowledge.value = true
  allowWebSearch.value = false
}

defineExpose({
  focus,
  clear,
  resetExecutionConfig,
})
</script>

<style scoped>
.user-input {
  padding: 0.5rem 1.5rem 1.5rem;
  border-top: 1px solid var(--color-border);
  background-color: var(--color-bg-2);
  flex-shrink: 0;
}

.header {
  display: flex;
  justify-content: center;
  margin-bottom: 0.5rem;
}

.toggle-button {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  color: var(--color-text-secondary);
  transition: color var(--transition-base);
  display: flex;
  align-items: center;
  justify-content: center;
}

.toggle-button:hover {
  color: var(--color-primary);
}

.toggle-button svg {
  transition: transform var(--transition-slow);
}

.toggle-button svg.rotated {
  transform: rotate(180deg);
}

.input-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.submit-row {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
}

.submit-actions {
  margin-left: auto;
  display: flex;
  gap: 0.75rem;
}

.config-button {
  padding: 0.75rem 1rem;
  font-size: 0.9rem;
  border: 1px solid var(--color-border);
  border-radius: var(--size-border-radius-sm);
  background-color: var(--color-bg-3);
  color: var(--color-text-primary);
  cursor: pointer;
  transition: border-color var(--transition-base);
}

.config-button:hover:not(:disabled) {
  border-color: var(--color-primary);
}

.config-button:disabled {
  background-color: var(--color-surface-hover);
  color: var(--color-text-tertiary);
  cursor: not-allowed;
}

textarea {
  padding: 1rem;
  font-size: 1rem;
  border: 1px solid var(--color-border);
  border-radius: var(--size-border-radius-sm);
  font-family: inherit;
  resize: none;
  transition: border-color var(--transition-base);
  background-color: var(--color-bg-3);
  color: var(--color-text-primary);
}

textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.1);
}

textarea:disabled {
  background-color: var(--color-surface-hover);
  color: var(--color-text-tertiary);
  cursor: not-allowed;
}

button[type='submit'] {
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--size-border-radius-sm);
  cursor: pointer;
  transition: background-color var(--transition-base);
  font-weight: 500;
}

button[type='submit']:hover:not(:disabled) {
  background-color: var(--color-primary-dark);
}

button[type='submit']:disabled {
  background-color: var(--color-border);
  cursor: not-allowed;
}

.stop-button {
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  background-color: var(--color-error-bg, #dc2626);
  color: white;
  border: 1px solid var(--color-error-border, #b91c1c);
  border-radius: var(--size-border-radius-sm);
  cursor: pointer;
  transition: background-color var(--transition-base);
  font-weight: 500;
}

.stop-button:hover {
  background-color: var(--color-error-border, #b91c1c);
}

@media (max-width: 640px) {
  .submit-row {
    flex-wrap: wrap;
  }

  .submit-actions {
    margin-left: 0;
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
