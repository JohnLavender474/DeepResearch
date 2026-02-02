import type { ChatTurnRole } from './chatTurnRole'


export default interface ChatTurn {
    id: string
    role: ChatTurnRole
    content: string | Record<string, any>
    timestamp: string
}
