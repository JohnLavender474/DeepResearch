<template>
  <div>
    <button
      class="add-profile-button"
      type="button"
      :disabled="props.disabled"
      @click="openModal"
    >
      + Add Profile
    </button>

    <CreateProfileModal
      :is-open="isModalOpen"
      @close="closeModal"
      @profile-created="onProfileCreated"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

import CreateProfileModal from '@/components/CreateProfileModal.vue'
import type Profile from '@/model/profile'


interface AddProfileButtonProps {
  disabled: boolean
}

const props = defineProps<AddProfileButtonProps>()

const emit = defineEmits<{
  (e: 'profile-created', profile: Profile): void
}>()

const isModalOpen = ref(false)

const openModal = () => {
  isModalOpen.value = true
}

const closeModal = () => {
  isModalOpen.value = false
}

const onProfileCreated = (profile: Profile) => {
  emit('profile-created', profile)
  closeModal()
}
</script>

<style scoped>
.add-profile-button {
  display: block;
  margin: 0 auto;
  padding: 0.5rem 0.9rem;
  border-radius: var(--size-border-radius);
  border: 1px solid var(--color-primary);
  background-color: var(--color-primary);
  color: var(--color-text-primary);
  font-size: 0.85rem;
  cursor: pointer;
  font-weight: 500;  
  transition: all var(--transition-base);
}

.add-profile-button:hover:not(:disabled) {
  background-color: var(--color-primary-dark);
  border-color: var(--color-primary-dark);
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.2);
}

.add-profile-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
