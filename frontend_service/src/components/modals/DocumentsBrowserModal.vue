<template>
    <div v-if="isOpen" class="modal-overlay" @click="closeModal">
        <div class="modal-content" @click.stop>
            <div class="modal-header">
                <h3>Documents</h3>
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
                <div class="search-container">
                    <input
                        v-model="searchQuery"
                        type="text"
                        class="search-input"
                        placeholder="Search documents by name"
                    />
                    <p class="documents-hint">
                        Showing {{ filteredAndSortedDocuments.length }} of {{ props.documents.length }} documents
                    </p>
                </div>

                <div class="table-container">
                    <table class="documents-table">
                        <colgroup>
                            <col class="filename-col">
                            <col class="uploaded-at-col">
                            <col class="actions-col">
                        </colgroup>
                        <thead>
                            <tr>
                                <th>
                                    <button
                                        class="sort-button"
                                        @click="toggleSort('filename')"
                                        type="button"
                                    >
                                        File Name
                                        <span class="sort-indicator">
                                            {{ getSortIndicator('filename') }}
                                        </span>
                                    </button>
                                </th>
                                <th>
                                    <button
                                        class="sort-button"
                                        @click="toggleSort('uploadedAt')"
                                        type="button"
                                    >
                                        Uploaded At
                                        <span class="sort-indicator">
                                            {{ getSortIndicator('uploadedAt') }}
                                        </span>
                                    </button>
                                </th>
                                <th class="actions-header">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr
                                v-for="document in paginatedDocuments"
                                :key="document.filename"
                            >
                                <td class="filename-cell">{{ document.filename }}</td>
                                <td class="uploaded-at-cell">{{ formatUploadedAt(document.uploadedAt) }}</td>
                                <td class="actions-cell">
                                    <button
                                        class="action-button"
                                        type="button"
                                        title="Download document"
                                        aria-label="Download document"
                                        :disabled="isActionLoading(document.filename)"
                                        @click="handleDownloadFile(document)"
                                    >
                                        <Download :size="14" />
                                    </button>
                                    <button
                                        class="action-button"
                                        type="button"
                                        title="Download embeddings"
                                        aria-label="Download embeddings"
                                        :disabled="isActionLoading(document.filename)"
                                        @click="handleDownloadEmbeddings(document)"
                                    >
                                        <FileJson :size="14" />
                                    </button>
                                    <button
                                        class="action-button delete"
                                        type="button"
                                        title="Delete document"
                                        aria-label="Delete document"
                                        :disabled="isActionLoading(document.filename)"
                                        @click="handleDeleteFile(document)"
                                    >
                                        <Trash2 :size="14" />
                                    </button>
                                </td>
                            </tr>
                            <tr v-if="filteredAndSortedDocuments.length === 0">
                                <td colspan="3" class="empty-state">
                                    No documents found
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <div class="pagination-container">
                    <button
                        class="pagination-button"
                        type="button"
                        :disabled="!canGoPrevious"
                        @click="goToPreviousPage"
                    >
                        Previous
                    </button>
                    <span class="pagination-info">
                        Page {{ currentPage }} of {{ totalPages }}
                    </span>
                    <button
                        class="pagination-button"
                        type="button"
                        :disabled="!canGoNext"
                        @click="goToNextPage"
                    >
                        Next
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import {
    Download,
    FileJson,
    Trash2,
} from 'lucide-vue-next'
import type FileInfo from '@/model/fileInfo'
import {
    deleteFile,
    downloadEmbeddings,
    downloadFile,
} from '@/services/fileService'

interface DocumentsBrowserModalProps {
    isOpen: boolean
    documents: FileInfo[]
    profileId: string
}

const props = defineProps<DocumentsBrowserModalProps>()

interface DocumentsBrowserModalEmits {
    (e: 'close'): void
    (e: 'document-deleted'): void
}

const emit = defineEmits<DocumentsBrowserModalEmits>()

const searchQuery = ref('')
const sortBy = ref<'filename' | 'uploadedAt'>('uploadedAt')
const sortDirection = ref<'asc' | 'desc'>('desc')
const loadingByFilename = ref<Record<string, boolean>>({})
const currentPage = ref(1)
const pageSize = 25

const closeModal = () => {
    emit('close')
}

const setActionLoading = (filename: string, loading: boolean) => {
    loadingByFilename.value = {
        ...loadingByFilename.value,
        [filename]: loading,
    }
}

const isActionLoading = (filename: string) => {
    return loadingByFilename.value[filename] === true
}

const handleDownloadFile = async (document: FileInfo) => {
    setActionLoading(document.filename, true)

    try {
        await downloadFile(props.profileId, document.filename)
    } finally {
        setActionLoading(document.filename, false)
    }
}

const handleDownloadEmbeddings = async (document: FileInfo) => {
    setActionLoading(document.filename, true)

    try {
        await downloadEmbeddings(document.filename)
    } finally {
        setActionLoading(document.filename, false)
    }
}

const handleDeleteFile = async (document: FileInfo) => {
    const confirmed = window.confirm(
        `Are you sure you want to delete "${document.filename}"? This action cannot be undone.`
    )

    if (!confirmed) {
        return
    }

    setActionLoading(document.filename, true)

    try {
        await deleteFile(props.profileId, document.filename)
        emit('document-deleted')
    } finally {
        setActionLoading(document.filename, false)
    }
}

const filteredAndSortedDocuments = computed(() => {
    const query = searchQuery.value.trim().toLowerCase()

    const filtered = query
        ? props.documents.filter((document) =>
            document.filename.toLowerCase().includes(query)
        )
        : props.documents

    return [...filtered].sort((a, b) => {
        if (sortBy.value === 'filename') {
            const nameA = a.filename.toLowerCase()
            const nameB = b.filename.toLowerCase()
            if (nameA < nameB) return sortDirection.value === 'asc' ? -1 : 1
            if (nameA > nameB) return sortDirection.value === 'asc' ? 1 : -1
            return 0
        }

        const timeA = new Date(a.uploadedAt).getTime()
        const timeB = new Date(b.uploadedAt).getTime()
        if (timeA < timeB) return sortDirection.value === 'asc' ? -1 : 1
        if (timeA > timeB) return sortDirection.value === 'asc' ? 1 : -1
        return 0
    })
})

const totalPages = computed(() => {
    return Math.max(1, Math.ceil(filteredAndSortedDocuments.value.length / pageSize))
})

const paginatedDocuments = computed(() => {
    const startIndex = (currentPage.value - 1) * pageSize
    return filteredAndSortedDocuments.value.slice(startIndex, startIndex + pageSize)
})

const canGoPrevious = computed(() => currentPage.value > 1)
const canGoNext = computed(() => currentPage.value < totalPages.value)

const goToPreviousPage = () => {
    if (canGoPrevious.value) {
        currentPage.value -= 1
    }
}

const goToNextPage = () => {
    if (canGoNext.value) {
        currentPage.value += 1
    }
}

const toggleSort = (field: 'filename' | 'uploadedAt') => {
    if (sortBy.value === field) {
        sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
        return
    }

    sortBy.value = field
    sortDirection.value = 'asc'
}

const getSortIndicator = (field: 'filename' | 'uploadedAt') => {
    if (sortBy.value !== field) {
        return '↕'
    }

    return sortDirection.value === 'asc' ? '↑' : '↓'
}

const formatUploadedAt = (value: string) => {
    const parsed = new Date(value)
    if (Number.isNaN(parsed.getTime())) {
        return value
    }

    return parsed.toLocaleString()
}

watch(searchQuery, () => {
    currentPage.value = 1
})

watch(totalPages, (newTotalPages) => {
    if (currentPage.value > newTotalPages) {
        currentPage.value = newTotalPages
    }
})
</script>

<style scoped>
.modal-overlay {
    position: fixed;
    inset: 0;
    background-color: rgba(15, 23, 42, 0.6);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.modal-content {
    background-color: var(--color-bg-2);
    border-radius: var(--size-border-radius-lg);
    border: 1px solid var(--color-border);
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
    width: min(1000px, 95vw);
    height: min(85vh, 760px);
    display: flex;
    flex-direction: column;
}

.modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 1.25rem;
    border-bottom: 1px solid var(--color-border);
}

.modal-header h3 {
    margin: 0;
    color: var(--color-text-primary);
    font-size: 1.05rem;
}

.close-button {
    background: none;
    border: none;
    cursor: pointer;
    color: var(--color-text-secondary);
    display: flex;
    align-items: center;
    justify-content: center;
}

.close-button:hover {
    color: var(--color-text-primary);
}

.modal-body {
    padding: 1rem 1.25rem 1.25rem;
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    overflow: hidden;
}

.search-input {
    width: 100%;
    padding: 0.6rem 0.75rem;
    background: var(--color-surface-hover);
    border: 1px solid var(--color-border);
    border-radius: var(--size-border-radius-sm);
    color: var(--color-text-primary);
    font-size: 0.9rem;
    outline: none;
}

.search-input::placeholder {
    color: var(--color-text-tertiary);
}

.search-input:focus {
    border-color: var(--color-primary);
}

.documents-hint {
    margin: 0.45rem 0 0;
    color: var(--color-text-tertiary);
    font-size: 0.8rem;
}

.table-container {
    flex: 1;
    min-height: 0;
    border: 1px solid var(--color-border);
    border-radius: var(--size-border-radius-sm);
    overflow-x: hidden;
    overflow-y: auto;
    padding-right: 0.4rem;
}

.documents-table {
    width: 100%;
    border-collapse: collapse;
    table-layout: fixed;
}

.filename-col {
    width: auto;
}

.uploaded-at-col {
    width: 190px;
}

.actions-col {
    width: 120px;
}

.documents-table thead th {
    text-align: left;
    padding: 0.7rem 0.75rem;
    color: var(--color-text-secondary);
    font-size: 0.8rem;
    border-bottom: 1px solid var(--color-border);
    background: var(--color-surface-hover);
}

.documents-table tbody td {
    padding: 0.7rem 0.75rem;
    color: var(--color-text-primary);
    border-bottom: 1px solid var(--color-border);
    font-size: 0.87rem;
}

.documents-table tbody tr:last-child td {
    border-bottom: none;
}

.sort-button {
    background: none;
    border: none;
    color: inherit;
    font: inherit;
    cursor: pointer;
    padding: 0;
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
}

.sort-indicator {
    color: var(--color-text-tertiary);
}

.filename-cell {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.uploaded-at-cell {
    white-space: nowrap;
}

.actions-header {
    white-space: nowrap;
}

.actions-cell {
    white-space: nowrap;
    padding-right: 0.35rem;
}

.action-button {
    background: var(--color-surface-hover);
    border: 1px solid var(--color-border);
    border-radius: var(--size-border-radius-sm);
    color: var(--color-text-secondary);
    width: 1.85rem;
    height: 1.85rem;
    padding: 0;
    cursor: pointer;
    margin-right: 0.35rem;
    display: inline-flex;
    align-items: center;
    justify-content: center;
}

.action-button:last-child {
    margin-right: 0;
}

.action-button:hover:not(:disabled) {
    border-color: var(--color-primary);
    color: var(--color-primary);
}

.action-button.delete:hover:not(:disabled) {
    border-color: var(--color-error-border);
    color: var(--color-error-text);
}

.action-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.pagination-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
    margin-top: 0.75rem;
    padding-top: 0.75rem;
    border-top: 1px solid var(--color-border);
    flex-shrink: 0;
}

.pagination-button {
    background: var(--color-surface-hover);
    border: 1px solid var(--color-border);
    border-radius: var(--size-border-radius-sm);
    padding: 0.4rem 0.7rem;
    color: var(--color-text-secondary);
    cursor: pointer;
    font-size: 0.85rem;
    transition: all var(--transition-base);
}

.pagination-button:hover:not(:disabled) {
    background: var(--color-surface-active);
    border-color: var(--color-primary);
    color: var(--color-primary);
}

.pagination-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.pagination-info {
    color: var(--color-text-tertiary);
    font-size: 0.85rem;
}

.empty-state {
    text-align: center;
    color: var(--color-text-tertiary);
    padding: 1.25rem;
}
</style>
