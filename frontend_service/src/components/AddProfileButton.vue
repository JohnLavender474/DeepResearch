<template>
  <div>
    <button
      class="add-profile-button"
      type="button"
      :disabled="props.disabled"
      @click="openModal"
    >
      Add Profile
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
  padding: 0.5rem 0.9rem;
  border-radius: 6px;
  border: 1px solid #42b983;
  background-color: #42b983;
  color: #ffffff;
  font-size: 0.85rem;
  cursor: pointer;
  width: 100%;
}

.add-profile-button:hover:not(:disabled) {
  background-color: #359268;
  border-color: #359268;
}

.add-profile-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
