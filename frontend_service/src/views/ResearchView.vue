<template>
  <div class="research-container">
    <aside class="sidebar">
      <ChatHistory
        :profile-id="selectedProfileId"
        @conversation-selected="onConversationSelected"
        @new-conversation="onNewConversation"
      />
    </aside>

    <main class="main-content">
      <header class="header">
        <h1>Deep Research</h1>
        <ProfileSelector @profile-changed="onProfileChanged" />
      </header>

      <div class="research-form">
        <textarea
          v-model="query"
          placeholder="Enter your research query..."
          rows="4"
        ></textarea>
        <button @click="submitResearch" :disabled="loading">
          {{ loading ? 'Processing...' : 'Submit Research' }}
        </button>
      </div>

      <div v-if="result" class="result">
        <h2>Result</h2>
        <pre>{{ result }}</pre>
      </div>

      <div v-if="error" class="error">
        <h2>Error</h2>
        <p>{{ error }}</p>
      </div>
    </main>

    <aside class="sidebar-right">
      <FileUpload
        :profile-id="selectedProfileId"
        @file-uploaded="onFileUploaded"
        @file-deleted="onFileDeleted"
      />
    </aside>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

import ProfileSelector from '@/components/ProfileSelector.vue'
import ChatHistory from '@/components/ChatHistory.vue'
import FileUpload from '@/components/FileUpload.vue'


const query = ref('')
const result = ref('')
const error = ref('')
const loading = ref(false)
const selectedProfileId = ref('')
const selectedConversationId = ref('')

const onProfileChanged = (profileId: string) => {
  selectedProfileId.value = profileId
  selectedConversationId.value = ''
  result.value = ''
}

const onConversationSelected = (conversationId: string) => {
  selectedConversationId.value = conversationId
}

const onNewConversation = () => {
  selectedConversationId.value = ''
  query.value = ''
  result.value = ''
}

const onFileUploaded = (filename: string) => {
  console.log(`File uploaded: ${filename}`)
}

const onFileDeleted = (filename: string) => {
  console.log(`File deleted: ${filename}`)
}

const submitResearch = async () => {
  if (!query.value.trim()) {
    error.value = 'Please enter a query'
    return
  }

  loading.value = true
  error.value = ''
  result.value = ''

  await new Promise((resolve) => setTimeout(resolve, 1000))
  result.value = `Simulated response for query: "${query.value}"`
  loading.value = false
}
</script>

<style scoped>
.research-container {
  display: grid;
  grid-template-columns: 280px 1fr 300px;
  gap: 1.5rem;
  height: calc(100vh - 2rem);
  padding: 1rem;
}

.sidebar {
  height: 100%;
  overflow: hidden;
}

.sidebar-right {
  height: fit-content;
}

.main-content {
  display: flex;
  flex-direction: column;
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

h1 {
  color: #2c3e50;
  margin: 0;
}

.research-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 2rem;
}

textarea {
  padding: 1rem;
  font-size: 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: inherit;
}

button {
  padding: 1rem 2rem;
  font-size: 1rem;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

button:hover:not(:disabled) {
  background-color: #38a071;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.result,
.error {
  margin-top: 2rem;
  padding: 1rem;
  border-radius: 4px;
}

.result {
  background-color: #f0f9ff;
  border: 1px solid #0ea5e9;
}

.error {
  background-color: #fef2f2;
  border: 1px solid #ef4444;
}

pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-size: 0.9rem;
}

@media (max-width: 1200px) {
  .research-container {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr auto;
  }

  .sidebar {
    height: 200px;
  }
}
</style>
