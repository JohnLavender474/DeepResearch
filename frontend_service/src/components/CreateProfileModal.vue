<template>
  <div v-if="isOpen" class="modal-backdrop">
    <div class="modal">
      <div class="modal-header">
        <h2>Create Profile</h2>
        <button
          class="modal-close"
          type="button"
          @click="handleClose"
        >
          ×
        </button>
      </div>
      <form class="modal-body" @submit.prevent="handleSubmit">
        <label for="new-profile-id">Profile name</label>
        <input
          id="new-profile-id"
          v-model="profileName"
          type="text"
          autocomplete="off"
          placeholder="lowercase alphanumeric"
        />
        <p v-if="validationError" class="error-text">
          {{ validationError }}
        </p>
        <p v-if="submitError" class="error-text">
          {{ submitError }}
        </p>
        <div class="modal-actions">
          <button
            class="secondary-button"
            type="button"
            @click="handleClose"
          >
            Cancel
          </button>
          <button
            class="primary-button"
            type="submit"
            :disabled="isSubmitting || !isValid"
          >
            Create
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import { createProfile, type Profile } from '@/services/profileService'


interface CreateProfileModalProps {
  isOpen: boolean
}

const props = defineProps<CreateProfileModalProps>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'profile-created', profile: Profile): void
}>()

const profileName = ref('')
const submitError = ref('')
const isSubmitting = ref(false)

const profileIdPattern = /^[a-z0-9]+$/

const validationError = computed(() => {
  if (!profileName.value) {
    return ''
  }

  if (!profileIdPattern.test(profileName.value)) {
    return 'Use lowercase letters and numbers only.'
  }

  return ''
})

const isValid = computed(() => {
  return profileIdPattern.test(profileName.value)
})

const handleClose = () => {
  resetForm()
  emit('close')
}

const resetForm = () => {
  profileName.value = ''
  submitError.value = ''
}

const handleSubmit = async () => {
  if (!isValid.value || isSubmitting.value) {
    return
  }

  isSubmitting.value = true
  submitError.value = ''

  try {
    const profile = await createProfile({
      id: profileName.value,
    })
    emit('profile-created', profile)
    resetForm()
  } catch (error) {
    const message =
      error instanceof Error
        ? error.message
        : 'Failed to create profile'
    submitError.value = message
  } finally {
    isSubmitting.value = false
  }
}

watch(
  () => props.isOpen,
  (newValue) => {
    if (!newValue) {
      resetForm()
    }
  }
)
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background-color: rgba(15, 23, 42, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
}

.modal {
  background-color: #ffffff;
  border-radius: 12px;
  width: min(420px, 90vw);
  box-shadow:
    0 20px 40px rgba(15, 23, 42, 0.2);
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.5rem;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.1rem;
  color: #0f172a;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.4rem;
  cursor: pointer;
  color: #475569;
}

.modal-body {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.modal-body label {
  font-weight: 600;
  color: #334155;
}

.modal-body input {
  padding: 0.6rem 0.75rem;
  border-radius: 8px;
  border: 1px solid #cbd5e1;
  font-size: 0.9rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.primary-button,
.secondary-button {
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-size: 0.85rem;
  cursor: pointer;
  border: 1px solid transparent;
}

.primary-button {
  background-color: #42b983;
  color: #ffffff;
}

.primary-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.secondary-button {
  background-color: #f1f5f9;
  color: #334155;
  border-color: #cbd5e1;
}

.error-text {
  margin: 0;
  color: #dc2626;
  font-size: 0.85rem;
}
</style>
