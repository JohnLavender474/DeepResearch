const SELECTED_PROFILE_KEY = 'deepresearch_selected_profile'
const PROFILE_CONVERSATIONS_KEY = 'deepresearch_profile_conversations'


export function useLocalStorage() {
  const getSelectedProfile = (): string | null => {
    return localStorage.getItem(SELECTED_PROFILE_KEY)
  }

  const setSelectedProfile = (profileId: string): void => {
    localStorage.setItem(SELECTED_PROFILE_KEY, profileId)
  }

  const getProfileConversations = (): Record<string, string> => {
    const stored = localStorage.getItem(PROFILE_CONVERSATIONS_KEY)
    if (!stored) {
      return {}
    }
    try {
      return JSON.parse(stored)
    } catch {
      return {}
    }
  }

  const getConversationForProfile = (profileId: string): string | null => {
    const conversations = getProfileConversations()
    return conversations[profileId] ?? null
  }

  const setConversationForProfile = (
    profileId: string,
    conversationId: string
  ): void => {
    const conversations = getProfileConversations()
    conversations[profileId] = conversationId
    localStorage.setItem(
      PROFILE_CONVERSATIONS_KEY,
      JSON.stringify(conversations)
    )
  }

  const clearConversationForProfile = (profileId: string): void => {
    const conversations = getProfileConversations()
    delete conversations[profileId]
    localStorage.setItem(
      PROFILE_CONVERSATIONS_KEY,
      JSON.stringify(conversations)
    )
  }

  return {
    getSelectedProfile,
    setSelectedProfile,
    getConversationForProfile,
    setConversationForProfile,
    clearConversationForProfile,
  }
}
