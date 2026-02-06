<template>
    <div v-if="isOpen" class="modal-backdrop" @click.self="handleCancel">
        <div class="modal split-modal">
            <div class="modal-header">
                <h2>File Too Large</h2>
                <button
                    class="modal-close"
                    type="button"
                    @click="handleCancel"
                >
                    ×
                </button>
            </div>

            <div class="modal-body">
                <div class="file-info">
                    <p class="info-text">
                        <strong>{{ filename }}</strong> is
                        <strong>{{ formattedSize }}</strong>,
                        which exceeds the
                        <strong>{{ maxSizeMb }}MB</strong> upload limit.
                    </p>
                </div>

                <div v-if="loading" class="loading-section">
                    <div class="spinner"></div>
                    <span>Analyzing PDF...</span>
                </div>

                <div v-else-if="pageCount > 0" class="split-options">
                    <p class="info-text">
                        This PDF has <strong>{{ pageCount }}</strong> pages.
                        It can be split into smaller parts for upload.
                    </p>

                    <label class="option-label">Pages per part</label>
                    <div class="pages-input-row">
                        <input
                            v-model.number="pagesPerPart"
                            type="number"
                            min="1"
                            :max="pageCount"
                            class="pages-input"
                        />
                        <span class="part-count-hint">
                            → {{ estimatedParts }} part(s)
                        </span>
                    </div>

                    <p v-if="validationError" class="error-text">
                        {{ validationError }}
                    </p>
                </div>

                <div v-else class="error-section">
                    <p class="error-text">
                        Unable to analyze this PDF.
                        Please try a smaller file.
                    </p>
                </div>

                <div class="modal-actions">
                    <button
                        class="secondary-button"
                        type="button"
                        @click="handleCancel"
                    >
                        Cancel
                    </button>
                    <button
                        class="primary-button"
                        type="button"
                        :disabled="!canSplit"
                        @click="handleSplit"
                    >
                        Split & Upload
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

import {
    getPageCount,
    getMaxFileSizeMb,
    formatFileSize,
} from '@/services/pdfSplitService'


interface FileSplitModalProps {
    isOpen: boolean
    file: File | null
}

const props = defineProps<FileSplitModalProps>()

const emit = defineEmits<{
    (e: 'cancel'): void
    (e: 'split', pagesPerPart: number): void
}>()

const loading = ref(false)
const pageCount = ref(0)
const pagesPerPart = ref(20)

const maxSizeMb = getMaxFileSizeMb()

const filename = computed(() => props.file?.name ?? '')

const formattedSize = computed(() =>
    props.file ? formatFileSize(props.file.size) : ''
)

const estimatedParts = computed(() => {
    if (pageCount.value <= 0 || pagesPerPart.value <= 0) {
        return 0
    }
    return Math.ceil(pageCount.value / pagesPerPart.value)
})

const validationError = computed(() => {
    if (pagesPerPart.value < 1) {
        return 'Pages per part must be at least 1'
    }
    if (pagesPerPart.value > pageCount.value) {
        return `Cannot exceed total page count (${pageCount.value})`
    }
    return ''
})

const canSplit = computed(() => {
    return (
        !loading.value &&
        pageCount.value > 0 &&
        pagesPerPart.value >= 1 &&
        pagesPerPart.value <= pageCount.value &&
        !validationError.value
    )
})

const handleCancel = () => {
    emit('cancel')
}

const handleSplit = () => {
    if (!canSplit.value) {
        return
    }
    emit('split', pagesPerPart.value)
}

const analyzeFile = async (file: File) => {
    loading.value = true
    
    pageCount.value = 0
    pagesPerPart.value = 20

    try {
        pageCount.value = await getPageCount(file)

        if (pagesPerPart.value > pageCount.value) {
            pagesPerPart.value = Math.max(
                1,
                Math.ceil(pageCount.value / 2)
            )
        }
    } catch (error) {
        console.error('Failed to analyze PDF:', error)
        pageCount.value = 0
    } finally {
        loading.value = false
    }
}

watch(
    () => props.isOpen,
    (newValue) => {
        if (newValue && props.file) {
            analyzeFile(props.file)
        }
    }
)
</script>

<style scoped>
.modal-backdrop {
    position: fixed;
    inset: 0;
    background-color: rgba(15, 23, 42, 0.45);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 50;
}

.split-modal {
    background-color: var(--color-bg-2);
    border-radius: var(--size-border-radius-lg);
    width: min(480px, 90vw);
    box-shadow: 0 20px 40px rgba(15, 23, 42, 0.2);
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding: 1.5rem;
}

.modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.modal-header h2 {
    margin: 0;
    font-size: 1.1rem;
    color: var(--color-text-primary);
}

.modal-close {
    background: none;
    border: none;
    font-size: 1.4rem;
    cursor: pointer;
    color: var(--color-text-secondary);
}

.modal-body {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.file-info {
    padding: 0.75rem 1rem;
    background-color: var(--color-surface-hover);
    border: 1px solid var(--color-border);
    border-radius: var(--size-border-radius);
}

.info-text {
    margin: 0;
    font-size: 0.9rem;
    color: var(--color-text-secondary);
    line-height: 1.5;
}

.info-text strong {
    color: var(--color-text-primary);
}

.loading-section {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem;
    color: var(--color-text-secondary);
    font-size: 0.9rem;
}

.spinner {
    border: 2px solid var(--color-border);
    border-top: 2px solid var(--color-primary);
    border-radius: 50%;
    width: 20px;
    height: 20px;
    animation: spin 1s linear infinite;
    flex-shrink: 0;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.split-options {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.option-label {
    font-weight: 600;
    font-size: 0.9rem;
    color: var(--color-text-primary);
}

.pages-input-row {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.pages-input {
    width: 80px;
    padding: 0.5rem 0.75rem;
    border-radius: var(--size-border-radius);
    border: 1px solid var(--color-border);
    font-size: 0.9rem;
    background-color: var(--color-bg-3);
    color: var(--color-text-primary);
    transition: border-color var(--transition-base);
}

.pages-input:focus {
    outline: none;
    border-color: var(--color-primary);
}

.part-count-hint {
    font-size: 0.85rem;
    color: var(--color-text-tertiary);
}

.error-section {
    padding: 0.75rem 1rem;
}

.error-text {
    margin: 0;
    color: var(--color-error-text);
    font-size: 0.85rem;
}

.modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 0.75rem;
    margin-top: 0.5rem;
}

.primary-button,
.secondary-button {
    padding: 0.5rem 1rem;
    border-radius: var(--size-border-radius);
    font-size: 0.85rem;
    cursor: pointer;
    border: 1px solid transparent;
    transition: background-color var(--transition-base);
}

.primary-button {
    background-color: var(--color-primary);
    color: white;
}

.primary-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.secondary-button {
    background-color: var(--color-surface-hover);
    color: var(--color-text-primary);
    border-color: var(--color-border);
}

.secondary-button:hover {
    background-color: var(--color-surface-active);
}
</style>
