<template>
  <div class="chat-section">
    <div v-if="isLoadingConversation" class="loading-conversation">
      <div class="spinner"></div>
      <span>Loading conversation...</span>
    </div>

    <ChatMessages
      v-else
      :messages="messages"
      :loading="isProcessing"
    />

    <UserInput
      ref="userInputRef"
      :disabled="isProcessing"
      :loading="isLoadingConversation"
      @submit="onSubmit"
    />

    <div v-if="error" class="error-banner">
      <p>{{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

import ChatMessages from './ChatMessages.vue'
import UserInput from './UserInput.vue'
// import { streamGraphExecution } from '@/services/graphService'
import {
  fetchConversation,
  createConversation,
  addChatTurnToConversation,
} from '@/services/conversationService'
import type ChatTurn from '@/model/chatTurn'
import '@/styles/shared.css'


interface ChatMessage {
  id: string
  role: 'user' | 'ai'
  content: any
  timestamp: Date
}

interface ChatSectionProps {
  conversationId: string
  profileId: string
}

const props = defineProps<ChatSectionProps>()

const emit = defineEmits<{
  (e: 'message-submitted', query: string): void
  (e: 'conversation-created', conversationId: string): void
}>()

const messages = ref<ChatMessage[]>([])
const isProcessing = ref(false)
const isLoadingConversation = ref(false)
const error = ref('')
const userInputRef = ref<InstanceType<typeof UserInput> | null>(null)
const currentConversationId = ref<string>('')

const loadConversation = async (conversationId: string) => {
  if (!conversationId) {
    messages.value = []
    currentConversationId.value = ''
    return
  }

  isLoadingConversation.value = true

  error.value = ''

  try {
    console.log('Loading conversation with ID:', conversationId)
    const conversation = await fetchConversation(conversationId)

    if (conversation) {
      currentConversationId.value = conversation.id
      messages.value = conversation.chat_turns.map((turn: ChatTurn) => ({
        id: turn.id,
        role: turn.role === 'human' ? 'user' : 'ai',
        content: turn.content,
        timestamp: new Date(turn.timestamp),
      }))
      console.log('Loaded messages:', messages.value)
    } else {
      messages.value = []
      currentConversationId.value = ''
      error.value = 'Conversation not found'
      console.warn('Conversation not found for ID:', conversationId)
    }
  } catch (err) {
    console.error('Failed to load conversation:', err)
    error.value = err instanceof Error ? err.message : 'Failed to load conversation'
    messages.value = []
    currentConversationId.value = ''
  } finally {
    isLoadingConversation.value = false
  }
}

const onSubmit = async (query: string) => {
  if (!query.trim()) {
    console.warn('Empty query submitted')
    error.value = 'Please enter a message'
    return
  }

  error.value = ''
  
  isProcessing.value = true

  let activeConversationId = currentConversationId.value

  if (!activeConversationId) {
    try {
      const newConversation = await createConversation(
        props.profileId,
        query
      )
      activeConversationId = newConversation.id
      currentConversationId.value = activeConversationId
      emit('conversation-created', activeConversationId)
      console.log('Created new conversation with ID:', activeConversationId)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create conversation'
      console.error('Failed to create conversation:', err)
      isProcessing.value = false      
      return
    }
  }

  const userMessageId = `msg_${Date.now()}`
  const userMessage: ChatMessage = {
    id: userMessageId,
    role: 'user',
    content: query,
    timestamp: new Date(),
  }

  messages.value.push(userMessage)
  emit('message-submitted', query)

  const userTurn: ChatTurn = {
    id: userMessageId,
    role: 'human',
    content: query,
    timestamp: new Date().toISOString(),
  }
  await addChatTurnToConversation(activeConversationId, userTurn)

  const aiMessageId = `msg_${Date.now()}_ai`
  const aiMessage: ChatMessage = {
    id: aiMessageId,
    role: 'ai',
    content: '',
    timestamp: new Date(),
  }
  messages.value.push(aiMessage)

  try {
    await new Promise((resolve) => setTimeout(resolve, 1000))

    const messageIndex = messages.value.findIndex((m) => m.id === aiMessageId)
    if (messageIndex !== -1) {
      messages.value[messageIndex].content = 'Hello World'
    }

    // const stream = streamGraphExecution({
    //   user_query: query,
    //   profile_id: props.profileId,
    // })

    // for await (const chunk of stream) {
    //   const messageIndex = messages.value.findIndex((m) => m.id === aiMessageId)
    //   if (messageIndex !== -1) {
    //     messages.value[messageIndex].content += chunk
    //   }
    // }

    const aiTurn: ChatTurn = {
      id: aiMessageId,
      role: 'ai',
      content: 'Hello World',
      timestamp: new Date().toISOString(),
    }
    await addChatTurnToConversation(activeConversationId, aiTurn)
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'An error occurred'
    console.error('An error occurred while processing AI response:', err)
  } finally {
    isProcessing.value = false
  }
}

const focusInput = () => {
  userInputRef.value?.focus()
}

const clearMessages = () => {
  messages.value = []
  currentConversationId.value = ''
}

const setError = (errorMessage: string) => {
  error.value = errorMessage
}

watch(
  () => props.conversationId,
  (newConversationId) => {
    if (newConversationId === currentConversationId.value) {
      return
    }
    loadConversation(newConversationId)
  },
  { immediate: true }
)

defineExpose({
  focusInput,
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

.loading-conversation {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  color: #64748b;
  font-size: 0.95rem;
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
