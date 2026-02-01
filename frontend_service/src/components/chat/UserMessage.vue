<template>
  <div class="user-message">
    <div class="message-content">
      {{ content }}
    </div>

    <div class="message-timestamp">
      {{ formatTime(timestamp) }}
    </div>
  </div>
</template>

<script setup lang="ts">
interface UserMessageProps {
  content: string
  timestamp: Date
}

defineProps<UserMessageProps>()

const formatTime = (date: Date): string => {
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
  })
}
</script>

<style scoped>
.user-message {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.5rem;
}

.message-content {
  max-width: 70%;
  padding: 0.75rem 1rem;
  background-color: #42b983;
  color: white;
  border-radius: 8px;
  word-wrap: break-word;
  white-space: pre-wrap;
  font-size: 0.95rem;
  line-height: 1.5;
}

.message-timestamp {
  font-size: 0.75rem;
  color: #94a3b8;
  padding-right: 0.5rem;
}
</style>
