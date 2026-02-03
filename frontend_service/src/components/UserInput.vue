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

      <button
        type="submit"
        :disabled="disabled || !isValidInput"
      >
        {{ submitButtonText }}
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'


interface UserInputProps {
  disabled?: boolean
  loading?: boolean
}

const props = withDefaults(defineProps<UserInputProps>(), {
  disabled: false,
  loading: false,
})

const emit = defineEmits<{
  (e: 'submit', query: string): void
}>()

const query = ref('')
const isCollapsed = ref(false)
const textareaRef = ref<HTMLTextAreaElement | null>(null)

const isValidInput = computed(() => query.value.trim().length > 0)

const submitButtonText = computed(() => {
  if (props.loading) {
    return 'Loading...'
  }
  if (props.disabled) {
    return 'Processing...'
  }
  return 'Submit Query'
})

const onSubmit = () => {
  if (
    query.value.trim() &&
    !props.disabled &&
    !props.loading
  ) {
    emit('submit', query.value)
    query.value = ''
  }
}

const focus = () => {
  textareaRef.value?.focus()
}

const clear = () => {
  query.value = ''
}

defineExpose({
  focus,
  clear,
})
</script>

<style scoped>
.user-input {
  padding: 0.5rem 1.5rem 1.5rem;
  border-top: 1px solid #e2e8f0;
  background-color: #f8fafc;
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
  color: #64748b;
  transition: color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toggle-button:hover {
  color: #42b983;
}

.toggle-button svg {
  transition: transform 0.3s ease;
}

.toggle-button svg.rotated {
  transform: rotate(180deg);
}

.input-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

textarea {
  padding: 1rem;
  font-size: 1rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-family: inherit;
  resize: none;
  transition: border-color 0.2s;
}

textarea:focus {
  outline: none;
  border-color: #42b983;
  box-shadow: 0 0 0 3px rgba(66, 185, 131, 0.1);
}

textarea:disabled {
  background-color: #f1f5f9;
  color: #94a3b8;
  cursor: not-allowed;
}

button {
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
  font-weight: 500;
}

button:hover:not(:disabled) {
  background-color: #38a071;
}

button:disabled {
  background-color: #cbd5e1;
  cursor: not-allowed;
}
</style>
