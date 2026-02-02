export interface SimpleMessage {
  role: string
  content: string
}


export interface GraphInput {
  user_query: string
  profile_id: string
  messages?: SimpleMessage[]
  custom_start_node?: string
}


export async function* streamGraphExecution(
  input: GraphInput
): AsyncGenerator<string, void, unknown> {
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
