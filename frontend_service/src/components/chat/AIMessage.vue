<template>
  <div class="ai-message">
    <div class="message-header">
      <span class="ai-label">AI Response</span>
      <span class="message-timestamp">{{ formatTime(timestamp) }}</span>
    </div>

    <div class="message-content">
      {{ content }}
    </div>
  </div>
</template>

<script setup lang="ts">


interface AIMessageProps {
  content: any
  timestamp: Date
}

defineProps<AIMessageProps>()

const formatTime = (date: Date): string => {
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
  })
}
</script>

<style scoped>
.ai-message {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.5rem;
}

.message-header {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  font-size: 0.85rem;
}

.ai-label {
  font-weight: 600;
  color: #334155;
}

.message-timestamp {
  color: #94a3b8;
}

.message-content {
  max-width: 85%;
  padding: 0.75rem 1rem;
  background-color: #f1f5f9;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  word-wrap: break-word;
  white-space: pre-wrap;
  font-size: 0.95rem;
  line-height: 1.5;
}
</style>
