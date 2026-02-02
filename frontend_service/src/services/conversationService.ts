import type Conversation from '@/model/conversation'
import type ChatTurn from '@/model/chatTurn'


const MOCK_CONVERSATIONS: Record<string, Conversation[]> = {
    'profile-1': [
        {
            id: 'conv-1',
            profile_id: 'profile-1',
            title: 'Research on AI Ethics',
            created_at: '2026-01-15T10:30:00Z',
            updated_at: '2026-01-15T11:45:00Z',
            chat_turns: [
                {
                    id: 'turn-1',
                    role: 'human',
                    content: 'What are the main ethical concerns in AI development?',
                    timestamp: '2026-01-15T10:30:00Z',
                },
                {
                    id: 'turn-2',
                    role: 'ai',
                    content: {
                        summary: 'Key ethical concerns in AI development include bias, privacy, and transparency.',
                        details: [
                            'Algorithmic bias and fairness',
                            'Data privacy and consent',
                            'Transparency and explainability',
                            'Accountability and responsibility',
                        ],
                    },
                    timestamp: '2026-01-15T10:31:00Z',
                },
            ],
        },
        {
            id: 'conv-2',
            profile_id: 'profile-1',
            title: 'Machine Learning Basics',
            created_at: '2026-01-14T09:00:00Z',
            updated_at: '2026-01-14T10:15:00Z',
            chat_turns: [
                {
                    id: 'turn-3',
                    role: 'human',
                    content: 'Explain supervised vs unsupervised learning',
                    timestamp: '2026-01-14T09:00:00Z',
                },
                {
                    id: 'turn-4',
                    role: 'ai',
                    content: {
                        summary: 'Supervised and unsupervised learning are two main ML paradigms.',
                        supervised: 'Uses labeled data to train models for prediction tasks.',
                        unsupervised: 'Finds patterns in unlabeled data without explicit guidance.',
                    },
                    timestamp: '2026-01-14T09:02:00Z',
                },
            ],
        },
    ],
}


export async function fetchConversationsForProfile(
    profileId: string
): Promise<Conversation[]> {
    await new Promise((resolve) => setTimeout(resolve, 500))

    return MOCK_CONVERSATIONS[profileId] || []
}


export async function fetchConversation(
    conversationId: string
): Promise<Conversation | null> {
    await new Promise((resolve) => setTimeout(resolve, 800))

    for (const conversations of Object.values(MOCK_CONVERSATIONS)) {
        const conversation = conversations.find((c) => c.id === conversationId)
        if (conversation) {
            return conversation
        }
    }

    return null
}


export async function createConversation(
    profileId: string,
    firstMessage: string
): Promise<Conversation> {
    await new Promise((resolve) => setTimeout(resolve, 300))

    const now = new Date().toISOString()
    const conversationId = `conv-${Date.now()}`

    const newConversation: Conversation = {
        id: conversationId,
        profile_id: profileId,
        title: firstMessage.substring(0, 50) + (firstMessage.length > 50 ? '...' : ''),
        created_at: now,
        updated_at: now,
        chat_turns: [],
    }

    if (!MOCK_CONVERSATIONS[profileId]) {
        MOCK_CONVERSATIONS[profileId] = []
    }
    MOCK_CONVERSATIONS[profileId].unshift(newConversation)

    return newConversation
}


export async function addChatTurnToConversation(
    conversationId: string,
    turn: ChatTurn
): Promise<void> {
    await new Promise((resolve) => setTimeout(resolve, 100))

    for (const conversations of Object.values(MOCK_CONVERSATIONS)) {
        const conversation = conversations.find((c) => c.id === conversationId)
        if (conversation) {
            conversation.chat_turns.push(turn)
            conversation.updated_at = new Date().toISOString()
            break
        }
    }
}
