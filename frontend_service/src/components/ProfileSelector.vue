<template>
  <div class="profile-selector">
    <label for="profile-select">Profile:</label>
    <select
      id="profile-select"
      v-model="selectedProfileId"
      @change="onProfileChange"
      :disabled="disabled"
    >
      <option value="" disabled>
        ▼ Select a profile
      </option>
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

import type Profile from '@/model/profile'


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
  background-color: var(--color-bg-2);
  border: 1px solid var(--color-border);
  border-radius: var(--size-border-radius);
}

label {
  font-weight: 600;
  color: var(--color-text-secondary);
  font-size: 0.9rem;
}

select {
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  border: 1px solid var(--color-border);
  border-radius: var(--size-border-radius-sm);
  background-color: var(--color-bg-3);
  color: var(--color-text-primary);
  cursor: pointer;
  min-width: 180px;
  transition: border-color var(--transition-base);
}

select:hover:not(:disabled) {
  border-color: var(--color-border-light);
}

select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(34, 197, 94, 0.2);
}

select:disabled {
  background-color: var(--color-surface-hover);
  cursor: not-allowed;
}

.loading-indicator {
  font-size: 0.8rem;
  color: var(--color-text-tertiary);
  font-style: italic;
}
</style>
