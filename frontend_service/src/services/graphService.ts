export interface SimpleMessage {
  role: string
  content: string
}


export interface GraphInput {
  user_query: string
  profile_id: string
  messages?: SimpleMessage[]
  custom_start_node?: string
  process_override?: string
  execution_config?: {
    process_override?: string
    model_selection?: string
    allow_general_knowledge_fallback?: boolean    
    temperature?: number
    reasoning_level?: string
  }
}


export async function fetchProcessTypes(): Promise<string[]> {
  const response = await fetch('/api/graph/process-types')

  if (!response.ok) {
    throw new Error(
      `Failed to fetch process types: ${response.statusText}`
    )
  }

  return response.json()
}


export async function fetchModels(): Promise<string[]> {
  const response = await fetch('/api/graph/models')

  if (!response.ok) {
    throw new Error(
      `Failed to fetch models: ${response.statusText}`
    )
  }

  return response.json()
}


export async function stopInvocation(
  invocationId: string,
): Promise<void> {
  const response = await fetch(
    `/api/graph/${invocationId}/stop`,
    { method: 'POST' },
  )

  if (!response.ok) {
    throw new Error(
      `Failed to stop invocation: ${response.statusText}`
    )
  }
}


export async function* streamGraphExecution(
  input: GraphInput,
  signal?: AbortSignal,
): AsyncGenerator<string, void, unknown> {
  if (!input.profile_id) {
    throw new Error('No profile selected');
  }

  const response = await fetch('/api/graph/execute', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(input),
    signal,
  })

  if (!response.ok) {
    throw new Error(`Graph execution failed: ${response.status} ${response.statusText}`)
  }

  const reader = response.body?.getReader()
  if (!reader) {
    throw new Error('Response body is not readable')
  }

  const decoder = new TextDecoder()

  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) {
        break
      }

      const chunk = decoder.decode(value, { stream: true })
      yield chunk
    }
  } finally {
    reader.releaseLock()
  }
}
