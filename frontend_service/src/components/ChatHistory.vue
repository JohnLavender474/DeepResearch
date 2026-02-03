<template>
    <div class="chat-history">
        <div class="chat-history-header">
            <h3>Chat History</h3>
        </div>

        <div class="chat-list">
            <div v-if="props.conversations.length === 0 && props.loading" class="loading-indicator">
                <div class="spinner"></div>
                Loading conversations...
            </div>
            <div v-else-if="props.conversations.length === 0" class="no-conversations">
                No conversations available
            </div>
            <div v-else>
                <div
                    v-for="conversation in props.conversations"
                    :key="conversation.id"
                    class="conversation-item"
                    :class="{ active: conversation.id === props.selectedConversationId }"
                    @click="selectConversation(conversation.id)"
                >
                    <div class="conversation-title">{{ conversation.title || 'Untitled' }}</div>
                    <div class="conversation-date">{{ formatDate(conversation.updated_at) }}</div>
                </div>
            </div>
        </div>

        <button class="new-conversation-btn" @click="startNewConversation">
            + New Conversation
        </button>
    </div>
</template>

<script setup lang="ts">
import type Conversation from '@/model/conversation'
import '@/styles/shared.css'


interface ChatHistoryProps {
    profileId: string
    conversations: Conversation[]
    loading: boolean
    selectedConversationId: string
}

const props = defineProps<ChatHistoryProps>()

const emit = defineEmits<{
    (e: 'conversation-selected', conversationId: string): void
    (e: 'new-conversation'): void
}>()

const selectConversation = (conversationId: string) => {
    emit('conversation-selected', conversationId)
}

const startNewConversation = () => {
    emit('new-conversation')
}

const formatDate = (dateString: string): string => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
    })
}
</script>

<style scoped>
.chat-history {
    display: flex;
    flex-direction: column;
    height: 100%;
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
