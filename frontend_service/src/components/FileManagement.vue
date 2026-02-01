<template>
    <div class="file-upload">
        <div class="drop-zone" :class="{ 'drag-over': isDragOver, 'uploading': uploading }"
            @dragover.prevent="onDragOver" @dragleave.prevent="onDragLeave" @drop.prevent="onDrop"
            @click="openFileDialog">
            <input ref="fileInput" type="file" accept=".pdf" @change="onFileSelected" hidden />

            <div class="upload-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                    <polyline points="17 8 12 3 7 8" />
                    <line x1="12" y1="3" x2="12" y2="15" />
                </svg>
            </div>

            <p v-if="uploading" class="upload-text">Uploading...</p>
            <p v-else class="upload-text">
                Drag & drop a PDF here<br />
                <span class="upload-subtext">or click to select</span>
            </p>
        </div>

        <div v-if="uploadedFiles.length > 0" class="uploaded-files">
            <h4>Uploaded Documents</h4>
            <ul>
                <li
                    v-for="file in uploadedFiles"
                    :key="file.filename"
                    @click="openDocumentModal(file)"
                    class="document-row"
                >
                    <span class="file-name">{{ file.filename }}</span>
                </li>
            </ul>
        </div>

        <div v-if="errorMessage" class="error-message">
            {{ errorMessage }}
        </div>

        <DocumentModal
            :is-open="isModalOpen"
            :document="selectedDocument"
            :profile-id="profileId"
            @close="closeDocumentModal"
            @document-deleted="handleDocumentDeleted"
        />
    </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { uploadFile, fetchFilesForProfile } from '@/services/fileService'
import DocumentModal from './modals/DocumentModal.vue'
import type FileInfo from '@/model/fileInfo'


interface FileManagementProps {
    profileId: string
}

const props = defineProps<FileManagementProps>()

const emit = defineEmits<{
    (e: 'file-uploaded', filename: string): void
}>()

const fileInput = ref<HTMLInputElement | null>(null)

const isDragOver = ref(false)

const uploadedFiles = ref<FileInfo[]>([])
const uploading = ref(false)

const errorMessage = ref('')

const isModalOpen = ref(false)
const selectedDocument = ref<FileInfo | null>(null)

const loadUploadedFiles = async (profileId: string) => {
    if (!profileId) {
        uploadedFiles.value = []
        return
    }

    try {
        uploadedFiles.value = await fetchFilesForProfile(profileId)
    } catch (error) {
        console.error('Failed to load documents:', error)
        uploadedFiles.value = []
    }
}

const openFileDialog = () => {
    if (!uploading.value && fileInput.value) {
        fileInput.value.click()
    }
}

const onDragOver = () => {
    isDragOver.value = true
}

const onDragLeave = () => {
    isDragOver.value = false
}

const onDrop = (event: DragEvent) => {
    isDragOver.value = false
    const files = event.dataTransfer?.files
    if (files && files.length > 0) {
        handleFile(files[0])
    }
}

const onFileSelected = (event: Event) => {
    const target = event.target as HTMLInputElement
    const files = target.files
    if (files && files.length > 0) {
        handleFile(files[0])
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

    uploading.value = true

    try {
        await uploadFile(props.profileId, file)
        await loadUploadedFiles(props.profileId)
        emit('file-uploaded', file.name)
    } catch (error) {
        errorMessage.value =
            error instanceof Error
                ? error.message
                : 'Failed to upload document'
    } finally {
        uploading.value = false

        if (fileInput.value) {
            fileInput.value.value = ''
        }
    }
}

const openDocumentModal = (document: FileInfo) => {
    selectedDocument.value = document
    isModalOpen.value = true
}

const closeDocumentModal = () => {
    isModalOpen.value = false
    selectedDocument.value = null
}

const handleDocumentDeleted = async (filename: string) => {
    await loadUploadedFiles(props.profileId)
}

watch(
    () => props.profileId,
    (newProfileId) => {
        loadUploadedFiles(newProfileId)
    },
    { immediate: true }
)
</script>

<style scoped>
.file-upload {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.drop-zone {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    border: 2px dashed #cbd5e1;
    border-radius: 8px;
    background-color: #f8fafc;
    cursor: pointer;
    transition: all 0.2s;
}

.drop-zone:hover {
    border-color: #42b983;
    background-color: #f0fdf4;
}

.drop-zone.drag-over {
    border-color: #42b983;
    background-color: #dcfce7;
}

.drop-zone.uploading {
    opacity: 0.7;
    cursor: not-allowed;
}

.upload-icon {
    color: #94a3b8;
    margin-bottom: 0.5rem;
}

.drop-zone:hover .upload-icon,
.drop-zone.drag-over .upload-icon {
    color: #42b983;
}

.upload-text {
    text-align: center;
    color: #64748b;
    margin: 0;
    font-size: 0.95rem;
}

.upload-subtext {
    font-size: 0.85rem;
    color: #94a3b8;
}

.uploaded-files {
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 1rem;
}

.uploaded-files h4 {
    margin: 0 0 0.75rem 0;
    font-size: 0.9rem;
    color: #475569;
}

.uploaded-files ul {
    list-style: none;
    padding: 0;
    margin: 0;
}

.document-row {
    display: flex;
    align-items: center;
    padding: 0.75rem;
    background-color: white;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    margin-bottom: 0.5rem;
    cursor: pointer;
    transition: all 0.2s;
}

.document-row:hover {
    background-color: #f1f5f9;
    border-color: #cbd5e1;
}

.document-row:last-child {
    margin-bottom: 0;
}

.file-name {
    font-size: 0.9rem;
    color: #334155;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.error-message {
    padding: 0.75rem 1rem;
    background-color: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 6px;
    color: #dc2626;
    font-size: 0.9rem;
}
</style>
