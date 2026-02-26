<template>
  <div class="human-message">
    <div class="message-content">
      {{ content }}
    </div>

    <div class="message-timestamp">
      {{ formatTime(timestamp) }}
    </div>
  </div>
</template>

<script setup lang="ts">


interface HumanChatMessageProps {
  content: string
  timestamp: Date
}

defineProps<HumanChatMessageProps>()

const formatTime = (date: Date): string => {
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
  })
}
</script>

<style scoped>
.human-message {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.5rem;
}

.message-content {
  max-width: 70%;
  padding: 0.75rem 1rem;
  background-color: var(--color-bg-3);
  color: var(--color-text-primary);
  border-radius: var(--size-border-radius);
  word-wrap: break-word;
  white-space: pre-wrap;
  font-size: 0.95rem;
  line-height: 1.5;
}

.message-timestamp {
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
  padding-right: 0.5rem;
}
</style>
