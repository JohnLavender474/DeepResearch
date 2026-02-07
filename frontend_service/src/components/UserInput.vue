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
          :class="{ 'rotated': !isCollapsed }"
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

    <form
      v-show="!isCollapsed"
      @submit.prevent="onSubmit"
      class="input-form"
    >
      <textarea
        ref="textareaRef"
        v-model="query"
        placeholder="Enter your research query..."
        rows="4"
        :disabled="disabled"
        @keydown.meta.enter="onSubmit"        
      ></textarea>

      <div class="submit-row">
        <select
          v-model="selectedModelType"
          :disabled="disabled"
          class="model-select"
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

        <select
          v-model="selectedProcessType"
          :disabled="disabled"
          class="process-select"
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

        <button
          type="submit"
          :disabled="disabled || !isValidInput"
        >
          {{ submitButtonText }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

import type UserQueryRequest from '@/model/userQueryRequest'


interface UserInputProps {
  disabled?: boolean
  loading?: boolean
  processTypes?: string[]
  modelTypes?: string[]
}

const props = withDefaults(defineProps<UserInputProps>(), {
  disabled: false,
  loading: false,
  processTypes: () => [],
  modelTypes: () => [],
})

const emit = defineEmits<{
  (e: 'submit', request: UserQueryRequest): void
}>()

const query = ref('')
const selectedProcessType = ref('')
const selectedModelType = ref('')
const isCollapsed = ref(false)
const textareaRef = ref<HTMLTextAreaElement | null>(null)

const isValidInput = computed(
  () => query.value.trim().length > 0
)

const submitButtonText = computed(() => {
  if (!query.value.trim()) {
    return 'Type in a prompt...'
  }
  if (props.loading) {
    return 'Loading...'
  }
  if (props.disabled) {
    return 'Processing...'
  }
  return 'Submit Query'
})

const formatProcessType = (pt: string): string => {
  return pt
    .split('_')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ')
}

const onSubmit = () => {
  if (
    query.value.trim() &&
    !props.disabled &&
    !props.loading
  ) {
    emit('submit', {
      query: query.value,
      processOverride: selectedProcessType.value || undefined,
      modelSelection: selectedModelType.value || undefined,
    })
    query.value = ''
  }
}

const focus = () => {
  isCollapsed.value = false
  textareaRef.value?.focus()  
}

const clear = () => {
  query.value = ''
}

const resetProcessType = () => {
  selectedProcessType.value = ''
}

const resetModelType = () => {
  selectedModelType.value = ''
}

defineExpose({
  focus,
  clear,
  resetProcessType,
  resetModelType,
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
  align-items: stretch;
}

.model-select,
.process-select {
  padding: 0.75rem 1rem;
  font-size: 0.9rem;
  border: 1px solid var(--color-border);
  border-radius: var(--size-border-radius-sm);
  background-color: var(--color-bg-3);
  color: var(--color-text-primary);
  cursor: pointer;
  transition: border-color var(--transition-base);
  min-width: 160px;
}

.model-select:focus,
.process-select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.1);
}

.model-select:disabled,
.process-select:disabled {
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

button[type="submit"] {
  flex: 1;
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

button[type="submit"]:hover:not(:disabled) {
  background-color: var(--color-primary-dark);
}

button[type="submit"]:disabled {
  background-color: var(--color-border);
  cursor: not-allowed;
}
</style>
