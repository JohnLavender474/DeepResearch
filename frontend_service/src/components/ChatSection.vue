<template>
  <div class="chat-section">
    <div v-if="props.isLoadingConversation" class="loading-conversation">
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
      :disabled="props.isProcessing"
      :loading="props.isLoadingConversation"
      :process-types="props.processTypes"
      @submit="onSubmit"
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
import '@/styles/shared.css'


interface ChatSectionProps {
  messages: ChatMessageViewModel[]
  isProcessing: boolean
  isLoadingConversation: boolean
  error: string
  profileId: string
  processTypes: string[]
}

const props = defineProps<ChatSectionProps>()

const emit = defineEmits<{
  (e: 'submit', query: string, processOverride: string): void
  (e: 'conversation-created', conversationId: string): void
}>()

const userInputRef = ref<InstanceType<typeof UserInput> | null>(null)
const chatMessagesRef = ref<InstanceType<typeof ChatMessages> | null>(null)

watch(
  () => props.isLoadingConversation,
  (isLoading, wasLoading) => {
    if (wasLoading && !isLoading && props.messages.length > 0) {
      chatMessagesRef.value?.scrollToBottom()
    }
  }
)

const onSubmit = async (
  query: string,
  processOverride: string,
) => {
  emit('submit', query, processOverride)
}

const focusInput = () => {
  userInputRef.value?.focus()
}

const resetProcessSelection = () => {
  userInputRef.value?.resetProcessType()
}

defineExpose({
  focusInput,
  resetProcessSelection,
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
