<template>
    <div
        class="drop-zone"
        :class="{ 'drag-over': isDragOver }"
        @click="openFileDialog"
    >
        <input
            ref="fileInput"
            type="file"
            accept=".pdf"
            multiple
            @change="onFilesSelected"
            hidden
        />

        <div class="upload-icon">
            <svg
                xmlns="http://www.w3.org/2000/svg"
                width="48"
                height="48"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
            >
                <path
                    d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"
                />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
            </svg>
        </div>

        <p class="upload-text">
            <span class="upload-subtext">
                Click to select one or more files for upload
            </span>
        </p>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'


const emit = defineEmits<{
    (e: 'files-selected', files: File[]): void
}>()

const fileInput = ref<HTMLInputElement | null>(null)

const isDragOver = ref(false)

const openFileDialog = () => {
    if (fileInput.value) {
        fileInput.value.click()
    }
}

const onFilesSelected = (event: Event) => {
    const target = event.target as HTMLInputElement
    const files = target.files
    if (files && files.length > 0) {
        emit('files-selected', Array.from(files))
    }

    if (fileInput.value) {
        fileInput.value.value = ''
    }
}
</script>

<style scoped>
.drop-zone {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    border: 2px dashed var(--color-border);
    border-radius: var(--size-border-radius);
    background-color: var(--color-bg-2);
    cursor: pointer;
    transition: all var(--transition-base);
    flex-shrink: 0;
}

.drop-zone:hover {
    border-color: var(--color-primary);
    background-color: var(--color-bg-3);
}

.drop-zone.drag-over {
    border-color: var(--color-primary);
    background-color: var(--color-surface-hover);
}

.upload-icon {
    color: var(--color-text-tertiary);
    margin-bottom: 0.5rem;
}

.drop-zone:hover .upload-icon,
.drop-zone.drag-over .upload-icon {
    color: var(--color-primary);
}

.upload-text {
    text-align: center;
    color: var(--color-text-secondary);
    margin: 0;
    font-size: 0.95rem;
}

.upload-subtext {
    font-size: 0.85rem;
    color: var(--color-text-tertiary);
}
</style>
