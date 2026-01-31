<template>
  <div class="chat-history">
    <div class="chat-history-header">
      <h3>Chat History</h3>
    </div>

    <div class="chat-list">
      <div
        v-for="conversation in conversations"
        :key="conversation.id"
        class="conversation-item"
        :class="{ active: conversation.id === selectedConversationId }"
        @click="selectConversation(conversation.id)"
      >
        <div class="conversation-title">{{ conversation.title }}</div>
        <div class="conversation-date">{{ formatDate(conversation.createdAt) }}</div>
      </div>

      <div v-if="conversations.length === 0" class="no-conversations">
        No conversations yet
      </div>
    </div>

    <button class="new-conversation-btn" @click="startNewConversation">
      + New Conversation
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'


interface Conversation {
  id: string
  title: string
  createdAt: Date
}

const props = defineProps<{
  profileId: string
}>()

const emit = defineEmits<{
  (e: 'conversation-selected', conversationId: string): void
  (e: 'new-conversation'): void
}>()

const conversations = ref<Conversation[]>([])
const selectedConversationId = ref<string>('')

const dummyConversationsByProfile: Record<string, Conversation[]> = {
  'profile-1': [
    {
      id: 'conv-1-1',
      title: 'Research on AI trends',
      createdAt: new Date('2026-01-30'),
    },
    {
      id: 'conv-1-2',
      title: 'Climate change analysis',
      createdAt: new Date('2026-01-29'),
    },
    {
      id: 'conv-1-3',
      title: 'Market research summary',
      createdAt: new Date('2026-01-28'),
    },
  ],
  'profile-2': [
    {
      id: 'conv-2-1',
      title: 'Q4 Financial Report Analysis',
      createdAt: new Date('2026-01-30'),
    },
    {
      id: 'conv-2-2',
      title: 'Competitor landscape review',
      createdAt: new Date('2026-01-27'),
    },
    {
      id: 'conv-2-3',
      title: 'Product roadmap planning',
      createdAt: new Date('2026-01-26'),
    },
    {
      id: 'conv-2-4',
      title: 'Customer feedback analysis',
      createdAt: new Date('2026-01-25'),
    },
    {
      id: 'conv-2-5',
      title: 'Marketing campaign strategy',
      createdAt: new Date('2026-01-24'),
    },
    {
      id: 'conv-2-6',
      title: 'Budget allocation review',
      createdAt: new Date('2026-01-23'),
    },
    {
      id: 'conv-2-7',
      title: 'Team performance metrics',
      createdAt: new Date('2026-01-22'),
    },
    {
      id: 'conv-2-8',
      title: 'Supply chain optimization',
      createdAt: new Date('2026-01-21'),
    },
    {
      id: 'conv-2-9',
      title: 'New vendor evaluation',
      createdAt: new Date('2026-01-20'),
    },
    {
      id: 'conv-2-10',
      title: 'Risk assessment report',
      createdAt: new Date('2026-01-19'),
    },
    {
      id: 'conv-2-11',
      title: 'Employee satisfaction survey',
      createdAt: new Date('2026-01-18'),
    },
    {
      id: 'conv-2-12',
      title: 'Technology stack review',
      createdAt: new Date('2026-01-17'),
    },
    {
      id: 'conv-2-13',
      title: 'Client retention strategies',
      createdAt: new Date('2026-01-16'),
    },
    {
      id: 'conv-2-14',
      title: 'Quarterly sales projections',
      createdAt: new Date('2026-01-15'),
    },
    {
      id: 'conv-2-15',
      title: 'Operational efficiency audit',
      createdAt: new Date('2026-01-14'),
    },
    {
      id: 'conv-2-16',
      title: 'Partnership opportunities',
      createdAt: new Date('2026-01-13'),
    },
    {
      id: 'conv-2-17',
      title: 'Compliance requirements update',
      createdAt: new Date('2026-01-12'),
    },
    {
      id: 'conv-2-18',
      title: 'Training program development',
      createdAt: new Date('2026-01-11'),
    },
    {
      id: 'conv-2-19',
      title: 'Cost reduction initiatives',
      createdAt: new Date('2026-01-10'),
    },
    {
      id: 'conv-2-20',
      title: 'Brand positioning research',
      createdAt: new Date('2026-01-09'),
    },
    {
      id: 'conv-2-21',
      title: 'Market expansion analysis',
      createdAt: new Date('2026-01-08'),
    },
    {
      id: 'conv-2-22',
      title: 'Customer segmentation study',
      createdAt: new Date('2026-01-07'),
    },
  ],
  'profile-3': [
    {
      id: 'conv-3-1',
      title: 'Travel destinations research',
      createdAt: new Date('2026-01-29'),
    },
  ],
}

const loadConversations = async (profileId: string) => {
  if (!profileId) {
    conversations.value = []
    return
  }

  await new Promise((resolve) => setTimeout(resolve, 300))
  conversations.value = dummyConversationsByProfile[profileId] || []
  selectedConversationId.value = ''
}

const selectConversation = (conversationId: string) => {
  selectedConversationId.value = conversationId
  emit('conversation-selected', conversationId)
}

const startNewConversation = () => {
  selectedConversationId.value = ''
  emit('new-conversation')
}

const formatDate = (date: Date): string => {
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  })
}

watch(
  () => props.profileId,
  (newProfileId) => {
    loadConversations(newProfileId)
  },
  { immediate: true }
)
</script>

<style scoped>
.chat-history {
  display: flex;
  flex-direction: column;
  height: 75%;
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
}

.chat-history-header {
  padding: 1rem;
  border-bottom: 1px solid #e2e8f0;
  background-color: white;
  flex-shrink: 0;
}

.chat-history-header h3 {
  margin: 0;
  font-size: 1rem;
  color: #1e293b;
}

.chat-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
  min-height: 0;
}

.conversation-item {
  padding: 0.75rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-bottom: 0.25rem;
}

.conversation-item:hover {
  background-color: #e2e8f0;
}

.conversation-item.active {
  background-color: #dbeafe;
  border-left: 3px solid #42b983;
}

.conversation-title {
  font-size: 0.9rem;
  color: #334155;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.conversation-date {
  font-size: 0.75rem;
  color: #94a3b8;
  margin-top: 0.25rem;
}

.no-conversations {
  padding: 2rem 1rem;
  text-align: center;
  color: #94a3b8;
  font-size: 0.9rem;
}

.new-conversation-btn {
  margin: 0.75rem;
  padding: 0.75rem;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background-color 0.2s;
  flex-shrink: 0;
}

.new-conversation-btn:hover {
  background-color: #38a071;
}
</style>
