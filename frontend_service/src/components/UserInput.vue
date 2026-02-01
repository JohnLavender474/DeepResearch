<template>
  <div class="user-input">
    <form @submit.prevent="onSubmit" class="input-form">
      <textarea
        v-model="query"
        placeholder="Enter your research query..."
        rows="4"
        :disabled="disabled"
        @keydown.meta.enter="onSubmit"
        @keydown.ctrl.enter="onSubmit"
      ></textarea>

      <button type="submit" :disabled="disabled">
        {{ disabled ? 'Processing...' : 'Submit' }}
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'


interface UserInputProps {
  disabled?: boolean
}

withDefaults(defineProps<UserInputProps>(), {
  disabled: false,
})

const emit = defineEmits<{
  (e: 'submit', query: string): void
}>()

const query = ref('')

const onSubmit = () => {
  if (query.value.trim()) {
    emit('submit', query.value)
    query.value = ''
  }
}
</script>

<style scoped>
.user-input {
  padding: 1.5rem;
  border-top: 1px solid #e2e8f0;
  background-color: #f8fafc;
  flex-shrink: 0;
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
  resize: vertical;
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
