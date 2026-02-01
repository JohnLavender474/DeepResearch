<template>
    <div v-if="isOpen" class="modal-overlay" @click="closeModal">
        <div class="modal-content" @click.stop>
            <div class="modal-header">
                <h3>{{ document!.filename }}</h3>
                <button class="close-button" @click="closeModal" aria-label="Close modal">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                        fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                        stroke-linejoin="round">
                        <line x1="18" y1="6" x2="6" y2="18" />
                        <line x1="6" y1="6" x2="18" y2="18" />
                    </svg>
                </button>
            </div>

            <div class="modal-body">
                <p class="document-info">
                    Document: <span class="info-value">{{ document.filename }}</span>
                </p>
            </div>

            <div class="modal-actions">
                <button class="action-button download-file" @click="handleDownloadFile" :disabled="isLoading">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"
                        fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                        stroke-linejoin="round">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                        <polyline points="7 10 12 15 17 10" />
                        <line x1="12" y1="15" x2="12" y2="3" />
                    </svg>
                    Download File
                </button>

                <button class="action-button download-embeddings" @click="handleDownloadEmbeddings"
                    :disabled="isLoading">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"
                        fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                        stroke-linejoin="round">
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2m0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8m3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5zm-7 0c.83 0 1.5-.67 1.5-1.5S9.33 8 8.5 8 7 8.67 7 9.5 7.67 11 8.5 11zm3.5 6.5c2.33 0 4.31-1.46 5.11-3.5H6.89c.8 2.04 2.78 3.5 5.11 3.5z" />
                    </svg>
                    Download Embeddings
                </button>

                <button class="action-button delete-file" @click="handleDelete" :disabled="isLoading">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"
                        fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                        stroke-linejoin="round">
                        <polyline points="3 6 5 6 21 6" />
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                        <line x1="10" y1="11" x2="10" y2="17" />
                        <line x1="14" y1="11" x2="14" y2="17" />
                    </svg>
                    Delete
                </button>
            </div>

            <div v-if="errorMessage" class="error-message">
                {{ errorMessage }}
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type FileInfo from '@/model/fileInfo'
import {
    downloadFile,
    downloadEmbeddings,
    deleteFile,
} from '@/services/fileService'


interface DocumentModalProps {
    isOpen: boolean
    document: FileInfo | null
    profileId: string
}

const props = defineProps<DocumentModalProps>()

interface DocumentModalEmits {
    (e: 'close'): void
    (e: 'document-deleted'): void
}

const emit = defineEmits<DocumentModalEmits>()

const isLoading = ref(false)
const errorMessage = ref('')

const closeModal = () => {
    errorMessage.value = ''
    emit('close')
}

const handleDownloadFile = async () => {
    if (!props.document) return

    isLoading.value = true
    errorMessage.value = ''

    try {
        await downloadFile(props.profileId, props.document.filename)
    } catch (error) {
        errorMessage.value =
            error instanceof Error
                ? error.message
                : 'Failed to download file'
    } finally {
        isLoading.value = false
    }
}

const handleDownloadEmbeddings = async () => {
    if (!props.document) return

    isLoading.value = true
    errorMessage.value = ''

    try {
        await downloadEmbeddings(props.document.filename)
    } catch (error) {
        errorMessage.value =
            error instanceof Error
                ? error.message
                : 'Failed to download embeddings'
    } finally {
        isLoading.value = false
    }
}

const handleDelete = async () => {
    if (!props.document) return

    const confirm = window.confirm(
        `Are you sure you want to delete "${props.document.filename}"? This action cannot be undone.`
    )
    if (!confirm) return

    isLoading.value = true
    errorMessage.value = ''

    try {
        await deleteFile(props.profileId, props.document.filename)
        emit('document-deleted')
        closeModal()
    } catch (error) {
        errorMessage.value =
            error instanceof Error
                ? error.message
                : 'Failed to delete file'
    } finally {
        isLoading.value = false
    }
}
</script>

<style scoped>
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.modal-content {
    background-color: white;
    border-radius: 12px;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    max-width: 500px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
}

.modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.5rem;
    border-bottom: 1px solid #e2e8f0;
}

.modal-header h3 {
    margin: 0;
    font-size: 1.25rem;
    color: #1e293b;
    word-break: break-word;
}

.close-button {
    background: none;
    border: none;
    cursor: pointer;
    padding: 0.25rem;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #64748b;
    transition: color 0.2s;
    flex-shrink: 0;
    margin-left: 1rem;
}

.close-button:hover {
    color: #1e293b;
}

.modal-body {
    padding: 1.5rem;
}

.document-info {
    margin: 0;
    font-size: 0.9rem;
    color: #475569;
}

.info-value {
    font-weight: 600;
    color: #1e293b;
    word-break: break-word;
}

.modal-actions {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    padding: 1.5rem;
    border-top: 1px solid #e2e8f0;
}

.action-button {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 0.75rem 1rem;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    font-size: 0.95rem;
    cursor: pointer;
    transition: all 0.2s;
    font-weight: 500;
}

.action-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.download-file {
    color: #2563eb;
    border-color: #bfdbfe;
    background-color: #eff6ff;
}

.download-file:hover:not(:disabled) {
    background-color: #dbeafe;
    border-color: #93c5fd;
}

.download-embeddings {
    color: #8b5cf6;
    border-color: #ddd6fe;
    background-color: #f5f3ff;
}

.download-embeddings:hover:not(:disabled) {
    background-color: #ede9fe;
    border-color: #c4b5fd;
}

.delete-file {
    color: #dc2626;
    border-color: #fecaca;
    background-color: #fef2f2;
}

.delete-file:hover:not(:disabled) {
    background-color: #fee2e2;
    border-color: #fca5a5;
}

.error-message {
    padding: 0.75rem 1.5rem 1.5rem 1.5rem;
    background-color: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 6px;
    color: #dc2626;
    font-size: 0.9rem;
    margin: 0 1.5rem 1.5rem 1.5rem;
}
</style>
