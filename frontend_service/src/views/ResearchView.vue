<template>
  <div class="research-container">
    <header class="research-header">
      <h1>Deep Research</h1>
    </header>

    <div class="content-area">
      <aside class="sidebar">
        <div v-if="loading && !selectedProfileId" class="loader">
          <div class="spinner"></div>
        </div>
        <div v-else class="component-wrapper">
          <AddProfileButton
            :disabled="profilesLoading"
            @profile-created="onProfileCreated"
          />
          <ProfileSelector
            :profiles="profiles"
            :loading="profilesLoading"
            :disabled="profilesLoading"
            :model-value="selectedProfileId"
            @profile-changed="onProfileChanged"
          />
          <ChatHistory
            :profile-id="selectedProfileId"
            :loading="loading && !selectedProfileId"
            @conversation-selected="onConversationSelected"
            @new-conversation="onNewConversation"
          />
        </div>
      </aside>

      <main class="main-section">
        <ChatSection
          ref="chatSection"
          :conversation-id="selectedConversationId"
          :profile-id="selectedProfileId"
          @message-submitted="onMessageSubmitted"
        />
      </main>

      <aside class="sidebar-right">
        <div class="component-wrapper">
          <FileManagement
            :profile-id="selectedProfileId"
            @file-uploaded="onFileUploaded"
            @file-deleted="onFileDeleted"
          />
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'

import AddProfileButton from '@/components/AddProfileButton.vue'
import ChatHistory from '@/components/ChatHistory.vue'
import ChatSection from '@/components/ChatSection.vue'
import FileManagement from '@/components/FileManagement.vue'
import { fetchProfiles } from '@/services/profileService'
import ProfileSelector from '@/components/ProfileSelector.vue'
import type Profile from '@/model/profile'
import { useLocalStorage } from '@/composables/useLocalStorage'


const storage = useLocalStorage()

const loading = ref(false)

const profiles = ref<Profile[]>([])
const profilesLoading = ref(false)

const selectedProfileId = ref('')

const selectedConversationId = ref('')
const chatSection = ref()

const loadProfiles = async (preferredProfileId: string | null) => {
  profilesLoading.value = true

  profiles.value = await fetchProfiles()

  if (profiles.value.length > 0) {
    const storedProfileId = storage.getSelectedProfile()
    const preferredProfile = preferredProfileId
      ? profiles.value.find(
          (profile) => profile.id === preferredProfileId
        )
      : storedProfileId
        ? profiles.value.find(
            (profile) => profile.id === storedProfileId
          )
        : null

    if (preferredProfile) {
      selectedProfileId.value = preferredProfile.id
    } else {
      selectedProfileId.value = profiles.value[0].id
    }

    const storedConversationId = storage.getConversationForProfile(
      selectedProfileId.value
    )
    if (storedConversationId) {
      selectedConversationId.value = storedConversationId
    }
  } else {
    selectedProfileId.value = ''
  }

  profilesLoading.value = false
}

const onProfileChanged = (profileId: string) => {
  selectedProfileId.value = profileId
  storage.setSelectedProfile(profileId)

  const storedConversationId = storage.getConversationForProfile(profileId)
  if (storedConversationId) {
    selectedConversationId.value = storedConversationId
  } else {
    selectedConversationId.value = ''
    if (chatSection.value) {
      chatSection.value.clearMessages()
    }
  }
}

const onProfileCreated = async (profile: Profile) => {
  console.log(`Profile created: ${profile.id}`)
  await loadProfiles(profile.id)
  selectedConversationId.value = ''
  if (chatSection.value) {
    chatSection.value.clearMessages()
  }
}

const onConversationSelected = (conversationId: string) => {
  selectedConversationId.value = conversationId
  if (selectedProfileId.value) {
    storage.setConversationForProfile(
      selectedProfileId.value,
      conversationId
    )
  }
}

const onNewConversation = () => {
  selectedConversationId.value = ''
  if (selectedProfileId.value) {
    storage.clearConversationForProfile(selectedProfileId.value)
  }
  if (chatSection.value) {
    chatSection.value.clearMessages()
  }
}

const onFileUploaded = (filename: string) => {
  console.log(`File uploaded: ${filename}`)
}

const onFileDeleted = (filename: string) => {
  console.log(`File deleted: ${filename}`)
}

const onMessageSubmitted = async (query: string) => {
  console.log(`Message submitted: ${query}`)
  try {
    await new Promise((resolve) => setTimeout(resolve, 1000))
  } catch (err) {
    console.error('Error handling message submission:', err)
  }
}

onMounted(async () => {
  loading.value = true
  await loadProfiles(null)
  loading.value = false
})

watch(selectedProfileId, (newProfileId) => {
  if (newProfileId) {
    storage.setSelectedProfile(newProfileId)
  }
})
</script>

<style scoped>
.research-header {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  flex-shrink: 0;
  padding: 1rem 0;
}

h1 {
  color: #2c3e50;
  margin: 0;
}

.research-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 2rem);
  padding: 1rem;
}

.content-area {
  display: grid;
  grid-template-columns: 280px 1fr 300px;
  gap: 1.5rem;
  flex: 1;
  min-height: 0;
}

.sidebar {
  height: 90%;
  overflow: hidden;
}

.sidebar-right {
  height: 90%;
  overflow: hidden;
}

.component-wrapper {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.main-section {
  display: flex;
  flex-direction: column;
  height: 100%;
}

@media (max-width: 1200px) {
  .content-area {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr auto;
  }

  .sidebar {
    height: 200px;
  }
}
</style>
