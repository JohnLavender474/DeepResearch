<template>
    <div class="file-upload">
        <UploadFile
            @file-selected="handleFile"
        />

        <div v-if="errorMessage" class="error-message">
            {{ errorMessage }}
        </div>

        <div class="uploaded-files">
            <div class="uploaded-files-header">
                <h4>Uploaded Documents</h4>
                <button
                    class="refresh-button"
                    @click="loadUploadedFiles(props.profileId)"
                    title="Refresh documents list"
                    :disabled="loadingDocuments"
                >
                    <RefreshCw
                        :size="18"
                        :class="{ 'spinning': loadingDocuments }"
                    />
                </button>
            </div>
            <div v-if="loadingDocuments && uploadedFiles.length === 0" class="loading-container">
                <div class="spinner"></div>
                <span>Loading documents...</span>
            </div>
            <ul v-else>
                <li
                    v-for="file in uploadedFiles"
                    :key="file.filename"
                    @click="openDocumentModal(file)"
                    class="document-row"
                >
                    <span class="file-name">{{ file.filename }}</span>
                </li>
                <li v-if="uploadedFiles.length === 0" class="no-documents">
                    No documents uploaded yet
                </li>
                <li v-if="loadingDocuments && uploadedFiles.length > 0" class="loading-more">
                    <div class="spinner-small"></div>
                    <span>Loading more documents...</span>
                </li>
            </ul>
        </div>

        <DocumentModal
            :is-open="isDocModalOpen"
            :document="selectedDocument"
            :profile-id="profileId"
            @close="closeDocumentModal"
            @document-deleted="handleDocumentDeleted"
        />

        <FileSplitModal
            :is-open="isSplitModalOpen"
            :file="oversizedFile"
            @cancel="closeSplitModal"
            @split="handleSplitConfirmed"
        />
    </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { RefreshCw } from 'lucide-vue-next'
import { uploadFile, fetchFilesForProfile } from '@/services/fileService'
import {
    fileSizeExceedsMax,
    formatFileSize,
    splitPdf,
} from '@/services/pdfSplitService'
import DocumentModal from './modals/DocumentModal.vue'
import FileSplitModal from './modals/FileSplitModal.vue'
import UploadFile from './UploadFile.vue'
import '@/styles/shared.css'
import type FileInfo from '@/model/fileInfo'
import { useToasts } from '@/composables/useToasts'


interface FileManagementProps {
    profileId: string
}

const props = defineProps<FileManagementProps>()

const emit = defineEmits<{
    (e: 'file-uploaded', filename: string): void
}>()

const uploadedFiles = ref<FileInfo[]>([])
const loadingDocuments = ref(false)

const errorMessage = ref('')

const isDocModalOpen = ref(false)
const selectedDocument = ref<FileInfo | null>(null)

const isSplitModalOpen = ref(false)
const oversizedFile = ref<File | null>(null)

const { addToast } = useToasts()

const loadUploadedFiles = async (profileId: string) => {
    if (!profileId) {
        uploadedFiles.value = []
        loadingDocuments.value = false
        return
    }

    loadingDocuments.value = true
    errorMessage.value = ''
    uploadedFiles.value = []

    try {
        await fetchFilesForProfile(profileId, (batchFiles: FileInfo[]) => {
            uploadedFiles.value = [...uploadedFiles.value, ...batchFiles]
        })
    } catch (error) {
        console.error('Failed to load documents:', error)
        uploadedFiles.value = []
        errorMessage.value = 'Failed to load documents. Please try again.'
    } finally {
        loadingDocuments.value = false
    }
}

const handleFile = async (file: File) => {
    errorMessage.value = ''

    if (!file.name.toLowerCase().endsWith('.pdf')) {
        errorMessage.value = 'Only PDF files are allowed'
        return
    }

    const existingFile = uploadedFiles.value.find(
        (f) => f.filename === file.name
    )
    if (existingFile) {
        errorMessage.value = 'A file with this name already exists'
        return
    }

    if (fileSizeExceedsMax(file)) {
        oversizedFile.value = file
        isSplitModalOpen.value = true
        return
    }

    await uploadSingleFile(file)
}

const uploadSingleFile = async (file: File) => {
    addToast(
        `File ${file.name} is processing`,
        'info',
    )

    uploadFile(props.profileId, file)
        .then(() => {
            console.log(`File ${file.name} uploaded successfully`)

            emit('file-uploaded', file.name)
            loadUploadedFiles(props.profileId)

            addToast(
                `File ${file.name} successfully uploaded`,
                'success',
            )
        })
        .catch((error) => {
            errorMessage.value =
                error instanceof Error
                    ? error.message
                    : 'Failed to upload document'

            addToast(
                `File ${file.name} failed to upload`,
                'error',
            )
        })
}

const closeSplitModal = () => {
    isSplitModalOpen.value = false
    oversizedFile.value = null
}

const handleSplitConfirmed = async (pagesPerPart: number) => {
    const file = oversizedFile.value
    if (!file) {
        return
    }

    isSplitModalOpen.value = false

    addToast(
        `Splitting ${file.name} into parts...`,
        'info',
    )

    try {
        const parts = await splitPdf(file, pagesPerPart)

        addToast(
            `Split into ${parts.length} parts. Uploading...`,
            'info',
        )

        for (const part of parts) {
            const existingFile = uploadedFiles.value.find(
                (f) => f.filename === part.file.name
            )
            if (existingFile) {
                addToast(
                    `Skipping ${part.file.name} (already exists)`,
                    'info',
                )
                continue
            }

            if (fileSizeExceedsMax(part.file)) {
                addToast(
                    `Part ${part.file.name} still exceeds size limit `
                    + `(${formatFileSize(part.file.size)}). `
                    + 'Try fewer pages per part.',
                    'error',
                )
                continue
            }

            await uploadSingleFile(part.file)
        }
    } catch (error) {
        const message = error instanceof Error
            ? error.message
            : 'Failed to split PDF'
        errorMessage.value = message

        addToast(
            `Failed to split ${file.name}: ${message}`,
            'error',
        )
    } finally {
        oversizedFile.value = null
    }
}

const openDocumentModal = (document: FileInfo) => {
    selectedDocument.value = document
    isDocModalOpen.value = true
}

const closeDocumentModal = () => {
    isDocModalOpen.value = false
    selectedDocument.value = null
}

const handleDocumentDeleted = async () => {
    await loadUploadedFiles(props.profileId)
}

watch(
    () => props.profileId,
    (newProfileId) => {
        if (newProfileId) {
            loadUploadedFiles(newProfileId)           
        } else {            
            uploadedFiles.value = []
        }
    },
    { immediate: true }
)
</script>

<style scoped>
.file-upload {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    height: 100%;
}

.uploaded-files {
    background-color: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--size-border-radius);
    padding: 1rem;
    flex: 1;
    overflow-y: auto;
    min-height: 0;
    display: flex;
    flex-direction: column;
}

.uploaded-files-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.75rem;
    flex-shrink: 0;
}

.uploaded-files-header h4 {
    margin: 0;
    font-size: 0.9rem;
    color: var(--color-text-primary);
    font-weight: 600;
}

.refresh-button {
    background: var(--color-surface-hover);
    border: 1px solid var(--color-border);
    border-radius: var(--size-border-radius-sm);
    padding: 0.4rem 0.6rem;
    cursor: pointer;
    color: var(--color-text-secondary);
    transition: all var(--transition-base);
    display: flex;
    align-items: center;
    justify-content: center;
}

.refresh-button:hover:not(:disabled) {
    background: var(--color-surface-active);
    color: var(--color-primary);
    border-color: var(--color-primary);
}

.refresh-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.refresh-button svg.spinning {
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }
    100% {
        transform: rotate(360deg);
    }
}

.uploaded-files ul {
    list-style: none;
    padding: 0;
    margin: 0;
    flex: 1;
    overflow-y: auto;
    min-height: 0;
}

.document-row {
    display: flex;
    align-items: center;
    padding: 0.75rem;
    background-color: var(--color-surface-hover);
    border: 1px solid var(--color-border);
    border-radius: var(--size-border-radius-sm);
    margin-bottom: 0.5rem;
    cursor: pointer;
    transition: all var(--transition-base);
}

.document-row:hover {
    background-color: var(--color-surface-active);
    border-color: var(--color-primary);
    box-shadow: 0 0 0 2px rgba(34, 197, 94, 0.1);
}

.document-row:last-child {
    margin-bottom: 0;
}

.no-documents {
    padding: 1rem;
    text-align: center;
    color: var(--color-text-tertiary);
    font-size: 0.9rem;
    background-color: transparent;
    border: none;
    cursor: default;
}

.no-documents:hover {
    background-color: transparent;
    border-color: transparent;
}

.file-name {
    font-size: 0.9rem;
    color: var(--color-text-primary);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.loading-more {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem;
    color: var(--color-text-tertiary);
    font-size: 0.85rem;
    background-color: transparent;
    border: none;
    cursor: default;
}

.spinner-small {
    border: 2px solid var(--color-border);
    border-top: 2px solid var(--color-primary);
    border-radius: 50%;
    width: 16px;
    height: 16px;
    animation: spin 1s linear infinite;
    flex-shrink: 0;
}

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }
    100% {
        transform: rotate(360deg);
    }
}

.error-message {
    padding: 0.75rem 1rem;
    background-color: var(--color-error-bg);
    border: 1px solid var(--color-error-border);
    border-radius: var(--size-border-radius);
    color: var(--color-error-text);
    font-size: 0.9rem;
}
</style>
