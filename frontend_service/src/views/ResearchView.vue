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
          <ProfileSelector :profiles="profiles" :loading="profilesLoading" :disabled="profilesLoading"
            :model-value="selectedProfileId" @profile-changed="onProfileChanged" />
          <!--
          <ChatHistory :profile-id="selectedProfileId" :loading="loading && !selectedProfileId"
            @conversation-selected="onConversationSelected" @new-conversation="onNewConversation" />
          -->
        </div>
      </aside>

      <main class="main-section">
        <ChatSection ref="chatSection" :conversation-id="selectedConversationId" :profile-id="selectedProfileId"
          @message-submitted="onMessageSubmitted" />
      </main>

      <aside class="sidebar-right">
        <div class="component-wrapper">
          <FileManagement :profile-id="selectedProfileId" @file-uploaded="onFileUploaded"
            @file-deleted="onFileDeleted" />
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

// import ChatHistory from '@/components/ChatHistory.vue'
import ChatSection from '@/components/ChatSection.vue'
import FileManagement from '@/components/FileManagement.vue'
import { fetchProfiles, type Profile } from '@/services/profileService'
import ProfileSelector from '@/components/ProfileSelector.vue'


const loading = ref(false)
const profiles = ref<Profile[]>([])
const profilesLoading = ref(false)
const selectedProfileId = ref('')
const selectedConversationId = ref('')
const chatSection = ref()

const loadProfiles = async () => {
  profilesLoading.value = true
  profiles.value = await fetchProfiles()

  if (profiles.value.length > 0) {
    selectedProfileId.value = profiles.value[0].id
  }

  profilesLoading.value = false
}

const onProfileChanged = (profileId: string) => {
  selectedProfileId.value = profileId
  selectedConversationId.value = ''
  if (chatSection.value) {
    chatSection.value.clearMessages()
  }
}

/*
const onConversationSelected = (conversationId: string) => {
  selectedConversationId.value = conversationId
}

const onNewConversation = () => {
  selectedConversationId.value = ''
  if (chatSection.value) {
    chatSection.value.clearMessages()
  }
}
*/

const onFileUploaded = (filename: string) => {
  console.log(`File uploaded: ${filename}`)
}

const onFileDeleted = (filename: string) => {
  console.log(`File deleted: ${filename}`)
}

const onMessageSubmitted = async (query: string) => {
  if (chatSection.value) {
    chatSection.value.setProcessing(true)
  }

  try {
    await new Promise((resolve) => setTimeout(resolve, 1000))

    const mockAIResponse = {
      current_result: `Research findings for: "${query}"`,
      process_selection: {
        process_type: 'parallel_tasks',
      },
      steps: [
        { type: 'process_selection', details: {} },
        { type: 'parallel_tasks', details: {} },
      ],
      task_entries: [
        { id: '1', title: 'Task 1' },
        { id: '2', title: 'Task 2' },
      ],
      review: 'This is a sample review of the research findings.',
    }

    if (chatSection.value) {
      chatSection.value.addAIMessage(mockAIResponse)
      chatSection.value.setProcessing(false)
    }
  } catch (err) {
    if (chatSection.value) {
      chatSection.value.setError('Failed to process request')
      chatSection.value.setProcessing(false)
    }
  }
}

onMounted(async () => {
  loading.value = true
  await loadProfiles()
  loading.value = false
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
