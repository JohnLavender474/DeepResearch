<template>
  <div class="chat-section">
    <ChatMessages
      :messages="messages"
      :loading="isProcessing"
    />

    <UserInput
      :disabled="isProcessing"
      @submit="onSubmit"
    />

    <div v-if="error" class="error-banner">
      <p>{{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import ChatMessages from './ChatMessages.vue'
import UserInput from './UserInput.vue'
import { streamGraphExecution } from '@/services/graphService'


interface ChatMessage {
  id: string
  role: 'user' | 'ai'
  content: any
  timestamp: Date
}

interface ChatSectionProps {  
  profileId: string
}

const props = defineProps<ChatSectionProps>()

const emit = defineEmits<{
  (e: 'message-submitted', query: string): void
}>()

const messages = ref<ChatMessage[]>([])
const isProcessing = ref(false)
const error = ref('')

const onSubmit = async (query: string) => {
  if (!query.trim()) {
    error.value = 'Please enter a message'
    return
  }

  error.value = ''
  isProcessing.value = true

  const userMessage: ChatMessage = {
    id: `msg_${Date.now()}`,
    role: 'user',
    content: query,
    timestamp: new Date(),
  }

  messages.value.push(userMessage)
  emit('message-submitted', query)

  const aiMessageId = `msg_${Date.now()}_ai`
  const aiMessage: ChatMessage = {
    id: aiMessageId,
    role: 'ai',
    content: '',
    timestamp: new Date(),
  }
  messages.value.push(aiMessage)

  try {
    const stream = streamGraphExecution({
      user_query: query,
      profile_id: props.profileId,
    })

    for await (const chunk of stream) {
      const messageIndex = messages.value.findIndex(m => m.id === aiMessageId)
      if (messageIndex !== -1) {
        messages.value[messageIndex].content += chunk
      }
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'An error occurred'
  } finally {
    isProcessing.value = false
  }
}

const addAIMessage = (content: any) => {
  const aiMessage: ChatMessage = {
    id: `msg_${Date.now()}_ai`,
    role: 'ai',
    content: content,
    timestamp: new Date(),
  }

  messages.value.push(aiMessage)
}

const setProcessing = (processing: boolean) => {
  isProcessing.value = processing
}

const clearMessages = () => {
  messages.value = []
}

const setError = (errorMessage: string) => {
  error.value = errorMessage
}

defineExpose({
  addAIMessage,
  setProcessing,
  clearMessages,
  setError,
})
</script>

<style scoped>
.chat-section {
  display: flex;
  flex-direction: column;
  height: 90%;
  background-color: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
}

.error-banner {
  padding: 0.75rem 1rem;
  background-color: #fef2f2;
  border-top: 1px solid #fecaca;
  color: #dc2626;
  font-size: 0.9rem;
  flex-shrink: 0;
}

.error-banner p {
  margin: 0;
}
</style>
