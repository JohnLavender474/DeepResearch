<template>
  <div class="ai-message">
    <MarkdownModal
      :is-open="isModalOpen"
      :title="modalTitle"
      :content="modalContent"
      @close="closeModal"
    />

    <div class="message-header">
      <span class="ai-label">AI Response</span>
      <span 
        class="status-badge"
        :class="statusClass"
      >
        {{ statusLabel }}
      </span>
      <div class="loading-state" v-if="isLoading">
        <div class="spinner"></div>
        <span>Processing...</span>
      </div>
    </div>

    <div class="message-body">
      <CollapsibleSection
        v-if="content.status === 'stopped'"
        title="Execution Stopped"
        :defaultExpanded="true"
      >
        <div class="result-warning">
          <div class="result-header">⚠️ Stopped</div>
          <div class="result-content">
            The graph execution was stopped before completion.
          </div>
        </div>
      </CollapsibleSection>

      <CollapsibleSection
        v-else-if="content.status === 'error'"
        title="Execution Error"
        :defaultExpanded="true"
      >
        <div class="result-error">
          <div class="result-header">❌ Error</div>
          <div class="result-content">
            {{ content.error_message || 'An unknown error occurred' }}
          </div>
        </div>
      </CollapsibleSection>

      <CollapsibleSection
        v-else
        title="Graph Execution"
        :badge="stepCountBadge"
        :defaultExpanded="false"
      >
        <div class="steps-container">
          <div 
            v-if="content.steps.length === 0" 
            class="no-steps"
          >
            <template v-if="isLoading">
              <div class="spinner-small"></div>
              <span>Starting...</span>
            </template>
            <template v-else>
              No steps recorded
            </template>
          </div>

          <template
            v-for="(step, index) in content.steps"
            :key="index"
          >
            <div 
              v-if="isExpandableStep(step.type)"
              class="step-item-expandable"
            >
              <CollapsibleSection
                :title="getStepDisplayText(step)"
                :badge="getStepBadge(step)"
                :defaultExpanded="false"
                :markdownBackground="isSimpleProcessStep(step.type) || isReviewStep(step.type) || isSummaryStep(step.type)"
              >
                <div v-if="isTaskStep(step.type)" class="tasks-container">
                  <div 
                    v-for="(taskEntry, taskIndex) in getTaskEntries(step)"
                    :key="taskIndex"
                    class="task-entry"
                  >
                    <div class="task-header">
                      <span class="task-icon">{{ taskEntry.success ? '✅' : '❌' }}</span>
                      <span class="task-text">{{ taskEntry.task }}</span>
                    </div>
                    
                    <CollapsibleSection
                      v-if="taskEntry.result || (taskEntry.citations && taskEntry.citations.length > 0)"
                      title="Details"
                      :defaultExpanded="false"
                      :markdownBackground="true"
                    >
                      <div v-if="taskEntry.result" class="task-result">
                        <div class="markdown-header">
                          <button
                            class="icon-button"
                            @click="openModal(`Task: ${taskEntry.task}`, taskEntry.result)"
                            title="View in modal"
                          >
                            <Maximize2 :size="16" />
                          </button>
                          <button
                            class="icon-button"
                            @click="copyToClipboard(taskEntry.result, `task-${index}-${taskIndex}`)"
                            :title="copiedStates[`task-${index}-${taskIndex}`] ? 'Copied!' : 'Copy to clipboard'"
                          >
                            <Check v-if="copiedStates[`task-${index}-${taskIndex}`]" :size="16" />
                            <Copy v-else :size="16" />
                          </button>
                        </div>
                        <div class="task-result-content markdown-content" v-html="renderMarkdown(taskEntry.result)"></div>
                      </div>                      
                    </CollapsibleSection>                    
                    <CollapsibleSection
                        v-if="taskEntry.citations && taskEntry.citations.length > 0"
                        title="Citations"
                        :defaultExpanded="false"
                      >
                        <div class="citations-container">
                          <div class="citation-bubbles">
                            <button
                              v-for="(citation, citIndex) in taskEntry.citations"
                              :key="citIndex"
                              class="citation-bubble"
                              :title="citation.filename"
                              @click="openPdfAtPage(step, citation)"
                            >
                              <span class="citation-filename">{{ truncateFilename(citation.filename) }}</span>
                              <span class="citation-page">p.{{ citation.page_number }}</span>
                            </button>
                          </div>
                        </div>
                      </CollapsibleSection>
                  </div>
                </div>

                <div v-else-if="isProcessSelectionStep(step.type)" class="step-content">
                  <div class="content-item">
                    <span class="content-label">Selected Process:</span>
                    <span class="content-value">{{ formatNodeName(step.details?.output?.process_type || 'unknown') }}</span>
                  </div>
                  <div class="content-item">
                    <span class="content-label">Reasoning:</span>
                    <p class="content-text">{{ step.details?.output?.reasoning || 'No reasoning provided' }}</p>
                  </div>
                </div>

                <div v-else-if="isSimpleProcessStep(step.type)" class="step-content">
                  <div class="markdown-header">
                    <button
                      class="icon-button"
                      @click="openModal('Direct Response', step.details?.output?.result || '')"
                      title="View in modal"
                    >
                      <Maximize2 :size="16" />
                    </button>
                    <button
                      class="icon-button"
                      @click="copyToClipboard(step.details?.output?.result || '', `simple-process-${index}`)"
                      :title="copiedStates[`simple-process-${index}`] ? 'Copied!' : 'Copy to clipboard'"
                    >
                      <Check v-if="copiedStates[`simple-process-${index}`]" :size="16" />
                      <Copy v-else :size="16" />
                    </button>
                  </div>
                  <div class="markdown-content" v-html="renderMarkdown(step.details?.output?.result || '')"></div>
                </div>

                <div v-else-if="isReviewStep(step.type)" class="step-content">
                  <div class="markdown-header">
                    <button
                      class="icon-button"
                      @click="openModal('Research Review', step.details?.output?.review || '')"
                      title="View in modal"
                    >
                      <Maximize2 :size="16" />
                    </button>
                    <button
                      class="icon-button"
                      @click="copyToClipboard(step.details?.output?.review || '', `review-${index}`)"
                      :title="copiedStates[`review-${index}`] ? 'Copied!' : 'Copy to clipboard'"
                    >
                      <Check v-if="copiedStates[`review-${index}`]" :size="16" />
                      <Copy v-else :size="16" />
                    </button>
                  </div>
                  <div class="markdown-content" v-html="renderMarkdown(step.details?.output?.review || '')"></div>
                </div>

                <div v-else-if="isSummaryStep(step.type)" class="step-content">
                  <div class="markdown-header">
                    <button
                      class="icon-button"
                      @click="openModal('Final Summary', content.final_result || '')"
                      title="View in modal"
                    >
                      <Maximize2 :size="16" />
                    </button>
                    <button
                      class="icon-button"
                      @click="copyToClipboard(content.final_result || '', 'final-summary')"
                      :title="copiedStates['final-summary'] ? 'Copied!' : 'Copy to clipboard'"
                    >
                      <Check v-if="copiedStates['final-summary']" :size="16" />
                      <Copy v-else :size="16" />
                    </button>
                  </div>
                  <div class="markdown-content summary-content" v-html="renderMarkdown(content.final_result || '')"></div>
                </div>
              </CollapsibleSection>
            </div>

            <div 
              v-else
              class="step-item"
            >
              <span class="step-icon">{{ getStepIcon(step.type) }}</span>
              <span class="step-text">{{ getStepDisplayText(step) }}</span>
            </div>
          </template>
        </div>
      </CollapsibleSection>      
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { marked } from 'marked'
import { Copy, Check, Maximize2 } from 'lucide-vue-next'

import CollapsibleSection from './CollapsibleSection.vue'
import MarkdownModal from '../modals/MarkdownModal.vue'
import type AIMessageContent from '@/model/aiMessageContent'
import type GraphStep from '@/model/graphStep'
import type TaskEntry from '@/model/taskEntry'
import type TaskCitation from '@/model/taskCitation'


interface AIChatMessageProps {
  content: AIMessageContent
  timestamp: Date
}

const props = defineProps<AIChatMessageProps>()

const copiedStates = ref<Record<string, boolean>>({})
const isModalOpen = ref(false)
const modalTitle = ref('')
const modalContent = ref('')

const openModal = (title: string, content: string) => {
  modalTitle.value = title
  modalContent.value = content
  isModalOpen.value = true
}

const closeModal = () => {
  isModalOpen.value = false
}

const copyToClipboard = async (text: string, key: string) => {
  try {
    await navigator.clipboard.writeText(text)
    copiedStates.value[key] = true
    setTimeout(() => {
      copiedStates.value[key] = false
    }, 2000)
  } catch (err) {
    console.error('Failed to copy text:', err)
  }
}

const formatTime = (date: Date): string => {
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
  })
}

const isLoading = computed(() => {
  return props.content.status === 'running'
})

const statusClass = computed(() => {
  return {
    'status-running': props.content.status === 'running',
    'status-completed': props.content.status === 'completed',
    'status-stopped': props.content.status === 'stopped',
    'status-error': props.content.status === 'error',
  }
})

const statusLabel = computed(() => {
  const labels: Record<string, string> = {
    running: 'Running',
    completed: 'Completed',
    stopped: 'Stopped',
    error: 'Error',
  }
  return labels[props.content.status] || 'Unknown'
})

const stepCountBadge = computed(() => {
  const count = props.content.steps.length
  return count === 1 ? '1 step' : `${count} steps`
})

const formatNodeName = (nodeName: string): string => {
  return nodeName
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

const isTaskStep = (stepType: string): boolean => {
  return stepType === 'parallel_tasks' || stepType === 'sequential_tasks'
}

const isProcessSelectionStep = (stepType: string): boolean => {
  return stepType === 'process_selection'
}

const isSimpleProcessStep = (stepType: string): boolean => {
  return stepType === 'simple_process'
}

const isReviewStep = (stepType: string): boolean => {
  return stepType === 'perform_review'
}

const isSummaryStep = (stepType: string): boolean => {
  return stepType === 'generate_summary'
}

const isExpandableStep = (stepType: string): boolean => {
  return isTaskStep(stepType) || 
    isProcessSelectionStep(stepType) || 
    isReviewStep(stepType) || 
    isSummaryStep(stepType) || 
    isSimpleProcessStep(stepType)
}

const getTaskEntries = (step: GraphStep): TaskEntry[] => {
  return step.details?.output?.task_entries || []
}

const getTaskCountBadge = (step: GraphStep): string => {
  const count = getTaskEntries(step).length
  return count === 1 ? '1 task' : `${count} tasks`
}

const getStepBadge = (step: GraphStep): string | undefined => {
  if (isTaskStep(step.type)) {
    return getTaskCountBadge(step)
  }
  return undefined
}

const truncateFilename = (filename: string, maxLength: number = 15): string => {
  if (filename.length <= maxLength) {
    return filename
  }
  
  const extension = filename.includes('.') 
    ? filename.slice(filename.lastIndexOf('.')) 
    : ''
  const nameWithoutExt = filename.slice(0, filename.length - extension.length)
  const truncatedName = nameWithoutExt.slice(0, maxLength - extension.length - 3)
  
  return `${truncatedName}...${extension}`
}

const openPdfAtPage = (step: GraphStep, citation: TaskCitation): void => {
  const profileId = step.details?.input?.collection_name || citation.collection_name
  const filename = citation.filename
  const pageNumber = citation.page_number
  
  const url = `/api/storage/collections/${profileId}/blobs/${encodeURIComponent(filename)}#page=${pageNumber}`
  window.open(url, '_blank')
}

const getStepIcon = (stepType: string): string => {
  if (stepType === 'process_selection') {
    return '🎯'
  }

  if (stepType === 'simple_process') {
    return '💬'
  }

  if (stepType === 'parallel_tasks') {
    return '⚡'
  }

  if (stepType === 'sequential_tasks') {
    return '📋'
  }

  if (stepType === 'perform_review') {
    return '🔍'
  }

  if (stepType === 'generate_summary') {
    return '📝'
  }

  return '✓'
}

const getStepDisplayText = (step: GraphStep): string => {
  const stepType = step.type

  if (stepType === 'process_selection') {
    return 'Selected method for answering the query'
  }

  if (stepType === 'simple_process') {
    return 'Generated direct response'
  }

  if (stepType === 'parallel_tasks') {
    const taskCount = step.details?.output?.task_entries?.length || 0
    return `Executed ${taskCount} research tasks in parallel`
  }

  if (stepType === 'sequential_tasks') {
    const taskCount = step.details?.output?.task_entries?.length || 0
    return `Executed ${taskCount} research tasks in sequence`
  }

  if (stepType === 'perform_review') {
    return 'Reviewed research results'
  }

  if (stepType === 'generate_summary') {
    return 'Generated final summary'
  }

  return `Completed: ${formatNodeName(stepType)}`
}

const renderMarkdown = (markdown: string) => {
  return marked(markdown)
}
</script>

<style scoped>
.ai-message {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.75rem;
  max-width: 90%;
}

.message-header {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  font-size: 0.85rem;
}

.ai-label {
  font-weight: 600;
  color: var(--color-text-primary);
}

.message-timestamp {
  color: var(--color-text-tertiary);
}

.status-badge {
  padding: 0.125rem 0.5rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-running {
  background-color: var(--color-info-bg);
  color: var(--color-info-text);
}

.status-completed {
  background-color: var(--color-success-bg);
  color: var(--color-success-text);
}

.status-stopped {
  background-color: var(--color-warning-bg);
  color: var(--color-warning-text);
}

.status-error {
  background-color: var(--color-error-bg);
  color: var(--color-error-text);
}

.message-body {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.steps-container {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.no-steps {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--color-text-tertiary);
  font-size: 0.9rem;
  font-style: italic;
}

.spinner-small {
  border: 2px solid var(--color-border);
  border-top: 2px solid var(--color-primary);
  border-radius: 50%;
  width: 14px;
  height: 14px;
  animation: spin 1s linear infinite;
  flex-shrink: 0;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--color-border);
  font-size: 0.9rem;
  color: var(--color-text-secondary);
}

.step-item:last-child {
  border-bottom: none;
}

.step-item-expandable {
  border-bottom: 1px solid var(--color-border);
}

.step-item-expandable:last-child {
  border-bottom: none;
}

.step-icon {
  flex-shrink: 0;
  width: 1.5rem;
  text-align: center;
}

.step-text {
  flex: 1;
}

.tasks-container {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.step-content {
  padding: 0.5rem;
}

.content-item {
  margin-bottom: 0.75rem;
}

.content-label {
  font-weight: 600;
  color: var(--color-text-primary);
  font-size: 0.875rem;
  display: block;
  margin-bottom: 0.25rem;
}

.content-value {
  color: var(--color-text-secondary);
  font-size: 0.875rem;
  font-weight: 500;
}

.content-text {
  color: var(--color-text-secondary);
  font-size: 0.875rem;
  line-height: 1.5;
  margin: 0;
  white-space: pre-wrap;
}



.summary-content {
  max-height: 400px;
  overflow-y: auto;
}

.task-entry {
  padding: 0.75rem;
  background-color: var(--color-bg-3);
  border-radius: var(--size-border-radius-sm);
  border: 1px solid var(--color-border);
}

.task-header {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.task-icon {
  flex-shrink: 0;
  font-size: 0.9rem;
}

.task-text {
  font-size: 0.875rem;
  color: var(--color-text-primary);
  line-height: 1.4;
}

.task-result {
  margin-bottom: 0.75rem;
  position: relative;
}

.markdown-header {
  display: flex;
  justify-content: flex-end;
  gap: 0.25rem;
  margin-bottom: 0.5rem;
}

.icon-button {
  background: var(--color-surface-hover);
  border: 1px solid var(--color-border);
  border-radius: var(--size-border-radius-sm);
  padding: 0.25rem 0.5rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  color: var(--color-text-secondary);
  transition: all var(--transition-base);
}

.icon-button:hover {
  background: var(--color-surface-active);
  color: var(--color-text-primary);
  border-color: var(--color-border-light);
}

.icon-button:active {
  transform: scale(0.95);
}

.task-result-content {
  font-size: 0.875rem;
  line-height: 1.6;
  color: black;
}

.citations-container {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.citation-bubbles {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
}

.citation-bubble {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  background-color: var(--color-info-bg);
  border: 1px solid var(--color-info-border);
  border-radius: 9999px;
  font-size: 0.75rem;
  color: var(--color-info-text);
  cursor: pointer;
  transition: all var(--transition-base);
}

.citation-bubble:hover {
  background-color: var(--color-info-bg);
  border-color: var(--color-info-border);
}

.citation-filename {
  font-weight: 500;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.citation-page {
  color: var(--color-info-text);
  font-weight: 600;
}

.loading-state {
  display: flex;
  align-items: center;
  gap: 0.75rem;
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
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.result-completed {
  border-left: 3px solid var(--color-primary);
  padding-left: 1rem;
}

.result-warning {
  border-left: 3px solid var(--color-status-warning);
  padding-left: 1rem;
}

.result-error {
  border-left: 3px solid var(--color-status-error);
  padding-left: 1rem;
}

.result-header {
  font-weight: 600;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
  color: var(--color-text-primary);
}

.result-content {
  font-size: 0.95rem;
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.result-content-scrollable {
  font-size: 0.95rem;
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 400px;
  overflow-y: auto;
}
</style>
