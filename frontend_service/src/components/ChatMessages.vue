<template>
  <div class="chat-messages">
    <div v-if="messages.length === 0" class="empty-state">
      <p>No messages yet. Start by entering a query.</p>
    </div>

    <div v-else class="messages-list">
      <template v-for="message in messages" :key="message.id">
        <UserMessage
          v-if="message.role === 'user'"
          :content="message.content"
          :timestamp="message.timestamp"
        />

        <AIMessage
          v-else-if="message.role === 'ai'"
          :content="message.content"
          :timestamp="message.timestamp"
        />
      </template>

      <div v-if="loading" class="loading-indicator">
        <div class="spinner"></div>
        Processing your request...
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import UserMessage from './chat/UserMessage.vue'
import AIMessage from './chat/AIMessage.vue'
import '@/styles/shared.css'


interface Message {
  id: string
  role: 'user' | 'ai'
  content: any
  timestamp: Date
}

interface ChatMessagesProps {
  messages: Message[]
  loading?: boolean
}

withDefaults(defineProps<ChatMessagesProps>(), {
  loading: false,
})
</script>

<style scoped>
.chat-messages {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  padding: 1.5rem;
  min-height: 0;
  gap: 1rem;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #94a3b8;
  font-size: 0.95rem;
}

.empty-state p {
  margin: 0;
}

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.loading-indicator {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background-color: #f0fdf4;
  border-left: 3px solid #42b983;
  border-radius: 6px;
  color: #166534;
  font-size: 0.9rem;
}

.spinner {
  border: 2px solid #f3f3f3;
  border-top: 2px solid #42b983;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  animation: spin 1s linear infinite;
  flex-shrink: 0;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
