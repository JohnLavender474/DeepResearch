<template>
  <div class="profile-selector">
    <label for="profile-select">Profile:</label>
    <select
      id="profile-select"
      v-model="selectedProfileId"
      @change="onProfileChange"
      :disabled="loading"
    >
      <option
        v-for="profile in profiles"
        :key="profile.id"
        :value="profile.id"
      >
        {{ profile.name }}
      </option>
    </select>
    <span v-if="loading" class="loading-indicator">Loading...</span>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'


interface Profile {
  id: string
  name: string
}

const emit = defineEmits<{
  (e: 'profile-changed', profileId: string): void
}>()

const profiles = ref<Profile[]>([])
const selectedProfileId = ref<string>('')
const loading = ref(false)

const fetchProfiles = async () => {
  loading.value = true

  await new Promise((resolve) => setTimeout(resolve, 500))
  profiles.value = [
    { id: 'profile-1', name: 'Default Profile' },
    { id: 'profile-2', name: 'Work Profile' },
    { id: 'profile-3', name: 'Personal Profile' },
  ]

  if (profiles.value.length > 0) {
    selectedProfileId.value = profiles.value[0].id
    emit('profile-changed', selectedProfileId.value)
  }

  loading.value = false
}

const onProfileChange = () => {
  emit('profile-changed', selectedProfileId.value)
}

onMounted(() => {
  fetchProfiles()
})
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
