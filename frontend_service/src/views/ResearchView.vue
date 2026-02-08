<template>
  <div class="research-container">
    <div v-if="loading" class="full-loader">
      <div class="spinner"></div>
    </div>

    <template v-else-if="!selectedProfileId">
      <div class="no-profile-state">
        <div class="no-profile-content">
          <h2>No Profile Selected</h2>
          <p>
            Create a new profile to get started with
            research, chat, and document uploads.
          </p>
          <AddProfileButton
            :disabled="profilesLoading"
            @profile-created="onProfileCreated"
          />
          <ProfileSelector
            v-if="profiles.length > 0"
            :profiles="profiles"
            :loading="profilesLoading"
            :disabled="profilesLoading"
            :model-value="selectedProfileId"
            @profile-changed="onProfileChanged"
          />
        </div>
      </div>
    </template>

    <template v-else>
      <div class="mobile-controls">
        <button
          class="sidebar-toggle"
          @click="toggleLeftSidebar"
          :class="{ active: isLeftSidebarOpen }"
        >
          <span class="toggle-icon">☰</span>
          <span class="toggle-text">Chats</span>
        </button>
        <button
          class="sidebar-toggle"
          @click="toggleRightSidebar"
          :class="{ active: isRightSidebarOpen }"
        >
          <span class="toggle-text">Files</span>
          <span class="toggle-icon">📁</span>
        </button>
      </div>

      <div
        v-if="isLeftSidebarOpen || isRightSidebarOpen"
        class="sidebar-backdrop"
        @click="closeSidebars"
      ></div>

      <div class="content-area">
        <aside
          class="sidebar"
          :class="{ 'sidebar-open': isLeftSidebarOpen }"
        >
          <button
            class="sidebar-close"
            @click="closeLeftSidebar"
          >
            ✕
          </button>
          <div class="component-wrapper">
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
              :conversations="conversations"
              :loading="isLoadingConversations"
              :selected-conversation-id="currentConversationId"
              @conversation-selected="onConversationSelected"
              @new-conversation="onNewConversation"
            />
          </div>
        </aside>

        <main class="main-section">
          <ChatSection
            ref="chatSectionRef"
            :messages="messages"
            :chat-status="chatStatus"
            :error="error"
            :profile-id="selectedProfileId"
            :process-types="processTypes"
            :model-types="modelTypes"
            @submit="onMessageSubmitted"
            @conversation-created="onConversationCreated"
            @stop="onStopRequested"
          />
        </main>

        <aside
          class="sidebar-right"
          :class="{ 'sidebar-open': isRightSidebarOpen }"
        >
          <button
            class="sidebar-close"
            @click="closeRightSidebar"
          >
            ✕
          </button>
          <div class="component-wrapper">
            <FileManagement
              :profile-id="selectedProfileId"
              @file-uploaded="onFileUploaded"
              @file-deleted="onFileDeleted"
            />
          </div>
        </aside>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'

import AddProfileButton from '@/components/AddProfileButton.vue'
import ChatHistory from '@/components/ChatHistory.vue'
import ChatSection from '@/components/ChatSection.vue'
import FileManagement from '@/components/FileManagement.vue'
import { fetchProfiles } from '@/services/profileService'
import { fetchProcessTypes, fetchModels } from '@/services/graphService'
import ProfileSelector from '@/components/ProfileSelector.vue'
import type Profile from '@/model/profile'
import type UserQueryRequest from '@/model/userQueryRequest'
import { useLocalStorage } from '@/composables/useLocalStorage'
import { useChatSession } from '@/composables/useChatSession'


const storage = useLocalStorage()

const loading = ref(false)

const profiles = ref<Profile[]>([])
const profilesLoading = ref(false)

const selectedProfileId = ref('')

const processTypes = ref<string[]>([])
const modelTypes = ref<string[]>([])

const chatSectionRef = ref<InstanceType<typeof ChatSection> | null>(null)

const isLeftSidebarOpen = ref(false)
const isRightSidebarOpen = ref(false)

const toggleLeftSidebar = () => {
  isLeftSidebarOpen.value = !isLeftSidebarOpen.value
  if (isLeftSidebarOpen.value) {
    isRightSidebarOpen.value = false
  }
}

const toggleRightSidebar = () => {
  isRightSidebarOpen.value = !isRightSidebarOpen.value
  if (isRightSidebarOpen.value) {
    isLeftSidebarOpen.value = false
  }
}

const closeLeftSidebar = () => {
  isLeftSidebarOpen.value = false
}

const closeRightSidebar = () => {
  isRightSidebarOpen.value = false
}

const closeSidebars = () => {
  isLeftSidebarOpen.value = false
  isRightSidebarOpen.value = false
}

const {
  messages,
  conversations,
  chatStatus,
  isLoadingConversations,
  error,
  currentConversationId,
  loadConversations,
  loadConversation,
  submitMessage,
  stopCurrentInvocation,
  clearChatSession,
} = useChatSession()

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

    await loadConversations(selectedProfileId.value)
  } else {
    selectedProfileId.value = ''
  }

  profilesLoading.value = false
}

const onProfileChanged = async (profileId: string) => {
  selectedProfileId.value = profileId
  storage.setSelectedProfile(profileId)

  clearChatSession()

  await loadConversations(profileId)
}

const onProfileCreated = async (profile: Profile) => {
  await loadProfiles(profile.id)

  clearChatSession()
}

const onConversationSelected = (conversationId: string) => {
  if (selectedProfileId.value) {
    loadConversation(conversationId, selectedProfileId.value)

    storage.setConversationForProfile(
      selectedProfileId.value,
      conversationId
    )

    closeLeftSidebar()

    if (chatSectionRef.value) {
      chatSectionRef.value.resetProcessSelection()
      chatSectionRef.value.resetModelSelection()
    }
  }
}

const onConversationCreated = async (conversationId: string) => {
  if (selectedProfileId.value) {
    storage.setConversationForProfile(
      selectedProfileId.value,
      conversationId
    )
  }
}

const onNewConversation = () => {
  if (selectedProfileId.value) {
    storage.clearConversationForProfile(selectedProfileId.value)
  }

  clearChatSession()

  if (chatSectionRef.value) {
    chatSectionRef.value.focusInput()
    chatSectionRef.value.resetProcessSelection()
    chatSectionRef.value.resetModelSelection()
  }
}

const onFileUploaded = (filename: string) => {
  console.log(`File uploaded: ${filename}`)
}

const onFileDeleted = (filename: string) => {
  console.log(`File deleted: ${filename}`)
}

const onStopRequested = async () => {
  await stopCurrentInvocation()
}

const onMessageSubmitted = async (
  request: UserQueryRequest,
) => {
  if (!selectedProfileId.value) {
    console.error('No profile selected')    
    return
  }

  await submitMessage(
    request,
    selectedProfileId.value,
  )
}

onMounted(async () => {
  loading.value = true

  await loadProfiles(null)

  try {
    processTypes.value = await fetchProcessTypes()
  } catch (err) {
    console.error('Failed to fetch process types:', err)
  }

  try {
    modelTypes.value = await fetchModels()
  } catch (err) {
    console.error('Failed to fetch models:', err)
  }

  loading.value = false
})

watch(selectedProfileId, (newProfileId) => {
  if (newProfileId) {
    storage.setSelectedProfile(newProfileId)
  }
})

watch(currentConversationId, (newConversationId, oldConversationId) => {
  if (newConversationId && !oldConversationId && selectedProfileId.value) {
    onConversationCreated(newConversationId)
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

.research-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  padding: 1.5rem 1.5rem 0 1.5rem;
  background-color: var(--color-bg-1);
}

.full-loader {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
}

.no-profile-state {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
}

.no-profile-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;  
  width: 100%;
  text-align: center;
  padding: 2rem;
}

.no-profile-content h2 {
  margin: 0;
  font-size: 1.3rem;
  color: var(--color-text-primary);
}

.no-profile-content p {
  margin: 0;
  font-size: 0.95rem;
  color: var(--color-text-secondary);
  line-height: 1.5;
}

.mobile-controls {
  display: none;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-shrink: 0;
}

.sidebar-toggle {
  flex: 1;
  padding: 0.75rem 1rem;
  background-color: var(--color-bg-2);
  border: 1px solid var(--color-border);
  border-radius: var(--size-border-radius);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--color-text-primary);
  transition: all var(--transition-base);
}

.sidebar-toggle:hover {
  background-color: var(--color-surface-hover);
  border-color: var(--color-primary);
}

.sidebar-toggle.active {
  background-color: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.toggle-icon {
  font-size: 1.2rem;
}

.toggle-text {
  font-weight: 600;
}

.sidebar-backdrop {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 999;
}

.content-area {
  display: grid;
  grid-template-columns: 280px 1fr 300px;
  gap: 1.5rem;
  flex: 1;
  min-height: 0;
}

.sidebar,
.sidebar-right {
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  position: relative;
}

.sidebar-close {
  display: none;
  position: absolute;
  top: 1rem;
  right: 1rem;
  z-index: 1001;
  background: var(--color-bg-2);
  border: 1px solid var(--color-border);
  border-radius: 50%;
  width: 2rem;
  height: 2rem;
  cursor: pointer;
  font-size: 1.2rem;
  color: var(--color-text-primary);
  transition: all var(--transition-base);
}

.sidebar-close:hover {
  background: var(--color-surface-hover);
  border-color: var(--color-primary);
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
  min-height: 0;
  overflow: hidden;
}

@media (max-width: 1400px) {
  .mobile-controls {
    display: flex;
  }

  .sidebar-backdrop {
    display: block;
    opacity: 0;
    pointer-events: none;
    transition: opacity var(--transition-base);
  }

  .sidebar-backdrop:has(~ .content-area .sidebar-open) {
    opacity: 1;
    pointer-events: auto;
  }

  .content-area {
    grid-template-columns: 1fr;
    position: relative;
  }

  .sidebar,
  .sidebar-right {
    position: fixed;
    top: 0;
    bottom: 0;
    width: 320px;
    height: 100vh;
    z-index: 1000;
    background-color: var(--color-bg-1);
    border: 1px solid var(--color-border);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    transition: transform var(--transition-slow);
    padding: 1rem;
  }

  .sidebar {
    left: 0;
    transform: translateX(-100%);
  }

  .sidebar-right {
    right: 0;
    transform: translateX(100%);
  }

  .sidebar.sidebar-open {
    transform: translateX(0);
  }

  .sidebar-right.sidebar-open {
    transform: translateX(0);
  }

  .sidebar-close {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .component-wrapper {
    margin-top: 2.5rem;
  }
}
</style>
