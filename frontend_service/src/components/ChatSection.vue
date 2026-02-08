<template>
  <div class="chat-section">
    <div v-if="props.chatStatus === 'loading'" class="loading-conversation">
      <div class="spinner"></div>
      <span>Loading conversation...</span>
    </div>

    <ChatMessages
      v-else
      ref="chatMessagesRef"
      :messages="props.messages"
    />

    <UserInput
      ref="userInputRef"
      :chat-status="props.chatStatus"
      :process-types="props.processTypes"
      :model-types="props.modelTypes"
      @submit="onSubmit"
      @stop="onStop"
    />

    <div v-if="props.error" class="error-banner">
      <p>{{ props.error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

import ChatMessages from './ChatMessages.vue'
import UserInput from './UserInput.vue'
import type ChatMessageViewModel from '@/model/chatMessageViewModel'
import type UserQueryRequest from '@/model/userQueryRequest'
import type { ChatStatus } from '@/model/chatStatus'
import '@/styles/shared.css'


interface ChatSectionProps {
  messages: ChatMessageViewModel[]
  chatStatus: ChatStatus
  error: string
  profileId: string
  processTypes: string[]
  modelTypes: string[]
}

const props = defineProps<ChatSectionProps>()

const emit = defineEmits<{
  (e: 'submit', request: UserQueryRequest): void
  (e: 'conversation-created', conversationId: string): void
  (e: 'stop'): void
}>()

const userInputRef = ref<InstanceType<typeof UserInput> | null>(null)
const chatMessagesRef = ref<InstanceType<typeof ChatMessages> | null>(null)

watch(
  () => props.chatStatus,
  (newStatus, oldStatus) => {
    if (oldStatus === 'loading' && newStatus !== 'loading' && props.messages.length > 0) {
      chatMessagesRef.value?.scrollToBottom()
    }
  }
)

const onSubmit = async (
  request: UserQueryRequest,
) => {
  emit('submit', request)
}

const onStop = () => {
  emit('stop')
}

const focusInput = () => {
  userInputRef.value?.focus()
}

const resetProcessSelection = () => {
  userInputRef.value?.resetProcessType()
}

const resetModelSelection = () => {
  userInputRef.value?.resetModelType()
}

defineExpose({
  focusInput,
  resetProcessSelection,
  resetModelSelection,
})
</script>

<style scoped>
.chat-section {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;  
  background-color: var(--color-bg-2);
  border: 1px solid var(--color-border);
  border-radius: var(--size-border-radius);
  overflow: hidden;
}

.loading-conversation {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  color: var(--color-text-secondary);
  font-size: 0.95rem;
}

.error-banner {
  padding: 0.75rem 1rem;
  background-color: var(--color-error-bg);
  border-top: 1px solid var(--color-error-border);
  color: var(--color-error-text);
  font-size: 0.9rem;
  flex-shrink: 0;
}

.error-banner p {
  margin: 0;
}
</style>
