<template>
  <div class="profile-selector">
    <label for="profile-select">Profile:</label>
    <select
      id="profile-select"
      v-model="selectedProfileId"
      @change="onProfileChange"
      :disabled="disabled"
    >
      <option
        v-for="profile in profiles"
        :key="profile.id"
        :value="profile.id"
      >
        {{ profile.id }}
      </option>
    </select>
    <span v-if="loading" class="loading-indicator">Loading...</span>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

import type { Profile } from '@/services/profileService'


interface ProfileSelectorProps {
  profiles: Profile[]
  disabled: boolean
  loading: boolean
  modelValue: string
}

const props = defineProps<ProfileSelectorProps>()

const emit = defineEmits<{
  (e: 'profile-changed', profileId: string): void
  (e: 'update:modelValue', profileId: string): void
}>()

const selectedProfileId = ref<string>('')

const onProfileChange = () => {
  emit('profile-changed', selectedProfileId.value)
  emit('update:modelValue', selectedProfileId.value)
}

watch(
  () => props.modelValue,
  (newValue) => {
    selectedProfileId.value = newValue
  },
  { immediate: true }
)
</script>

<style scoped>
.profile-selector {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
}

label {
  font-weight: 600;
  color: #475569;
  font-size: 0.9rem;
}

select {
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  background-color: white;
  cursor: pointer;
  min-width: 180px;
}

select:hover:not(:disabled) {
  border-color: #94a3b8;
}

select:focus {
  outline: none;
  border-color: #42b983;
  box-shadow: 0 0 0 2px rgba(66, 185, 131, 0.2);
}

select:disabled {
  background-color: #f1f5f9;
  cursor: not-allowed;
}

.loading-indicator {
  font-size: 0.8rem;
  color: #64748b;
  font-style: italic;
}
</style>
