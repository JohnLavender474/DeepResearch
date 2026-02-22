<template>
  <div class="chat-messages">
    <div v-if="props.messages.length === 0" class="empty-state">
      <p>No messages yet. Start by entering a query.</p>
    </div>

    <div v-else class="messages-list">
      <template v-for="message in props.messages" :key="message.id">
        <HumanChatMessage
          v-if="message.role === 'user'"
          :content="message.content"
          :timestamp="message.timestamp"
        />

        <AIChatMessage
          v-else-if="message.role === 'ai'"
          :content="message.content"
          :timestamp="message.timestamp"
        />
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">

import HumanChatMessage from './chat/HumanChatMessage.vue'
import AIChatMessage from './chat/AIChatMessage.vue'
import '@/styles/shared.css'


interface Message {
  id: string
  role: 'user' | 'ai'
  content: any
  timestamp: Date
}

interface ChatMessagesProps {
  messages: Message[]
}

const props = defineProps<ChatMessagesProps>()
</script>

<style scoped>
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  min-height: 0;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--color-text-tertiary);
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
</style>
