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
                <li v-for="file in uploadedFiles" :key="file.name">
                    <span class="file-name">{{ file.name }}</span>
                    <button class="delete-btn" @click="deleteFile(file.name)">×</button>
                </li>
            </ul>
        </div>

        <div v-if="errorMessage" class="error-message">
            {{ errorMessage }}
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'


interface UploadedFile {
    name: string
    uploadedAt: Date
}

const props = defineProps<{
    profileId: string
}>()

const emit = defineEmits<{
    (e: 'file-uploaded', filename: string): void
    (e: 'file-deleted', filename: string): void
}>()

const fileInput = ref<HTMLInputElement | null>(null)
const isDragOver = ref(false)
const uploading = ref(false)
const uploadedFiles = ref<UploadedFile[]>([])
const errorMessage = ref('')

const loadUploadedFiles = async (profileId: string) => {
    if (!profileId) {
        uploadedFiles.value = []
        return
    }

    await new Promise((resolve) => setTimeout(resolve, 200))
    uploadedFiles.value = [
        { name: 'research-paper.pdf', uploadedAt: new Date('2026-01-30') },
        { name: 'quarterly-report.pdf', uploadedAt: new Date('2026-01-29') },
    ]
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

    const existingFile = uploadedFiles.value.find((f) => f.name === file.name)
    if (existingFile) {
        errorMessage.value = 'A file with this name already exists'
        return
    }

    uploading.value = true

    await new Promise((resolve) => setTimeout(resolve, 1000))
    uploadedFiles.value.push({
        name: file.name,
        uploadedAt: new Date(),
    })

    uploading.value = false
    emit('file-uploaded', file.name)

    if (fileInput.value) {
        fileInput.value.value = ''
    }
}

const deleteFile = async (filename: string) => {
    await new Promise((resolve) => setTimeout(resolve, 300))
    uploadedFiles.value = uploadedFiles.value.filter((f) => f.name !== filename)
    emit('file-deleted', filename)
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

.uploaded-files li {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.5rem 0.75rem;
    background-color: white;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    margin-bottom: 0.5rem;
}

.uploaded-files li:last-child {
    margin-bottom: 0;
}

.file-name {
    font-size: 0.9rem;
    color: #334155;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.delete-btn {
    background: none;
    border: none;
    color: #ef4444;
    font-size: 1.25rem;
    cursor: pointer;
    padding: 0 0.25rem;
    line-height: 1;
}

.delete-btn:hover {
    color: #dc2626;
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
