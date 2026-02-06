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


export async function* streamGraphExecution(
  input: GraphInput
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
