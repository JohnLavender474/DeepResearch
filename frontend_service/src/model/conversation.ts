import type ChatTurn from './chatTurn'


export default interface Conversation {
    id: string
    profile_id: string
    title: string | null
    created_at: string
    updated_at: string
    chat_turns: ChatTurn[]
}