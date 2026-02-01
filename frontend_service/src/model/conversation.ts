export default interface Conversation {
    id: string
    title: string | null
    created_at: string
    updated_at: string
    chat_turns: string[]
}