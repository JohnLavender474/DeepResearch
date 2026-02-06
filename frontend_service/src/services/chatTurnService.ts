import type ChatTurn from '@/model/chatTurn'


const API_BASE_URL = '/api/database'


export async function createChatTurn(
  profileId: string,
  conversationId: string,
  role: string,
  data: Record<string, any>,
  timestamp: string
): Promise<ChatTurn> {
  if (!profileId) {
    throw new Error('No profile selected');
  }

  const response = await fetch(
    `${API_BASE_URL}/${profileId}/conversations/${conversationId}/chat-turns`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        role,
        data,
        timestamp,
      }),
    }
  )

  if (!response.ok) {
    throw new Error(`Failed to create chat turn: ${response.statusText}`)
  }

  return response.json()
}


export async function updateChatTurn(
  profileId: string,
  chatTurnId: string,
  data: Record<string, any>
): Promise<ChatTurn> {
  if (!profileId) {
    throw new Error('No profile selected');
  }

  const response = await fetch(
    `${API_BASE_URL}/${profileId}/chat-turns/${chatTurnId}`,
    {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    }
  )

  if (!response.ok) {
    throw new Error(`Failed to update chat turn: ${response.statusText}`)
  }

  return response.json()
}


export async function fetchChatTurnsByConversation(
  profileId: string,
  conversationId: string
): Promise<ChatTurn[]> {
  const response = await fetch(
    `${API_BASE_URL}/${profileId}/conversations/${conversationId}/chat-turns`
  )

  if (!response.ok) {
    throw new Error(`Failed to fetch chat turns: ${response.statusText}`)
  }

  return response.json()
}
