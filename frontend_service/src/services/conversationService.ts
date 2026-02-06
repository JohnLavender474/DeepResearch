import type Conversation from '@/model/conversation'


const API_BASE_URL = '/api/database'


export async function fetchConversationsForProfile(
    profileId: string
): Promise<Conversation[]> {
    if (!profileId) {
        throw new Error('No profile selected');
    }

    const response = await fetch(
        `${API_BASE_URL}/${profileId}/conversations`
    )

    if (!response.ok) {
        throw new Error(
            `Failed to fetch conversations: ${response.statusText}`
        )
    }

    return response.json()
}


export async function fetchConversation(
    conversationId: string,
    profileId: string
): Promise<Conversation | null> {
    if (!profileId) {
        throw new Error('No profile selected');
    }

    const response = await fetch(
        `${API_BASE_URL}/${profileId}/conversations/${conversationId}/with-turns`
    )

    if (response.status === 404) {
        return null
    }

    if (!response.ok) {
        throw new Error(
            `Failed to fetch conversation: ${response.statusText}`
        )
    }

    return response.json()
}


export async function createConversation(
    profileId: string,
    title: string
): Promise<Conversation> {
    if (!profileId) {
        throw new Error('No profile selected');
    }

    const response = await fetch(
        `${API_BASE_URL}/${profileId}/conversations`,
        {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                profile_id: profileId,
                title,
                chat_turns: [],
            }),
        }
    )

    if (!response.ok) {
        throw new Error(
            `Failed to create conversation: ${response.statusText}`
        )
    }

    return response.json()
}
