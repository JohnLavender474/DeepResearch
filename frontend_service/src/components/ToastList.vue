<template>
    <div class="toast-container">
        <div
            v-for="toast in props.toasts"
            :key="toast.id"
            class="toast"
            :class="toast.type"
        >
            {{ toast.message }}
        </div>
    </div>
</template>

<script setup lang="ts">
import type Toast from '@/model/toast'


interface ToastListProps {
    toasts: Toast[]
}

const props = defineProps<ToastListProps>()
</script>

<style scoped>
.toast-container {
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    z-index: 9999;
    max-width: 400px;
}

.toast {
    padding: 0.75rem 1rem;
    border-radius: var(--size-border-radius);
    font-size: 0.85rem;
    font-weight: 500;
    border: 1px solid transparent;
    box-shadow: var(--shadow-toast);
    animation: slideIn 0.3s ease-out;
    backdrop-filter: blur(8px);
}

@keyframes slideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

.toast.info {
    background-color: var(--color-info-bg);
    border-color: var(--color-info-border);
    color: var(--color-info-text);
}

.toast.success {
    background-color: var(--color-success-bg);
    border-color: var(--color-success-border);
    color: var(--color-success-text);
}

.toast.error {
    background-color: var(--color-error-bg);
    border-color: var(--color-error-border);
    color: var(--color-error-text);
}
</style>
