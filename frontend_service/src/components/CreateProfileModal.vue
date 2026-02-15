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
          placeholder="lowercase alphanumeric and underscores"
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

import { createProfile } from '@/services/profileService'
import type Profile from '@/model/profile'


const PROFILE_IDS_NOT_ALLOWED = [
  'conversations',
]


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

const profileIdPattern = /^[a-z0-9_]+$/

const validationError = computed(() => {
  if (!profileName.value) {
    return ''
  }

  if (!profileIdPattern.test(profileName.value)) {
    return 'Use lowercase letters, numbers, and underscores only.'
  }

  if (PROFILE_IDS_NOT_ALLOWED.includes(profileName.value)) {
    return 'This profile name is reserved.'
  }

  return ''
})

const isValid = computed(() => {
  return profileIdPattern.test(profileName.value) &&
    !PROFILE_IDS_NOT_ALLOWED.includes(profileName.value)
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
  background-color: var(--color-bg-2);
  border-radius: var(--size-border-radius-lg);
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
  color: var(--color-text-primary);
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.4rem;
  cursor: pointer;
  color: var(--color-text-secondary);
}

.modal-body {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.modal-body label {
  font-weight: 600;
  color: var(--color-text-primary);
}

.modal-body input {
  padding: 0.6rem 0.75rem;
  border-radius: var(--size-border-radius);
  border: 1px solid var(--color-border);
  font-size: 0.9rem;
  background-color: var(--color-bg-3);
  color: var(--color-text-primary);
  transition: border-color var(--transition-base);
}

.modal-body input:focus {
  outline: none;
  border-color: var(--color-primary);
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
  border-radius: var(--size-border-radius);
  font-size: 0.85rem;
  cursor: pointer;
  border: 1px solid transparent;
  transition: background-color var(--transition-base);
}

.primary-button {
  background-color: var(--color-primary);
  color: white;
}

.primary-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.secondary-button {
  background-color: var(--color-surface-hover);
  color: var(--color-text-primary);
  border-color: var(--color-border);
}

.secondary-button:hover {
  background-color: var(--color-surface-active);
}

.error-text {
  margin: 0;
  color: var(--color-error-text);
  font-size: 0.85rem;
}
</style>
