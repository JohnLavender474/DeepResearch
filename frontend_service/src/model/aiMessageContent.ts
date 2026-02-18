import type GraphStep from './graphStep'


export type InvocationStatus = 
  | 'running' 
  | 'completed' 
  | 'stopped' 
  | 'error'


export default interface AIMessageContent {
  invocation_id?: string
  status: InvocationStatus
  steps: GraphStep[]
  final_result?: string
  error_message?: string
  latestBlurb?: string
}
